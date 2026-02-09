# MASTER PLAN

## 1. Document Purpose

This document defines the **master governance and planning framework** for the project.

Its purpose is to:
- describe the overall project structure and lifecycle,
- define stages and their intent,
- act as the top-level Source of Truth for planning,
- provide navigation to all governance and execution documents.

This document **does not** contain implementation details, technical instructions, or execution steps.

---

## 2. Source of Truth (SoT)

The single Source of Truth for this project is the **Git repository** and its Markdown documents.

Rules:
- If a statement is not recorded in Git, it is not considered valid.
- External tools (Notion, AppFlowy, diagrams, chats) are **supporting tools only**.
- This document is authoritative over all stage-level plans.

## Authoritative Paths (Source of Truth)
- **Authoritative (SoT): repo root** for core governance docs:
  - `MASTER_PLAN.md`, `WORK_BREAKDOWN.md`, `QUALITY_GATES.md`, `RISK_REGISTER.md`, `README.md`
- `/docs/*` may contain mirrors or supporting materials, but **root is authoritative** unless an ADR states otherwise.
- Stage Briefs: **authoritative naming scheme must be single-source** (see note in `docs/STAGE_BRIEFS/`).

## Repository Structure (operational)
- Root (authoritative governance SoT):
  - `MASTER_PLAN.md`, `WORK_BREAKDOWN.md`, `QUALITY_GATES.md`, `RISK_REGISTER.md`, `README.md`, `CONTRIBUTING.md`
- `/docs/` (supporting materials):
  - `docs/STAGE_BRIEFS/` — stage briefs (authoritative naming scheme documented; avoid drift per QG-DOC1)
  - `docs/DISCOVERY/` — Stage B baseline capture (environment, persistence, WP, Woo)
  - `docs/EXPORTS/` — snapshots/evidence exports (when used)
  - `docs/INSTRUCTIONS/` — stage chat instruction packets
  - `docs/ADR/` — architecture decisions
  - `docs/REPORTS/` — stage reports (one per stage when applicable)

---

## 3. Project Lifecycle Overview

The project lifecycle is divided into **nine sequential stages**:

| Stage | Name        | Purpose (High-level) |
|------:|------------|----------------------|
| A | Foundation | Governance, documentation, rules, templates |
| B | Discovery | Requirements, references, constraints |
| C | Architecture | System and solution design |
| D | UX/UI | Information architecture and design |
| E | Build Prep | Technical preparation before build |
| F | Implementation | Controlled execution |
| G | Testing | Validation and quality assurance |
| H | Release | Deployment and handover |
| I | Closure | Final review and documentation |

Each stage:
- has a dedicated **Stage Brief**,
- produces explicit deliverables,
- has defined acceptance criteria.

- - - -

## Milestones

- **M0:** Governance baseline in main (SoT=root, QG-DOC1 active, Stage B kickoff pack present)

---

---

## 4. Stage Control Principles

1. **Sequential execution**  
   A stage may start only when the previous stage is formally closed.

2. **Docs-first governance**  
   No execution is allowed unless the governing documents exist and are approved.

3. **Change Control mandatory**  
   Any deviation from approved plans requires an ADR.

4. **No implicit decisions**  
   Decisions must be recorded explicitly in Git documents.

---

## 5. Change Control & ADR

### 5.1 When an ADR is Required

An Architecture Decision Record (ADR) is required when:
- scope boundaries change,
- architectural principles change,
- tooling or platform choices change,
- stage structure or lifecycle changes.

### 5.2 ADR Authority

- ADRs are binding once approved.
- An unrecorded decision is considered **non-existent**.

ADR templates are located in:
```
docs/ADR/
```

## 5.3 Change Control Policy (Operational Rules)

These rules define **how changes are proposed, evaluated, and recorded**.

### 5.3.1 Default Rule

If a change is not explicitly approved and recorded, it is **not allowed**.

### 5.3.2 ADR Triggers (ADR Required)

An ADR is mandatory if the change affects any of the following:

- **Scope boundaries** (what is in/out of scope for the project or a stage)
- **Stage model** (stages A–I, sequencing, stage entry/exit rules)
- **Deliverables** (adding/removing/renaming deliverables that change stage outputs)
- **Architecture principles** (structure, integrations, major design choices)
- **Tooling / platform choices** (hosting, WordPress/WooCommerce setup approach, CI/CD, major plugins/theme strategy)
- **Quality model** (DoD, Acceptance Tests, Quality Gates, stage closure rules)
- **Risk model** (risk acceptance rules, high-risk thresholds, mitigation commitments)

### 5.3.3 Change Submission Requirements

Every proposed change must include:
- a clear description of what changes and why,
- expected impact on deliverables and stages,
- risks introduced or changed (reference `RISK_REGISTER.md`),
- documents that must be updated if the change is accepted.

### 5.3.4 Decision Outcomes

A change proposal results in one of the following:
- **Accepted** (recorded as ADR; dependent documents updated)
- **Rejected** (reason recorded; no changes applied)
- **Deferred** (recorded with conditions and revisit criteria)

### 5.3.5 Consistency Update Rule (Hard Requirement)

If an ADR is accepted, all impacted documents must be updated in the same change set, at minimum:
- `MASTER_PLAN.md`
- `WORK_BREAKDOWN.md`
- relevant `docs/STAGE_BRIEFS/STAGE_<X>.md`
- `QUALITY_GATES.md` (if quality rules are impacted)
- `RISK_REGISTER.md` (if risk profile changes)

### 5.3.6 No Silent Overrides

No document may silently override another.
If a conflict exists, it must be resolved via:
- a superseding ADR, and
- explicit updates to conflicting documents.

### 5.3.7 Where ADRs Live

ADR files are stored under:
- `docs/ADR/`

Use the template:
- `docs/ADR/ADR-000_TEMPLATE.md`

---

## 6. Quality & Acceptance

Quality control is enforced via:
- Definition of Done (DoD) per stage,
- Acceptance Tests (AT) per stage,
- Explicit Quality Gates.

The authoritative quality rules are defined in:
```
QUALITY_GATES.md
```

---

## 7. Risk Governance

Project risks are:
- explicitly identified,
- tracked,
- reviewed per stage.

The authoritative risk register is:
```
RISK_REGISTER.md
```

---

## 8. Navigation

Primary documents:
- `README.md` — repository navigation
- `WORK_BREAKDOWN.md` — stage-level work packages
- `QUALITY_GATES.md` — acceptance and quality rules
- `RISK_REGISTER.md` — risk tracking

Stage-specific documents:
```
docs/STAGE_BRIEFS/
```

---

## 9. Scope Boundary Statement

This Master Plan:
- defines **what is governed**, not **how it is executed**,
- does **not** authorize implementation,
- does **not** replace stage briefs.

Any attempt to derive execution steps directly from this document is a **scope violation**.

---

## 10. Document Status

Status: **Active**  
Owner: Project Governance  
Change control: **ADR required**
