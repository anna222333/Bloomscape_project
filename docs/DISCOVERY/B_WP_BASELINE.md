# Stage B: Platform Baseline Definition

**Status:** ESTABLISHED
**Date:** 2026-02-16
**Version:** 1.0.0

## 1. Runtime Environment
The following configuration is now the strict baseline for all development.

- **Infrastructure:** Google Cloud VM (Docker Host)
- **Orchestration:** Docker Compose
- **Web Server:** Nginx (Alpine based)
- **Application:** WordPress (PHP 8.2-FPM)
- **Database:** MySQL 8.0
- **Commerce Engine:** WooCommerce 10.5.1
- **Caching:** Redis 7.0

## 2. Access Coordinates (Dev Environment)
*Note: Credentials are stored here for team access during the specific Dev Stage. In Production, these will be managed via Secrets Manager.*

- **Public URL:** `http://34.121.114.145`
- **Admin Entry:** `http://34.121.114.145/wp-admin/`
- **User:** `bloom_admin`
- **Pass:** `Bloom2024!Secure_1771256012`

## 3. Configuration Standards
- **Permalinks:** `/%postname%/` (Enforced via CLI)
- **File System:** 
  - `wp-content` mounted via Docker Volume `wordpress_data`
  - DB persistence via Docker Volume `db_data`
- **Plugins (Core):**
  - WooCommerce (Active)
  - Redis Object Cache (Installed/Pending config)

## 4. Verification Gates (Passed)
- [x