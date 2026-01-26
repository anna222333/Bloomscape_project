# STAGE A — FOUNDATION

## 1. Stage Purpose

Establish the **governance foundation** for the entire project:
- documentation structure and navigation,
- templates for stage briefs and ADRs,
- quality gates and acceptance model,
- risk register and scope creep controls,
- change control rules sufficient to start Stage B without oral context.

No implementation is allowed in Stage A.

---

## 2. Stage Position in Lifecycle

- Previous stage: N/A (Stage A is the entry stage)
- Next stage: Stage B — Discovery

---

## 3. In-Scope

- Create and maintain governance documents in Git.
- Define repository documentation structure, naming, and linking conventions.
- Provide templates:
  - Stage Brief template
  - ADR template
- Define quality model:
  - Definition of Done (DoD)
  - Acceptance Tests (AT)
  - Quality Gates
- Create and maintain risk governance (initial register).
- Define Change Control rules and ADR usage criteria.

---

## 4. Out-of-Scope (Explicit)

- Any environment changes (hosting, WordPress, Docker, VM, OS).
- Any implementation or configuration work.
- Any technical execution instructions (CLI commands, installation steps).
- Any content creation for the store.

---

## 5. Deliverables

| ID | Deliverable | Description | Format |
|----|-------------|-------------|--------|
| D-A-01 | MASTER_PLAN.md | Project governance and stage model | Markdown |
| D-A-02 | README.md | Repository navigation hub | Markdown |
| D-A-03 | WORK_BREAKDOWN.md | Stage-level WBS | Markdown |
| D-A-04 | QUALITY_GATES.md | Quality model and gates | Markdown |
| D-A-05 | RISK_REGISTER.md | Risk register | Markdown |
| D-A-06 | docs/STAGE_BRIEFS/_TEMPLATE.md | Stage Brief template | Markdown |
| D-A-07 | docs/STAGE_BRIEFS/STAGE_A..I.md | Stage brief skeletons | Markdown |
| D-A-08 | docs/ADR/ADR-000_TEMPLATE.md | ADR template | Markdown |

---

## 6. Quality Gates & Acceptance Criteria

### 6.1 Definition of Done (DoD)

Stage A is done when:
- all Stage A deliverables exist as files in Git,
- repository navigation is coherent and self-contained,
- change control is defined and usable,
- quality gates and acceptance tests are defined,
- risk register exists and includes scope creep risk.

### 6.2 Acceptance Tests

| ID | Test | Description |
|----|------|-------------|
| AT-A1 | Readability & Verifiability | A new contributor can follow governance docs without oral context |
| AT-A2 | Scope Boundaries | Forbidden actions are explicit; no implicit execution steps exist |

---

## 7. Dependencies & Inputs

Inputs:
- Stage A instruction set (governance-only)
- Existing repository files (if any)

---

## 8. Risks & Mitigation

| Risk ID | Description | Mitigation |
|--------:|-------------|------------|
| R-004 | Scope creep (docs drifting into execution) | Explicit forbidden scope; ADR required for scope changes; quality checks per iteration |

---

## 9. Change Control

Any change to:
- stage model,
- deliverables list,
- governance rules,
requires an ADR.

---

## 10. Stage Closure Rules

Stage A may be closed only when:
- DoD is satisfied,
- AT-A1 and AT-A2 pass,
- all files are committed and linked.

---

## 11. Document Status

Status: Closed  
Owner: Project Governance  
Change control: ADR required

---

## 12. Stage Closure Record

Closure date: 2026-01-26  
Gate: QG-A (Foundation Readiness) — PASSED

Evidence (Git paths):
- `MASTER_PLAN.md`
- `README.md`
- `WORK_BREAKDOWN.md`
- `QUALITY_GATES.md`
- `RISK_REGISTER.md`
- `docs/STAGE_BRIEFS/_TEMPLATE.md`
- `docs/ADR/ADR-000_TEMPLATE.md`
- `docs/STAGE_BRIEFS/STAGE_A.md` … `docs/STAGE_BRIEFS/STAGE_I.md`
- Exports (snapshot): `docs/EXPORTS/stage_a_foundation_artifacts_export.txt`
- Repo metadata: `docs/REPO_METADATA.md`
- Contribution rules: `CONTRIBUTING.md`

Acceptance Tests:
- AT-A1 — PASSED
- AT-A2 — PASSED

Notes:
- Stage A is governance-only; no execution/environment changes were performed or documented.
