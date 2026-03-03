"""
Authentication and SSH Key Management

Handles:
1. Gemini API key retrieval from Secret Manager
2. SSH key generation and configuration
  - OS Login path (when a Google identity email is resolvable)
  - Instance metadata path (fallback, only when OS Login is disabled)
"""

import os
import time
import streamlit as st
import paramiko
import requests as _requests
import google.auth.transport.requests
from google.cloud import secretmanager

import app.config
from app.config import GCP_INSTANCE_NAME, GCP_INSTANCE_ZONE, DEFAULT_VM_USERNAME
from app.core.logger import app_logger


def _get_identity_email(credentials):
    """
    Resolve the Google identity email from credentials.

    Tries multiple sources in order:
    1. credentials.service_account_email  (service account ADC / impersonation)
    2. credentials.signer_email           (impersonated SA chain)
    3. tokeninfo endpoint                 (user ADC / WIF without impersonation)

    Returns:
        str: email address, or None if not resolvable
    """
    # 1. service_account_email
    email = getattr(credentials, 'service_account_email', None)
    if email:
        app_logger.log_info(f"_get_identity_email: found service_account_email={email}")
        return email

    # 2. signer_email (impersonated SA)
    email = getattr(credentials, 'signer_email', None)
    if email:
        app_logger.log_info(f"_get_identity_email: found signer_email={email}")
        return email

    # 3. Tokeninfo endpoint (user ADC / WIF)
    try:
        request = google.auth.transport.requests.Request()
        credentials.refresh(request)
        token = getattr(credentials, 'token', None)
        if token:
            resp = _requests.get(
                "https://www.googleapis.com/oauth2/v1/tokeninfo",
                params={"access_token": token},
                timeout=10
            )
            if resp.status_code == 200:
                data = resp.json()
                email = data.get('email')
                if email:
                    app_logger.log_info(f"_get_identity_email: resolved via tokeninfo email={email}")
                    return email
                app_logger.log_info(f"_get_identity_email: tokeninfo response has no email field: {data}")
            else:
                app_logger.log_info(f"_get_identity_email: tokeninfo returned {resp.status_code}: {resp.text[:200]}")
    except Exception as e:
        app_logger.log_info(f"_get_identity_email: tokeninfo lookup failed: {e}")

    # 4. Read 'account' field from ADC JSON file (authorized_user type from gcloud auth application-default login)
    try:
        import json
        adc_path = os.path.expanduser("~/.config/gcloud/application_default_credentials.json")
        if os.path.exists(adc_path):
            with open(adc_path) as f:
                adc = json.load(f)
            if adc.get('type') == 'authorized_user':
                email = adc.get('account', '').strip()
                if email and '@' in email:
                    app_logger.log_info(f"_get_identity_email: resolved from ADC file account field: {email}")
                    return email
    except Exception as e:
        app_logger.log_info(f"_get_identity_email: ADC file lookup failed: {e}")

    # 5. Fallback: gcloud CLI
    try:
        import subprocess
        result = subprocess.run(
            ['gcloud', 'config', 'get-value', 'account'],
            capture_output=True, text=True, timeout=8
        )
        email = result.stdout.strip()
        if email and '@' in email:
            app_logger.log_info(f"_get_identity_email: resolved via gcloud config account: {email}")
            return email
    except Exception as e:
        app_logger.log_info(f"_get_identity_email: gcloud fallback failed: {e}")

    return None


def get_gemini_key(credentials):
    """
    Retrieve Gemini API key from Google Secret Manager.
    
    Args:
        credentials: Google Cloud credentials
        
    Returns:
        str: API key, or None if retrieval failed
    """
    try:
        client = secretmanager.SecretManagerServiceClient(credentials=credentials)
        name = f"projects/{app.config.PROJECT_ID}/secrets/GEMINI_KEY/versions/latest"
        response = client.access_secret_version(request={"name": name})
        return response.payload.data.decode("UTF-8")
    except Exception as e:
        app_logger.log_error("SecretManager", f"Failed to retrieve Gemini key: {e}")
        st.warning(f"⚠️ Could not retrieve Gemini API key from Secret Manager: {e}")
        return None


