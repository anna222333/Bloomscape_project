# Stage Chat B — Instructions (Platform Baseline)

## Purpose
Execute Stage B using Git as the Source of Truth and return evidence that closes AT-B1, AT-B2, and AT-B3.

## Allowed / Forbidden
**Allowed:** Documenting Docker/WordPress/WooCommerce baseline steps, capturing evidence, and updating governance Markdown under the established rules.  
**Forbidden:** Scope expansion, feature implementation beyond baseline discovery, or altering SoT rules without an ADR.

## Inputs (must read)
- `docs/STAGE_BRIEFS/STAGE_B.md` (including the “Stage B Handoff Expectations” block)
- `MASTER_PLAN.md` (Authoritative Paths)
- `QUALITY_GATES.md` (QG-DOC1 and related gates)
- `WORK_BREAKDOWN.md` (B-01..B-03 references)
- Discovery skeletons:
  - `docs/DISCOVERY/B_ENVIRONMENT.md`
  - `docs/DISCOVERY/B_PERSISTENCE.md`
  - `docs/DISCOVERY/B_WP_BASELINE.md`
  - `docs/DISCOVERY/B_WC_BASELINE.md`

## Required Outputs (Git-ready)
1. Record discovery facts/evidence in the four baseline skeletons (`docs/DISCOVERY/B_*`).
2. Update `docs/STAGE_BRIEFS/STAGE_B.md`:
   - Set Status to `Closed`.
   - Add a closure record that documents QG-B (if defined) and AT-B1..AT-B3 results with references to evidence.
3. Add a `docs/EXPORTS/` snapshot entry only when Stage B policy explicitly requires it.
4. Update `RISK_REGISTER.md` with any new or changed discovery risks and mitigations.

## Evidence requirements (minimum)
- **AT-B1:** Capture commands + expected outputs that prove the discovery environment boots from docs.
- **AT-B2:** Document WP admin and WooCommerce baseline checks (screenshots or logs).
- **AT-B3:** Describe persistence tests (restart + restore) with results.

## Report format
Create `docs/REPORTS/STAGE_B_REPORT.md` describing:
- What was done (mapped to B-01..B-03)
- Evidence links/paths
- Deviations or known issues
- Recommendations for Stage C

## Handoff rule
Stage C planning starts only after Stage B Report, updated Stage Brief, and updated discovery docs exist in Git.
