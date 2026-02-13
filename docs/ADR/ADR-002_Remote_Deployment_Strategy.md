# ADR-002: Remote Deployment Strategy (GitOps-lite)

- **Status:** Accepted
- **Date:** 2024-05-22
- **Decision Owner:** Architect
- **Stage:** B (Discovery / Infrastructure)

## 1. Context
The application relies on a **Remote Google Cloud VM** for the actual runtime (WordPress, Database), while the AI Agents operate locally via `app.py`. There is a risk of "Configuration Drift" where the live server state diverges from the code stored in GitHub.

## 2. Decision
We adopt a **"Repo-First"** policy for all persistent code and configurations.

### Rules:
1.  **Code is King:** PHP files, Theme assets, and Docker Compose files must be written to the local file system first, committed to Git, and then pulled to the VM.
2.  **Orchestrator's Role:** The Orchestrator is responsible for executing the synchronization mechanism (e.g., `ssh user@ip "cd /app && git pull"`).
3.  **Ephemeral configs:** One-off commands (installing dependencies, restarting services) are executed via SSH directly, but the *steps* to achieve them must be documented in `docs/` or scripted in a setup script (e.g., `setup.sh`).
4.  **No "Cowboy Coding":** Agents must strictly avoid using editors (nano/vim) directly on the server via SSH interactive shells.

## 3. Consequences
*   **Positive:** The site can be rebuilt from scratch using the Repo + `setup.sh`.
*   **Negative:** Slower iteration cycle (Edit -> Commit -> Push -> Pull -> Test).
*   **Mitigation:** For Stage B/C (Discovery/Setup), we allow direct shell commands for *exploration* (ls, cat, grep), but *changes* must go through Git.