def get_ssh_key(credentials, oslogin_service):
    """
    Generate temporary SSH key and prepare for SSH connection.

    Routing logic:
    1. OS Login path  — used when a Google identity email is resolvable.
       Required when the VM has enable-oslogin=true (instance metadata keys are
       ignored by sshd in that case).
    2. Instance Metadata path  — fallback used only when no email can be resolved
       AND OS Login is disabled on the target VM.

    Args:
        credentials: Google Cloud credentials
        oslogin_service: OS Login API service client

    Returns:
        tuple: (paramiko.RSAKey, str) if successful, (None, None) if failed
    """
    try:
        user_email = _get_identity_email(credentials)

        if user_email:
            # Path 1: OS Login — import key for the resolved Google identity
            app_logger.log_info(f"get_ssh_key: identity email resolved ({user_email}); using OS Login path")
            key = paramiko.RSAKey.generate(2048)
            return _get_ssh_key_via_oslogin(key, user_email, oslogin_service)
        else:
            # Path 2: Instance Metadata fallback (only works when OS Login is disabled)
            app_logger.log_info(
                "get_ssh_key: could not resolve identity email; "
                "falling back to instance metadata path (requires OS Login disabled on VM)"
            )

            # Cache the private key so the same key pair is reused across SSH calls
            if 'ssh_private_key' in st.session_state and st.session_state.ssh_private_key:
                app_logger.log_info("Using cached SSH private key from session state")
                key = st.session_state.ssh_private_key
            else:
                key = paramiko.RSAKey.generate(2048)
                st.session_state.ssh_private_key = key
                app_logger.log_info("Generated and cached new SSH private key in session state")

            # Always re-upload to metadata to ensure VM has the current key
            public_key_str = f"{key.get_name()} {key.get_base64()}"
            return _get_ssh_key_via_instance_metadata(
                key, public_key_str, DEFAULT_VM_USERNAME,
                GCP_INSTANCE_NAME, GCP_INSTANCE_ZONE, credentials
            )
    
    except Exception as e:
        app_logger.log_error("get_ssh_key", str(e))
        st.error(f"❌ SSH key generation failed: {e}")
        return None, None


def _get_ssh_key_via_oslogin(key, user_email, oslogin_service):
    """
    Helper: Retrieve SSH key via OS Login (when service_account_email exists).
    
    Imports the public key to OS Login and retrieves POSIX username.
    """
    try:
        public_key = f"{key.get_name()} {key.get_base64()}"
        parent = f"users/{user_email}"
        
        # Retry import with exponential backoff
        response = None
        for attempt in range(1, 4):
            try:
                response = oslogin_service.users().importSshPublicKey(
                    parent=parent,
                    projectId=app.config.PROJECT_ID,
                    body={'key': public_key}
                ).execute()
                app_logger.log_info(f"OS Login: importSshPublicKey succeeded on attempt {attempt}")
                break
            except Exception as e:
                app_logger.log_info(f"OS Login: importSshPublicKey attempt {attempt} failed: {e}")
                if attempt < 3:
                    time.sleep(2 ** attempt)
                else:
                    raise
        
        login_profile = response.get('loginProfile', {}) if response else {}
        posix_accounts = login_profile.get('posixAccounts', [])
        
        if posix_accounts:
            username = posix_accounts[0].get('username')
            app_logger.log_info(f"OS Login: retrieved username '{username}' from POSIX accounts")
            return key, username
        else:
            app_logger.log_error("_get_ssh_key_via_oslogin", "No posixAccounts in OS Login response")
            st.error("❌ OS Login did not return POSIX accounts. Check instance configuration.")
            return None, None
    
    except Exception as e:
        app_logger.log_error("_get_ssh_key_via_oslogin", str(e))
        st.error(f"❌ OS Login error: {e}")
        return None, None


def _get_ssh_key_via_instance_metadata(key, public_key_str, username, instance_name, zone, credentials):
    """
    Helper: Add SSH key to instance metadata (when service_account_email missing - WIF).
    
    For WIF without impersonation, we add the public key directly to instance metadata.
    This is the same approach GitHub Actions uses.
    """
    from app.core.gcp_helpers import add_ssh_key_to_instance_metadata
    
    try:
        app_logger.log_info(f"WIF: Adding SSH public key to instance metadata for user '{username}'")
        print(f"[DEBUG] _get_ssh_key_via_instance_metadata: Adding key for user '{username}' to {instance_name}/{zone}")
        
        success = add_ssh_key_to_instance_metadata(
            public_key_str,
            username,
            instance_name,
            zone,
            credentials
        )
        
        print(f"[DEBUG] add_ssh_key_to_instance_metadata returned: {success}")
        
        if success:
            app_logger.log_info(f"SSH key successfully added to instance {instance_name} metadata for user {username}")
            return key, username
        else:
            err_msg = "add_ssh_key_to_instance_metadata returned False (check logs for details)"
            app_logger.log_error("_get_ssh_key_via_instance_metadata", err_msg)
            print(f"[ERROR] {err_msg}")
            st.error(f"❌ Failed to add SSH key to instance metadata. Check permissions.")
            return None, None
    
    except Exception as e:
        err_msg = str(e)
        app_logger.log_error("_get_ssh_key_via_instance_metadata", err_msg)
        print(f"[ERROR] Exception in _get_ssh_key_via_instance_metadata: {err_msg}")
        import traceback
        traceback.print_exc()
        st.error(f"❌ Failed to configure SSH on instance: {e}")
        return None, None