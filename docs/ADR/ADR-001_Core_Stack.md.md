# ADR-001: Core Tech Stack & Automation Approach

- **Status:** Accepted
- **Date:** 2024-05-24
- **Decision Owner:** Chief Architect
- **Stage:** B (Platform Baseline)

---

## 1. Context
The business goal is "automation of website development". We need a standardized target runtime to build our automation tools around. We also need to define the language of the automation tools themselves.

## 2. Decision
We will utilize the following stack:

### A. Automation Engine (The "Bloomscape" App)
- **Language:** Python 3.x (Entry point `app.py`).
- **Scripting:** Bash (for low-level system interactions via `bash-wizard`).
- **Interface:** CLI-based interaction.

### B. Target Runtime (The Generated Product)
- **CMS:** WordPress (Latest Stable).
- **Commerce Engine:** WooCommerce.
- **Database:** MySQL/MariaDB.
- **Server Interface:** SSH + WP-CLI (WordPress Command Line Interface).

## 3. Consequences
- **Positive:** WP-CLI provides extensive support for headless/CLI management, which is crucial for automation.
- **Negative:** WordPress architecture requires state management (DB + Filesystem), which complicates "atomic" deployments compared to static sites.
- **Mitigation:** We will strictly separate "Code" (Themes/Plugins) from "Data" (Uploads/DB) in our deployment logic.