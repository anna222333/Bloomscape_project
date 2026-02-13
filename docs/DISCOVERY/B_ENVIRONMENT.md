# Environment Specification (Stage B)

## 1. Infrastructure Topology
*   **Controller:** Local machine running `app.py` (Streamlit). Hosting the AI Agents.
*   **Repository:** GitHub (Source of Truth).
*   **Runtime Host:** Google Cloud Platform VM.

## 2. Access Mechanism
*   **Protocol:** SSH.
*   **Authentication:** SSH Key (Managed via Google Secret Manager, injected into `app.py`).
*   **User:** Defined in `.env` (VM_USER).

## 3. Directory Structure (Target on VM)
*   **Root:** `/home/<VM_USER>/Bloomscape_project/` (Assumed - to be verified by Foreman).
*   **Web Root:** TBD (Likely inside Docker container).

## 4. Current State Constraints
*   The VM is live.
*   The Orchestrator has root/sudo privileges (Assumed).
*   **Network:** Port 80/443 must be open for web access.