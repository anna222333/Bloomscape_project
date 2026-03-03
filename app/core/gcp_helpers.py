"""
GCP Compute API Helper Functions

Provides utilities for interacting with Google Cloud Compute Engine instances.
Used for SSH operations: IP resolution, OS Login validation, metadata management.
"""

import os
import streamlit as st
from googleapiclient import discovery
import app.config
from app.core.logger import app_logger


def get_compute_service(credentials):
    """
    Build a Compute Engine API client.
    
    Args:
        credentials: Google Cloud credentials
        
    Returns:
        google.api_core.grpc_service.Service: Compute API service client
    """
    return discovery.build('compute', 'v1', credentials=credentials)


def get_instance_ip(instance_name, zone, credentials, ip_type='external'):
    """
    Retrieve the IP address of a GCP Compute Engine instance.
    
    Args:
        instance_name: Name of the Compute Engine instance
        zone: GCP zone (e.g., 'us-central1-f')
        credentials: Google Cloud credentials
        ip_type: 'external' (default) or 'internal'
        
    Returns:
        str: IP address, or None if not found
    """
    try:
        compute = get_compute_service(credentials)
        
        # Get instance details
        request = compute.instances().get(
            project=app.config.PROJECT_ID,
            zone=zone,
            instance=instance_name
        )
        response = request.execute()
        
        if ip_type == 'external':
            # Try to get external IP from accessConfigs
            network_interfaces = response.get('networkInterfaces', [])
            for iface in network_interfaces:
                access_configs = iface.get('accessConfigs', [])
                if access_configs:
                    ext_ip = access_configs[0].get('natIP')
                    if ext_ip:
                        app_logger.log_info(f"Instance {instance_name}: external IP = {ext_ip}")
                        return ext_ip
            # No external IP found
            app_logger.log_info(f"Instance {instance_name}: no external IP configured")
            return None
        
        elif ip_type == 'internal':
            # Get internal IP (networkIP)
            network_interfaces = response.get('networkInterfaces', [])
            if network_interfaces:
                int_ip = network_interfaces[0].get('networkIP')
                if int_ip:
                    app_logger.log_info(f"Instance {instance_name}: internal IP = {int_ip}")
                    return int_ip
            return None
        
    except Exception as e:
        app_logger.log_error("get_instance_ip", f"Failed to retrieve IP: {str(e)}")
        return None


def validate_instance_exists(instance_name, zone, credentials):
    """
    Check if a Compute Engine instance exists.
    
    Args:
        instance_name: Name of the instance
        zone: GCP zone
        credentials: Google Cloud credentials
        
    Returns:
        bool: True if instance exists, False otherwise
    """
    try:
        compute = get_compute_service(credentials)
        
        request = compute.instances().get(
            project=app.config.PROJECT_ID,
            zone=zone,
            instance=instance_name
        )
        response = request.execute()
        
        status = response.get('status', 'UNKNOWN')
        app_logger.log_info(f"Instance {instance_name} status: {status}")
        return True
        
    except Exception as e:
        if '404' in str(e):
            app_logger.log_info(f"Instance {instance_name} not found")
            return False
        app_logger.log_error("validate_instance_exists", str(e))
        return False


def is_oslogin_enabled(instance_name, zone, credentials):
    """
    Check if OS Login is enabled on an instance.
    
    Args:
        instance_name: Name of the instance
        zone: GCP zone
        credentials: Google Cloud credentials
        
    Returns:
        bool: True if OS Login is enabled, False otherwise
    """
    try:
        compute = get_compute_service(credentials)
        
        request = compute.instances().get(
            project=app.config.PROJECT_ID,
            zone=zone,
            instance=instance_name
        )
        response = request.execute()
        
        metadata = response.get('metadata', {})
        items = metadata.get('items', [])
        
        for item in items:
            if item.get('key') == 'enable-oslogin':
                value = item.get('value', '').lower()
                is_enabled = value == 'true'
                app_logger.log_info(f"Instance {instance_name}: enable-oslogin = {value}")
                return is_enabled
        
        app_logger.log_info(f"Instance {instance_name}: enable-oslogin metadata not set (default: disabled)")
        return False
        
    except Exception as e:
        app_logger.log_error("is_oslogin_enabled", str(e))
        return False


def get_instance_ssh_keys(instance_name, zone, credentials):
    """
    Retrieve SSH public keys set in instance metadata.
    
    Args:
        instance_name: Name of the instance
        zone: GCP zone
        credentials: Google Cloud credentials
        
    Returns:
        dict: Mapping of username -> list of public keys
    """
    try:
        compute = get_compute_service(credentials)
        
        request = compute.instances().get(
            project=app.config.PROJECT_ID,
            zone=zone,
            instance=instance_name
        )
        response = request.execute()
        
        metadata = response.get('metadata', {})
        items = metadata.get('items', [])
        
        ssh_keys_by_user = {}
        for item in items:
            if item.get('key') == 'ssh-keys':
                # Format: "username:ssh-rsa AAAA...==\nuser2:ssh-rsa BBBB..."
                ssh_keys_str = item.get('value', '')
                for line in ssh_keys_str.strip().split('\n'):
                    if ':' in line:
                        username, key_part = line.split(':', 1)
                        if username not in ssh_keys_by_user:
                            ssh_keys_by_user[username] = []
                        ssh_keys_by_user[username].append(key_part.strip())
        
        app_logger.log_info(f"Instance {instance_name}: found SSH keys for users: {list(ssh_keys_by_user.keys())}")
        return ssh_keys_by_user
        
    except Exception as e:
        app_logger.log_error("get_instance_ssh_keys", str(e))
        return {}


