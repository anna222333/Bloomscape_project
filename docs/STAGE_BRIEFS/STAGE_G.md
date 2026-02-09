# STAGE G — TESTING

## 1. Stage Purpose

Validate the implemented solution:
- define and execute test plans,
- record results and defects,
- confirm compliance with requirements and quality gates.

---

## 2. Stage Position in Lifecycle

- Previous stage: Stage F — Implementation
- Next stage: Stage H — Release

---

## 3. In-Scope

- Test planning and test execution governance.
- Test reporting and defect tracking.
- Validation against requirements and quality gates.
- Update risks related to quality and defects.

---

## 4. Out-of-Scope (Explicit)

- Adding new features.
- Scope expansion during testing without ADR.
- Uncontrolled fixes not tracked and governed.

---

## 5. Deliverables

| ID | Deliverable | Description | Format |
|----|-------------|-------------|--------|
| D-G-01 | Test plan | Scope, cases, criteria | Markdown |
| D-G-02 | Test report | Results and evidence | Markdown |
| D-G-03 | Defect log | Issues and status | Markdown |
| D-G-04 | Updated risk register | Testing/quality risks | Markdown |

(Exact file paths to be defined in Stage G under Change Control.)

---

## 6. Quality Gates & Acceptance Criteria

### 6.1 Definition of Done (DoD)

Stage G is done when:
- test plan is executed,
- results are recorded,
- critical defects are resolved or explicitly accepted,
- release readiness is documented.

### 6.2 Acceptance Tests

| ID | Test | Description |
|----|------|-------------|
| AT-G1 | Coverage | Planned test areas are covered |
| AT-G2 | Evidence | Results are recorded and reviewable |
| AT-G3 | Release readiness | Clear go/no-go outcome exists |

---

## 7. Dependencies & Inputs

Inputs:
- Stage B requirements
- Stage F implementation outputs
- Quality gates definition

---

## 8. Risks & Mitigation

| Risk ID | Description | Mitigation |
|--------:|-------------|------------|
| R-G-01 | Inadequate coverage | Enforce test planning gate |
| R-004 | Scope creep | ADR required for scope changes |

---

## 9. Change Control

Changes to acceptance criteria or release conditions require ADR.

---

## 10. Stage Closure Rules

Stage G may be closed only when DoD is satisfied and acceptance tests pass.

---

## 11. Document Status

Status: Draft  
Owner: Project Governance  
Change control: ADR required
