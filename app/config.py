import os



# Project and GCP settings
# PROJECT_ID resolves dynamically from google.auth.default() at startup (see app.py)
PROJECT_ID = None

LOCATION = os.getenv("LOCATION", "us-central1")



# Model names

MODEL_PRO = "gemini-3.1-pro-preview"

MODEL_FLASH = "gemini-3-flash-preview"



# Directory paths

ADR_DIR = "docs/ADR/"

LOGS_DIR = "logs/"

SSH_LOG_FILE = os.path.join(LOGS_DIR, "ssh_audit.log")



# GCP Compute Instance settings (used for SSH operations)

REPO_PATH = os.getcwd()

VM_IP = os.getenv("VM_IP")

DEFAULT_VM_USERNAME = os.getenv("DEFAULT_VM_USERNAME", "anna_sonny48")

GCP_INSTANCE_NAME = os.getenv("GCP_INSTANCE_NAME", "wp-ai-agent-server")

GCP_INSTANCE_ZONE = os.getenv("GCP_INSTANCE_ZONE", "us-central1-f")