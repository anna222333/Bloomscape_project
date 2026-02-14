# Technical Requirements (Stage B)

## 1. Runtime Environment
- **Container Runtime:** Docker Engine (Verified)
- **Orchestration:** Docker Compose
- **Host OS:** Linux (Ubuntu/Debian compatible) on Google Cloud VM

## 2. Application Stack (Target)
- **CMS:** WordPress 6.5+ (Latest Stable)
- **E-commerce:** WooCommerce 8.9+
- **Language:** PHP 8.2 (FPM)
- **Database:** MySQL 8.0 or MariaDB 10.11
- **Cache:** Redis 7.0 (Object Cache)
- **Web Server:** Nginx (Alpine based)

## 3. Development Tools
- **CLI:** WP-CLI (Primary configuration tool)
- **Dependency Manager:** Composer (PHP), NPM (Theme assets)
- **Version Control:** Git (Trunk-based)

## 4. Performance Constraints
- Page Load Time: < 2.0s
- Google Lighthouse Score: > 90 (Mobile/Desktop)