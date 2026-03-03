"""
SSH Execution Module

Handles remote command execution via SSH with integrated security validation,
error handling, and comprehensive logging.
"""

import os
import subprocess
import paramiko
import streamlit as st
from app.core.validators import validate_bash_command, get_validation_summary
from app.core.logger import ssh_logger, app_logger


def _get_vm_ip():
    """
    Retrieve VM IP address.
    
    Priority:
    1. VM_IP from session state (set during app initialization)
    2. VM_IP from environment variable
    3. Dynamically resolve via Compute API
    
    Returns:
        str: IP address or None if not available
    """
    import streamlit as st
    
    # Check Streamlit session state first
    if 'vm_ip' in st.session_state and st.session_state.vm_ip and st.session_state.vm_ip != "127.0.0.1":
        return st.session_state.vm_ip
    
    # Check environment variable
    vm_ip = os.getenv("VM_IP")
    if vm_ip and vm_ip != "127.0.0.1":
        return vm_ip
    
    # Try to resolve dynamically (fallback)
    try:
        from app.config import GCP_INSTANCE_NAME, GCP_INSTANCE_ZONE
        from app.core.gcp_helpers import get_instance_ip
        import google.auth
        
        creds, _ = google.auth.default()
        ip = get_instance_ip(GCP_INSTANCE_NAME, GCP_INSTANCE_ZONE, creds, ip_type='external')
        if ip:
            # Cache in session state
            st.session_state.vm_ip = ip
            return ip
    except Exception as e:
        app_logger.log_info(f"Dynamic IP resolution failed: {e}")
    
    return None


