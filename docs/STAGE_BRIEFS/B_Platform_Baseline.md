# STAGE BRIEF — B: Platform Baseline

## Purpose
Deliver a reproducible WordPress + WooCommerce baseline that boots via Docker Compose on Ubuntu VM.

## Scope
- **In scope:** Compose definition, persistent volumes, base WordPress/WooCommerce settings.
- **Out of scope:** UX/content enhancements or feature experimentation.

## Deliverables
- Baseline documentation in docs/ plus AT-B* evidence from Stage Chat.

## Definition of Done
- Baseline documented and executable per repo docs.
- WooCommerce installed with admin access configured.
- Persistence behavior confirmed across restarts.

## Acceptance Tests
- AT-B1: Startup works following README/runbook.
- AT-B2: WP admin dashboard is reachable.
- AT-B3: Data survives container restarts.

## Dependencies
- Depends on Stage A artifacts.

## Tasks
- B-01: Define Docker Compose baseline.
- B-02: Document configuration steps.
- B-03: Capture persistence verification.

## Risks
- R-001: Unable to reproduce baseline reliably.
- R-005: Data loss during restarts.

## Handoff
Stage Chat B shares baseline report and evidence stored in the repo.