def _wait_for_zone_operation(compute, project, zone, operation_name, timeout=60, poll_interval=3):
    """
    Poll a GCP zone operation until it reaches DONE status.

    Args:
        compute: Compute Engine API client
        project: GCP project ID
        zone: GCP zone
        operation_name: Name of the zone operation to wait for
        timeout: Maximum seconds to wait (default: 60)
        poll_interval: Seconds between polls (default: 3)

    Raises:
        Exception: If the operation fails or times out
    """
    import time
    deadline = time.time() + timeout
    while time.time() < deadline:
        op = compute.zoneOperations().get(
            project=project,
            zone=zone,
            operation=operation_name
        ).execute()
        status = op.get('status')
        print(f"[DEBUG] _wait_for_zone_operation: {operation_name} status={status}")
        if status == 'DONE':
            # Check for errors
            error = op.get('error')
            if error:
                errors = error.get('errors', [])
                msg = '; '.join(e.get('message', '') for e in errors)
                raise Exception(f"setMetadata operation failed: {msg}")
            return
        time.sleep(poll_interval)
    raise Exception(f"setMetadata operation timed out after {timeout}s (still {status})")


def add_ssh_key_to_instance_metadata(public_key_str, username, instance_name, zone, credentials):
    """
    Add or update SSH public key in instance metadata.
    
    Args:
        public_key_str: Public key string (e.g., "ssh-rsa AAAA...")
        username: Username to associate with the key
        instance_name: Name of the instance
        zone: GCP zone
        credentials: Google Cloud credentials
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        print(f"[DEBUG] add_ssh_key_to_instance_metadata: Starting for {username}@{instance_name}")
        compute = get_compute_service(credentials)
        
        # Get current metadata
        print(f"[DEBUG] Getting instance metadata...")
        request = compute.instances().get(
            project=app.config.PROJECT_ID,
            zone=zone,
            instance=instance_name
        )
        response = request.execute()
        print(f"[DEBUG] Got instance response, status={response.get('status')}")
        
        metadata = response.get('metadata', {})
        items = metadata.get('items', [])
        fingerprint = metadata.get('fingerprint', '')
        print(f"[DEBUG] Current metadata items count: {len(items)}, fingerprint: {fingerprint[:20]}...")
        
        # Build new ssh-keys value
        ssh_keys_dict = {}
        for item in items:
            if item.get('key') == 'ssh-keys':
                ssh_keys_str = item.get('value', '')
                for line in ssh_keys_str.strip().split('\n'):
                    if ':' in line:
                        user, key = line.split(':', 1)
                        ssh_keys_dict[user] = key.strip()
                print(f"[DEBUG] Found existing SSH keys for users: {list(ssh_keys_dict.keys())}")
        
        # Add/update new key
        ssh_keys_dict[username] = public_key_str
        print(f"[DEBUG] Added/updated key for user: {username}")
        
        # Format back to string
        ssh_keys_str = '\n'.join([f"{u}:{k}" for u, k in ssh_keys_dict.items()])
        
        # Update metadata
        new_items = [item for item in items if item.get('key') != 'ssh-keys']
        new_items.append({'key': 'ssh-keys', 'value': ssh_keys_str})
        
        new_metadata = {
            'items': new_items,
            'fingerprint': fingerprint
        }
        
        print(f"[DEBUG] Calling setMetadata with {len(new_items)} items...")
        # Apply update
        request = compute.instances().setMetadata(
            project=app.config.PROJECT_ID,
            zone=zone,
            instance=instance_name,
            body=new_metadata
        )
        result = request.execute()
        print(f"[DEBUG] setMetadata response: {result}")

        # Wait for the async operation to fully complete before returning
        op_name = result.get('name')
        if op_name:
            print(f"[DEBUG] Waiting for setMetadata operation to complete: {op_name}")
            _wait_for_zone_operation(compute, app.config.PROJECT_ID, zone, op_name, timeout=60)
            print(f"[DEBUG] ✅ setMetadata operation DONE")
        
        app_logger.log_info(f"SSH key added to {instance_name} for user {username}")
        print(f"[DEBUG] ✅ SSH key successfully added")
        return True
        
    except Exception as e:
        print(f"[ERROR] add_ssh_key_to_instance_metadata failed: {e}")
        import traceback
        traceback.print_exc()
        app_logger.log_error("add_ssh_key_to_instance_metadata", str(e))
        return False
