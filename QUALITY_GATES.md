# QUALITY GATES

## 1. Document Purpose

This document defines the project's **quality governance model**:
- quality gates by stage,
- Definition of Done (DoD) expectations,
- Acceptance Tests (AT) structure,
- review and evidence rules,
- blockers and non-compliance handling.

This document is governance-only and does not include implementation instructions.

---

## 2. Quality Governance Principles

1. **Docs are evidence**
   - A deliverable is considered real only if it exists in Git.
2. **Explicit acceptance**
   - Each stage must define acceptance tests that can be objectively checked.
3. **No hidden work**
   - If a requirement, decision, or constraint is not recorded, it is not valid.
4. **Stage-by-stage control**
   - A stage may not start until the previous stage is closed.
5. **Change control protection**
   - Non-trivial changes require an ADR and updates to impacted documents.

---

## 3. Definitions

### 3.1 Definition of Done (DoD)

DoD is a **minimum completion standard** for a stage.

A stage is "Done" only if:
- all required deliverables exist,
- deliverables are linked from the Stage Brief,
- acceptance tests pass,
- change control was respected (ADR where required),
- blocking risks are addressed or explicitly accepted.

### 3.2 Acceptance Tests (AT)

Acceptance Tests are **stage-specific** checks written as:
- clear, objective statements,
- verifiable using Git artifacts,
- linked to deliverables.

AT naming convention:
- Stage-level: `AT-<STAGE><NUMBER>` (e.g., `AT-A1`, `AT-B2`)
- Cross-stage/global (rare): `AT-GLOBAL-<NUMBER>`

### 3.3 Quality Gates

Quality Gates are **mandatory checkpoints** that must be passed to:
- close the current stage,
- and/or start the next stage.

---

## 4. Evidence Rules

Evidence must be:
- stored in Git, or referenced by stable links recorded in Git,
- reviewable by someone without oral context,
- organized and linked from the relevant Stage Brief.

Allowed evidence formats:
- Markdown documents
- diagrams committed to repo (or referenced with stable links)
- structured checklists and logs

Not allowed as evidence:
- oral agreement
- “it works on my machine”
- unrecorded chat decisions

---

## 5. Global Minimum Quality Gate (All Stages)

This gate applies to every stage **A–I**.

### QG-0: Governance Compliance Gate

Pass criteria:
- all stage deliverables exist in Git,
- Stage Brief links to every deliverable,
- acceptance tests for the stage are defined and pass,
- no forbidden (out-of-scope) activity is present,
- any scope/tooling/lifecycle changes are covered by ADR.

Failing QG-0 is a **hard blocker**: stage cannot close.

---

## 6. Stage Quality Gates (A–I)

### Stage A — Foundation

Gate: **QG-A: Foundation Readiness**
Pass criteria:
- MASTER_PLAN.md exists and is coherent
- README.md provides repository navigation
- WORK_BREAKDOWN.md exists and matches stage model A–I
- QUALITY_GATES.md and RISK_REGISTER.md exist
- Stage Brief template and ADR template exist
- Stage Brief skeletons A–I exist
- AT-A1 and AT-A2 are defined and pass in STAGE_A.md

---

### Stage B — Discovery

Gate: **QG-B: Requirements Baseline**
Pass criteria:
- requirements are documented and testable
- constraints and assumptions are explicit
- scope baseline is recorded
- key references are captured
- risks updated
- acceptance tests AT-B* pass (as defined in STAGE_B.md)

---

### Stage C — Architecture

Gate: **QG-C: Architecture Integrity**
Pass criteria:
- architecture overview exists and is consistent
- key decisions captured as ADRs
- traceability to Stage B requirements exists
- risks updated
- AT-C* pass (as defined in STAGE_C.md)

---

### Stage D — UX/UI

Gate: **QG-D: Design Readiness**
Pass criteria:
- information architecture exists
- UX flows exist for primary journeys
- UI specs are coherent enough for build planning
- traceability to requirements exists
- risks updated
- AT-D* pass (as defined in STAGE_D.md)

---

### Stage E — Build Preparation

Gate: **QG-E: Execution Readiness**
Pass criteria:
- implementation plan exists (management-level)
- readiness checklist exists
- tooling/platform decisions are documented (ADR if required)
- risks updated
- AT-E* pass (as defined in STAGE_E.md)

---

### Stage F — Implementation

Gate: **QG-F: Implementation Completion**
Pass criteria:
- implementation tasks match the approved plan
- deviations are recorded and approved (ADR where required)
- evidence exists for test readiness
- risks updated if needed
- AT-F* pass (as defined in STAGE_F.md)

---

### Stage G — Testing

Gate: **QG-G: Release Readiness**
Pass criteria:
- test plan executed
- results and evidence recorded
- critical defects resolved or explicitly accepted
- go/no-go decision documented
- AT-G* pass (as defined in STAGE_G.md)

---

### Stage H — Release

Gate: **QG-H: Controlled Release**
Pass criteria:
- release checklist passed
- release notes exist
- handover docs exist
- deviations recorded and approved
- AT-H* pass (as defined in STAGE_H.md)

---

### Stage I — Closure

Gate: **QG-I: Formal Closure**
Pass criteria:
- closure report exists
- lessons learned recorded
- documentation completeness checklist passed
- repository is ready for archival/handover
- AT-I* pass (as defined in STAGE_I.md)

---

## 7. Blockers and Non-Compliance Handling

A stage is **blocked** if any of the following are true:
- a required deliverable is missing,
- acceptance tests are missing or fail,
- scope boundaries are violated,
- ADR-required change happened without an ADR,
- evidence is not reviewable from Git.

When blocked:
- the stage must not be closed,
- the next stage must not start,
- the blocker must be recorded in the relevant Stage Brief or governance log (as defined by the stage).

---

## 8. Change Control Impact

Changes to:
- quality gate criteria,
- definitions (DoD / AT),
- stage closure rules,

require an ADR and updates to:
- this document (QUALITY_GATES.md),
- affected Stage Brief(s),
- any dependent governance docs.

---

## 9. Document Status

Status: **Active**  
Owner: Project Governance  
Change control: **ADR required**
