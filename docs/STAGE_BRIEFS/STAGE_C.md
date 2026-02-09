# STAGE C — ARCHITECTURE

## 1. Stage Purpose

Define the solution architecture based on Stage B outputs:
- high-level architecture and components,
- integration boundaries,
- key design decisions recorded as ADRs,
- architecture validation against requirements and constraints.

Stage C produces **design and decisions**, not execution.

---

## 2. Stage Position in Lifecycle

- Previous stage: Stage B — Discovery
- Next stage: Stage D — UX/UI

---

## 3. In-Scope

- Architecture definition (components, boundaries, responsibilities).
- Decision-making and recording via ADRs.
- Architecture validation against requirements/constraints.
- Update risk register for architectural risks.

---

## 4. Out-of-Scope (Explicit)

- Implementation.
- Environment changes or deployment actions.
- Tooling setup beyond documented decisions (no execution steps).

---

## 5. Deliverables

| ID | Deliverable | Description | Format |
|----|-------------|-------------|--------|
| D-C-01 | Architecture overview | High-level structure and rationale | Markdown |
| D-C-02 | ADR set | Architecture decisions recorded | Markdown |
| D-C-03 | Validation notes | Requirements-to-architecture checks | Markdown |
| D-C-04 | Updated risk register | Architecture risks added/updated | Markdown |

(Exact file paths to be defined in Stage C under Change Control.)

---

## 6. Quality Gates & Acceptance Criteria

### 6.1 Definition of Done (DoD)

Stage C is done when:
- architecture is documented and internally consistent,
- key decisions are captured as ADRs,
- architecture is validated against Stage B requirements,
- risks are updated and mitigations defined.

### 6.2 Acceptance Tests

| ID | Test | Description |
|----|------|-------------|
| AT-C1 | Consistency | Architecture components and boundaries are coherent |
| AT-C2 | Traceability | Major requirements map to architectural choices |
| AT-C3 | Decision Logging | Relevant decisions have ADRs |

---

## 7. Dependencies & Inputs

Inputs:
- Stage B requirements, constraints, scope baseline
- Stage A governance docs and any approved ADRs

---

## 8. Risks & Mitigation

| Risk ID | Description | Mitigation |
|--------:|-------------|------------|
| R-C-01 | Over-complex architecture | Prefer simplicity; document tradeoffs |
| R-004 | Scope creep | ADR required for major scope/structure changes |

---

## 9. Change Control

Any change to architectural principles or platform/tooling choices requires an ADR.

---

## 10. Stage Closure Rules

Stage C may be closed only when DoD is satisfied and acceptance tests pass.

---

## 11. Document Status

Status: Draft  
Owner: Project Governance  
Change control: ADR required