def execute_ssh(command, credentials, oslogin_service, exec_timeout=120, block_unsafe=False):
    """
    Execute SSH command with integrated security validation.
    
    Process:
    1. Validate bash command for security
    2. Generate/retrieve SSH key and username
    3. Connect to VM via SSH
    4. Execute command and capture output
    5. Log execution with full context
    
    Args:
        command: Bash command to execute
        credentials: Google Cloud credentials
        oslogin_service: OS Login service client
        exec_timeout: Command execution timeout in seconds (default: 120)
        block_unsafe: If True, blocks unsafe commands (default: False)
        
    Returns:
        str: Command output or error message
    """
    from app.core.auth import get_ssh_key
    
    # --- VALIDATION PHASE ---
    is_safe, validation_report = validate_bash_command(command)
    validation_summary = get_validation_summary(is_safe, validation_report)
    
    if not is_safe and block_unsafe:
        ssh_logger.log_blocked_command(command, validation_report)
        return f"❌ EXECUTION BLOCKED - Security validation failed:\n{validation_report}"
    
    # --- GET VM IP & RESOLVE SSH CREDENTIALS ---
    vm_ip = _get_vm_ip()
    if not vm_ip:
        err_msg = "VM_IP not configured or could not be resolved"
        ssh_logger.log_ssh_error(command, err_msg, validation_summary)
        return f"❌ SSH error: {err_msg}"
    
    key, username = get_ssh_key(credentials, oslogin_service)
    if not key or not username:
        err_msg = "Failed to prepare SSH credentials (key generation/OS Login failed)"
        ssh_logger.log_ssh_error(command, err_msg, validation_summary)
        return f"❌ SSH error: {err_msg}"
    
    # --- EXECUTION PHASE ---
    try:
        app_logger.log_info(f"execute_ssh: connecting to {vm_ip}:{22} as user '{username}' (timeout={exec_timeout}s)")
        print(f"[SSH DEBUG] Connecting to {vm_ip}:22")
        print(f"[SSH DEBUG] Username: {username}")
        print(f"[SSH DEBUG] Key type: {key.get_name() if key else 'None'}")
        
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        # Connect with detailed error handling
        try:
            print(f"[SSH DEBUG] Starting SSH connection attempt...")
            ssh.connect(
                hostname=vm_ip,
                username=username,
                pkey=key,
                timeout=60,  # Connection timeout
                look_for_keys=False,
                allow_agent=False
            )
            print(f"[SSH DEBUG] ✅ SSH connection successful!")
            app_logger.log_info(f"SSH connection established to {vm_ip} as {username}")
        except paramiko.ssh_exception.NoValidConnectionsError as e:
            print(f"[SSH ERROR] NoValidConnectionsError: {e}")
            raise Exception(f"Connection refused (SSH unreachable): {e}")
        except paramiko.ssh_exception.AuthenticationException as e:
            print(f"[SSH ERROR] AuthenticationException: {e}")
            print(f"[SSH DEBUG] This usually means:")
            print(f"  1. Public key not in {username}'s ~/.ssh/authorized_keys")
            print(f"  2. Wrong username")
            print(f"  3. Key permissions issue on VM")
            raise Exception(f"Authentication failed: {e}")
        except Exception as e:
            print(f"[SSH ERROR] Connection error: {type(e).__name__}: {e}")
            raise Exception(f"Connection failed: {e}")
        
        # Execute command
        try:
            print(f"[SSH DEBUG] Executing command: {command[:50]}...")
            stdin, stdout, stderr = ssh.exec_command(command, get_pty=True, timeout=exec_timeout)
            exit_status = stdout.channel.recv_exit_status()
            output = stdout.read().decode('utf-8', errors='replace')
            error_output = stderr.read().decode('utf-8', errors='replace')
            ssh.close()
            print(f"[SSH DEBUG] Command completed with exit status: {exit_status}")
            
            if error_output:
                output += f"\n[STDERR]\n{error_output}"
            
            # --- LOGGING PHASE ---
            ssh_logger.log_command_execution(username, command, output, exit_status, validation_summary)
            app_logger.log_info(f"execute_ssh: command completed with exit status {exit_status}")
            return output
        
        except paramiko.ssh_exception.SSHException as e:
            print(f"[SSH ERROR] SSHException during command execution: {e}")
            raise Exception(f"SSH command execution failed: {e}")
        except subprocess.TimeoutExpired:
            print(f"[SSH ERROR] TimeoutExpired: command took > {exec_timeout}s")
            raise Exception(f"Command execution timeout ({exec_timeout}s exceeded)")
    
    except Exception as e:
        ssh_logger.log_ssh_error(command, str(e), validation_summary)
        app_logger.log_error("execute_ssh", str(e))
        print(f"[SSH ERROR] Final error: {str(e)}")
        return f"❌ SSH execution error: {str(e)}"


def upload_to_vm(local_path, remote_path, credentials, oslogin_service):
    """
    Upload local file to remote VM via SFTP.
    
    Args:
        local_path: Path to local file
        remote_path: Path on remote VM
        credentials: Google Cloud credentials
        oslogin_service: OS Login service client
        
    Returns:
        str: Status message (success or error)
    """
    from app.core.auth import get_ssh_key
    
    vm_ip = _get_vm_ip()
    if not vm_ip:
        return "❌ VM_IP not configured or could not be resolved"
    
    key, username = get_ssh_key(credentials, oslogin_service)
    if not key or not username:
        return "❌ Failed to prepare SSH credentials for SFTP"
    
    try:
        app_logger.log_info(f"upload_to_vm: uploading {local_path} to {vm_ip}:{remote_path} as {username}")
        
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(vm_ip, username=username, pkey=key, timeout=60)
        sftp = ssh.open_sftp()
        sftp.put(local_path, remote_path)
        sftp.close()
        ssh.close()
        
        msg = f"✅ File uploaded to VM: {remote_path}"
        app_logger.log_info(msg)
        return msg
    
    except Exception as e:
        err_msg = f"SFTP upload failed: {str(e)}"
        app_logger.log_error("upload_to_vm", str(e))
        return f"❌ {err_msg}"
