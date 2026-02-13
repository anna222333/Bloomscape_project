# Contributing (Docs-Only)

This repository is a **docs-first governance system**. Contributions must remain documentation-only.

## What you may change
- Governance docs: `MASTER_PLAN.md`, `WORK_BREAKDOWN.md`, `QUALITY_GATES.md`, `RISK_REGISTER.md`
- Stage briefs: `docs/STAGE_BRIEFS/STAGE_*.md`
- Templates: `docs/STAGE_BRIEFS/_TEMPLATE.md`, `docs/ADR/ADR-000_TEMPLATE.md`
- Navigation: `README.md`

## What is not allowed
- Source code, deployment steps, environment setup instructions (CLI commands), secrets/credentials.

## Change Control (ADR required)
Create an ADR if your change affects:
- scope boundaries (in/out of scope),
- stage model (A–I sequencing, entry/exit rules),
- deliverables (adding/removing/renaming outputs),
- quality model (DoD, Acceptance Tests, Quality Gates),
- tooling/platform choices recorded at governance level.

Use template:
- `docs/ADR/ADR-000_TEMPLATE.md`

## Consistency rule
If an ADR is accepted, update all impacted documents in the same change set, at minimum:
- `MASTER_PLAN.md`
- `WORK_BREAKDOWN.md`
- relevant `docs/STAGE_BRIEFS/STAGE_<X>.md`
- `QUALITY_GATES.md` (if impacted)
- `RISK_REGISTER.md` (if impacted)
