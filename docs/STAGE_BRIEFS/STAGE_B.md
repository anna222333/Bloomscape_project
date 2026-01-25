# STAGE B — DISCOVERY

## 1. Stage Purpose

Define the project discovery outputs:
- goals and success criteria,
- functional and non-functional requirements,
- constraints and assumptions,
- reference and competitor analysis (if applicable),
- scope baseline for downstream stages.

Stage B produces **documents and decisions**, not implementation.

---

## 2. Stage Position in Lifecycle

- Previous stage: Stage A — Foundation
- Next stage: Stage C — Architecture

---

## 3. In-Scope

- Requirements definition (functional / non-functional).
- Constraints and assumptions documentation.
- Reference analysis and inspiration capture (documented and traceable).
- Establish scope baseline and boundaries for later stages.
- Identify discovery-stage risks and update the global risk register.

---

## 4. Out-of-Scope (Explicit)

- Any environment changes.
- Any implementation, configuration, or deployment.
- Any build actions (themes/plugins setup, server setup).
- Any content production beyond discovery documentation needs.

---

## 5. Deliverables

| ID | Deliverable | Description | Format |
|----|-------------|-------------|--------|
| D-B-01 | Requirements set | Functional and non-functional requirements | Markdown |
| D-B-02 | Constraints & assumptions | Documented constraints and assumptions | Markdown |
| D-B-03 | References | Reference capture and analysis | Markdown |
| D-B-04 | Updated risk register | Discovery risks added/updated | Markdown |
| D-B-05 | Updated plan links | Updates to navigation where needed | Markdown |

(Exact file paths to be defined in Stage B execution, under Change Control.)

---

## 6. Quality Gates & Acceptance Criteria

### 6.1 Definition of Done (DoD)

Stage B is done when:
- requirements are complete, unambiguous, and traceable,
- constraints and assumptions are explicit,
- scope baseline is recorded,
- relevant risks are updated,
- outputs are committed to Git and linked.

### 6.2 Acceptance Tests

| ID | Test | Description |
|----|------|-------------|
| AT-B1 | Completeness | Required deliverables exist and are linked |
| AT-B2 | Clarity | Requirements are testable and non-contradictory |
| AT-B3 | Scope Baseline | Clear boundaries exist for Stage C/D planning |

---

## 7. Dependencies & Inputs

Inputs:
- Stage A governance docs (MASTER_PLAN, WBS, Quality Gates, Risk Register)
- Any approved ADRs

---

## 8. Risks & Mitigation

| Risk ID | Description | Mitigation |
|--------:|-------------|------------|
| R-B-01 | Requirements ambiguity | Use acceptance tests; require traceable statements |
| R-004 | Scope creep | Enforce out-of-scope; ADR required for boundary changes |

---

## 9. Change Control

Changes to:
- scope baseline,
- requirements priorities that affect architecture,
require an ADR.

---

## 10. Stage Closure Rules

Stage B may be closed only when:
- DoD is satisfied,
- acceptance tests pass,
- all outputs are committed and linked.

---

## 11. Document Status

Status: Draft  
Owner: Project Governance  
Change control: ADR required
