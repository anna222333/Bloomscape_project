# MASTER PLAN — Bloomscape-like WooCommerce Store

## Purpose
Capture the strategy for delivering a reproducible WooCommerce storefront inspired by Bloomscape, including documentation, demo artifacts, and runbooks that can be recreated on an Ubuntu VM with Docker.

## Scope
### In Scope
- Docker Compose environment with WordPress + WooCommerce baseline and documented startup steps.
- Theme or child-theme adjustments to deliver a Bloomscape-like UX for catalog browsing, product detail, search, and filters.
- Sample catalog content (products, categories, attributes, variations, and imagery) suitable for portfolio demos.
- Checkout lifecycle with at least one mocked payment option plus minimal shipping and tax handling for the demo scenario.
- Operational guidance for backups, logging, monitoring links, and upgrade notes.
- Security and compliance checklist for secrets handling, permission hygiene, and patching reminders.
- Demo/portfolio artifacts (scenarios, screenshots, reproducible instructions) to validate the experience.

### Out of Scope
- Custom headless architecture beyond the documented baseline (requires ADR to revisit).
- ERP/CRM/1C or complex external API integrations.
- Multi-warehouse/multi-vendor systems or advanced loyalty/referrals.
- Production migrations, real domains, or live payments without a dedicated ADR.

## Working Assumptions (validated)
- Payments: sandbox/test-only, no live transactions.
- Theme: existing theme with customization, no headless delivery.
- Store locale: EN, currency EUR, shipping worldwide.
- Demo catalog size: 20 products.
- Evidence (screenshots/media) is stored in this repository with size controls.

## Prerequisites
- Ubuntu VM with Docker and Docker Compose installed.
- Access to this Git repository; Git + Markdown is the source of truth for docs.
- A workspace (AppFlowy/Notion) for coordination; docs hosted here are canonical.

## Procedure
### Context
- Platform: WordPress + WooCommerce.
- Environment: Ubuntu VM running Docker.
- Execution: Codex agent implementing documentation.
- Evidence focus: capture commands or configs in docs.

### Stage Map and Dependencies
- **A. Foundation** — create repo dossier, docs standards, change control rules.
- **B. Platform Baseline** — scripted Docker Compose launch, admin access, base configuration.
- **C. Theme & UX** — theme/child-theme styling, navigation, Bloomscape-like patterns.
- **D. Catalog & Content** — demo catalog, categories, attributes, imagery.
- **E. Checkout & Payments** — end-to-end purchase path, tests for checkout.
- **F. Operations & Observability** — backups, logging, health checks, runbook instructions.
- **G. Security & Compliance** — hardening baseline, secret management, update controls.
- **H. Demo & Portfolio** — demo narratives, screenshots, README "how to run".
- **I. Handover & Runbook** — final runbook, known issues, handover documentation.

### Dependencies
- B depends on A.
- C depends on B.
- D depends on C (with partial parallel work but holds for acceptance).
- E depends on B and D.
- F depends on B; G depends on B and F (for logs and controls).
- H depends on C, D, E, F, G.
- I depends on H.

### Critical Path for Demo Store
A → B → C → D → E → H → I.

### Definition of Done per Stage
- **A:** docs structure established, templates ready, change control rules documented.
- **B:** `docker compose up` launches WP + WooCommerce, admin creds verified, base configs captured.
- **C:** Bloomscape-like design skeleton implemented, core pages readable.
- **D:** Catalog demo content present, categories and attributes functioning, imagery included.
- **E:** Sample checkout completes end-to-end in a test scenario with acceptance checklist.
- **F:** Backups/restores documented, health checks/logging available.
- **G:** Baseline hardening applied, secrets excluded, security checklist satisfied.
- **H:** Demo scripts, screenshots, README “how to run” reproducible.
- **I:** Runbook, known issues, and handover checklist finalized.

### Milestones
- **M1 (post-B):** Platform boots with one command and WooCommerce is reachable.
- **M2 (post-D):** Catalog content complete for review.
- **M3 (post-E):** Working end-to-end order flow demonstrable.
- **M4 (post-G):** Security and operations baseline documented.
- **M5 (post-I):** Portfolio package and runbook complete.

## Verification
- Confirm the repository structure with README and docs remains in sync with this plan.
- Verify Docker Compose can bring up WordPress + WooCommerce (capture `docker compose up` output). TODO: evidence.
- Validate catalog content and checkout tests; reference acceptance tests per stage briefs.
- Review security and ops checklists for completeness relative to Quality Gates.

## Evidence
- `docs/QUALITY_GATES.md` will capture reproducibility, acceptance tests, and metrics (link for detail).
- TODO: capture `docker compose up` logs, WP admin login screenshot (if applicable), and checkout logs once ready.
- TODO: document backups/logs output under `docs/STAGE_BRIEFS/F_...` evidence section.

## Troubleshooting
- If `docker compose up` fails, inspect container logs (e.g., `docker compose logs wordpress` or `mysql`).
- Missing assets should be addressed by verifying the catalog import instructions in the relevant stage brief.
- For any blocked ADR decisions, reference `docs/ADR/` templates before adjusting scope.
