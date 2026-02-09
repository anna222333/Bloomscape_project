# STAGE H — RELEASE

## 1. Stage Purpose

Perform controlled release and handover:
- release preparation and governance,
- controlled deployment (as defined),
- release notes and handover documentation.

---

## 2. Stage Position in Lifecycle

- Previous stage: Stage G — Testing
- Next stage: Stage I — Closure

---

## 3. In-Scope

- Release readiness confirmation.
- Release process governance and tracking.
- Release notes and handover documentation.

---

## 4. Out-of-Scope (Explicit)

- Last-minute feature additions.
- Unapproved changes bypassing testing and change control.
- Scope expansion without ADR.

---

## 5. Deliverables

| ID | Deliverable | Description | Format |
|----|-------------|-------------|--------|
| D-H-01 | Release notes | Summary of what is released | Markdown |
| D-H-02 | Handover docs | Operational and usage notes | Markdown |
| D-H-03 | Release checklist | Evidence-based release readiness | Markdown |

(Exact file paths to be defined in Stage H under Change Control.)

---

## 6. Quality Gates & Acceptance Criteria

### 6.1 Definition of Done (DoD)

Stage H is done when:
- release readiness is confirmed,
- release notes and handover docs exist,
- release activities are recorded,
- any deviations are documented and approved.

### 6.2 Acceptance Tests

| ID | Test | Description |
|----|------|-------------|
| AT-H1 | Readiness | Release checklist passes |
| AT-H2 | Documentation | Release notes and handover docs exist |
| AT-H3 | Control | Deviations are recorded and approved |

---

## 7. Dependencies & Inputs

Inputs:
- Stage G test report and release readiness decision
- Approved ADRs affecting release

---

## 8. Risks & Mitigation

| Risk ID | Description | Mitigation |
|--------:|-------------|------------|
| R-H-01 | Uncontrolled release | Enforce release checklist and approvals |
| R-004 | Scope creep | ADR required for scope changes |

---

## 9. Change Control

Changes to release scope or go/no-go rules require ADR.

---

## 10. Stage Closure Rules

Stage H may be closed only when DoD is satisfied and acceptance tests pass.

---

## 11. Document Status

Status: Draft  
Owner: Project Governance  
Change control: ADR required
