# Environment Baseline (Stage B)

## Status: PROVISIONED (As of Active Phase)

## 1. Runtime Architecture
The application is running in a containerized environment on a Remote Google Cloud VM.

### Core Stack
- **Orchestration:** Docker Compose
- **Web Server:** Nginx (Proxying PHP-FPM)
- **Application:** WordPress (PHP 8.2)
- **Database:** MySQL 8.0
- **Cache:** Redis (Object Cache)
- **CLI:** WP-CLI (Installed in app container)

## 2. Persistence Strategy
- **Database:** Docker Volume `db_data` -> Persists MySQL data.
- **WordPress Content:** Docker Volume `wp_data` -> Persists `/var/www/html` (uploads, plugins, themes).
- **Verification:** Automated audit confirmed data survival after container restart.

## 3. Configuration & Secrets
- **Environment Variables:** Managed via `.env` (excluded from git).
- **Admin Credentials:** Generated during provisioning (See `ssh_audit.log` or secure storage). *Do not commit to repo.*

## 4. Network Access
- **Public Access:** Via VM Public IP (Port 80/443).
- **Current Issue:** `siteurl` and `home` currently set to placeholder. Requires update to Public IP for correct routing.