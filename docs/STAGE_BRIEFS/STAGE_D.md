# STAGE D — UX / UI

## 1. Stage Purpose

Define the user experience and user interface design:
- information architecture,
- user flows,
- UI system and key screens,
- UX/UI validation against requirements.

Stage D produces **design artifacts and documentation**, not implementation.

---

## 2. Stage Position in Lifecycle

- Previous stage: Stage C — Architecture
- Next stage: Stage E — Build Preparation

---

## 3. In-Scope

- Information architecture and navigation model.
- User flows and key scenarios.
- UI design system and screen specifications (documentation).
- Update risk register for UX/UI risks.

---

## 4. Out-of-Scope (Explicit)

- UI implementation (themes, CSS, code).
- Environment setup or configuration.
- Content production beyond design documentation needs.

---

## 5. Deliverables

| ID | Deliverable | Description | Format |
|----|-------------|-------------|--------|
| D-D-01 | Information architecture | Site structure and navigation | Markdown/Diagram |
| D-D-02 | UX flows | Primary user journeys | Markdown/Diagram |
| D-D-03 | UI specs | Key screens and design rules | Markdown |
| D-D-04 | Updated risk register | UX/UI risks added/updated | Markdown |

(Exact file paths to be defined in Stage D under Change Control.)

---

## 6. Quality Gates & Acceptance Criteria

### 6.1 Definition of Done (DoD)

Stage D is done when:
- IA and flows are documented and consistent,
- UI specs are clear enough for build planning,
- outputs are traceable to requirements,
- risks are updated.

### 6.2 Acceptance Tests

| ID | Test | Description |
|----|------|-------------|
| AT-D1 | Usability coverage | Main user journeys are documented |
| AT-D2 | Consistency | IA, flows, and UI rules do not conflict |
| AT-D3 | Traceability | UX/UI decisions map to requirements |

---

## 7. Dependencies & Inputs

Inputs:
- Stage B requirements
- Stage C architecture constraints and decisions

---

## 8. Risks & Mitigation

| Risk ID | Description | Mitigation |
|--------:|-------------|------------|
| R-D-01 | Design drift from requirements | Traceability checks; review gates |
| R-004 | Scope creep | ADR for changes affecting scope or lifecycle |

---

## 9. Change Control

Changes to IA that affect scope or architecture require an ADR.

---

## 10. Stage Closure Rules

Stage D may be closed only when DoD is satisfied and acceptance tests pass.

---

## 11. Document Status

Status: Draft  
Owner: Project Governance  
Change control: ADR required
