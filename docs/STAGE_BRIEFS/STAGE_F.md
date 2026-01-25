# STAGE F — IMPLEMENTATION

## 1. Stage Purpose

Execute the approved plans under strict change control:
- implement features and configurations defined by prior stages,
- track progress and deviations,
- record decisions and changes via ADR where required.

Stage F is the primary **execution stage**.

---

## 2. Stage Position in Lifecycle

- Previous stage: Stage E — Build Preparation
- Next stage: Stage G — Testing

---

## 3. In-Scope

- Implementation tasks approved in Stage E plans.
- Configuration and build work as explicitly authorized by Stage F plan.
- Ongoing change control, progress tracking, documentation updates.

---

## 4. Out-of-Scope (Explicit)

- Unplanned or undocumented work.
- Changes that bypass ADR and quality gates.
- Scope expansion not approved via ADR.

---

## 5. Deliverables

| ID | Deliverable | Description | Format |
|----|-------------|-------------|--------|
| D-F-01 | Implemented outputs | Built components/configurations | As defined |
| D-F-02 | Change log | ADRs / records for deviations | Markdown |
| D-F-03 | Progress records | Status and completion evidence | Markdown |

(Exact deliverables and file paths are defined in Stage F planning.)

---

## 6. Quality Gates & Acceptance Criteria

### 6.1 Definition of Done (DoD)

Stage F is done when:
- implementation plan items are completed,
- changes are properly recorded,
- evidence exists for readiness to test,
- quality gates for implementation are passed.

### 6.2 Acceptance Tests

| ID | Test | Description |
|----|------|-------------|
| AT-F1 | Plan compliance | Work matches the approved plan |
| AT-F2 | Change control | Deviations are tracked and approved |
| AT-F3 | Evidence | Completion evidence is recorded |

---

## 7. Dependencies & Inputs

Inputs:
- Stage E approved implementation plan and readiness checklist
- Stage B/C/D outputs and ADRs

---

## 8. Risks & Mitigation

| Risk ID | Description | Mitigation |
|--------:|-------------|------------|
| R-F-01 | Uncontrolled change | Enforce ADR and gates; frequent reviews |
| R-004 | Scope creep | Reject non-approved scope changes |

---

## 9. Change Control

Any change affecting scope, architecture, or tooling requires ADR.

---

## 10. Stage Closure Rules

Stage F may be closed only when DoD is satisfied and acceptance tests pass.

---

## 11. Document Status

Status: Draft  
Owner: Project Governance  
Change control: ADR required
