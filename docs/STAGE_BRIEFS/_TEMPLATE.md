# STAGE <X> — <STAGE NAME>

## 1. Stage Purpose

This document defines the **scope, goals, and governance rules** for Stage <X>.

The purpose of this stage is to:
- clearly define what is in scope and out of scope,
- specify required deliverables,
- define acceptance criteria and completion rules,
- provide a single reference point for controlling this stage.

This document **does not** contain implementation instructions unless explicitly allowed by the stage definition.

---

## 2. Stage Position in Lifecycle

- Previous stage: <STAGE X-1>
- Next stage: <STAGE X+1>

This stage:
- may start only after the previous stage is formally closed,
- must be formally closed before the next stage may begin.

---

## 3. In-Scope

The following activities and outcomes are **explicitly allowed** in this stage:

- <List of allowed activities>
- <Types of documents or decisions produced>
- <Forms of analysis or design, if applicable>

Anything not listed here is considered **out of scope**.

---

## 4. Out-of-Scope (Explicit)

The following are **strictly forbidden** in this stage:

- <Implementation activities>
- <Environment changes>
- <Execution steps not approved for this stage>

If an activity is not explicitly allowed, it is forbidden by default.

---

## 5. Deliverables

The stage is expected to produce the following deliverables:

| ID | Deliverable | Description | Format |
|----|-------------|-------------|--------|
| D-X-01 | <Name> | <Short description> | <Markdown / Diagram / Other> |
| D-X-02 | <Name> | <Short description> | <Format> |

All deliverables must be:
- committed to Git,
- linked from this Stage Brief,
- reviewable without external context.

---

## 6. Quality Gates & Acceptance Criteria

### 6.1 Definition of Done (DoD)

This stage is considered **done** when:

- all listed deliverables exist,
- deliverables follow repository standards,
- scope boundaries are respected,
- required reviews are completed.

### 6.2 Acceptance Tests

| ID | Test | Description |
|----|------|-------------|
| AT-X-01 | Completeness | All deliverables are present and linked |
| AT-X-02 | Scope Control | No out-of-scope activity detected |
| AT-X-03 | Readability | Documents are clear and unambiguous |

---

## 7. Dependencies & Inputs

This stage depends on:

- deliverables from previous stages,
- approved ADRs,
- external references (if any, documented).

All inputs must be explicitly listed and linked.

---

## 8. Risks & Mitigation

| Risk ID | Description | Mitigation |
|--------:|-------------|------------|
| R-X-01 | <Risk description> | <Mitigation approach> |

Risks must align with the global `RISK_REGISTER.md`.

---

## 9. Change Control

Changes affecting:
- stage scope,
- deliverables,
- acceptance criteria

require an **ADR**.

Unrecorded changes are considered invalid.

---

## 10. Stage Closure Rules

This stage may be formally closed only when:

- Definition of Done is satisfied,
- all Acceptance Tests pass,
- no unresolved blocking risks remain,
- closure is recorded in Git.

---

## 11. Document Status

Status: **Draft / Active / Closed**  
Owner: Project Governance  
Change control: **ADR required**
