# Project Documentation Repository

## Purpose of This Repository

This repository contains the **complete governance, planning, and documentation system**
for the project.

It is designed so that:
- the project can be understood without oral explanations,
- all decisions are traceable,
- all stages are governed through documents,
- execution is strictly separated from governance.

This repository is the **single Source of Truth (SoT)**.

---

## Repository Metadata (GitHub About)

Use the following values for the GitHub repository "About" section.

**Short description (About):**  
Docs-first governance repository for a Bloomscape-inspired WooCommerce skincare store case study (Stage A: Foundation).

**Website:**  
TBD (add later when a public demo exists)

**Topics:**  
`woocommerce`, `wordpress`, `ecommerce`, `case-study`, `documentation`, `governance`, `project-management`, `adr`, `quality-gates`

See also: `docs/REPO_METADATA.md`

Exports (snapshots): `docs/EXPORTS/`

## How to Read This Repository

If you are new to the project, follow this order:

1. **MASTER_PLAN.md**  
   High-level project lifecycle, stages, and governance principles.

2. **WORK_BREAKDOWN.md**  
   Structured decomposition of work into stages and packages.

3. **QUALITY_GATES.md**  
   Quality rules, acceptance criteria, and Definition of Done.

4. **RISK_REGISTER.md**  
   Identified risks and mitigation strategies.

5. **Stage Briefs**  
   Detailed scope and deliverables per stage.

---

## Repository Structure

```
/
├─ README.md
├─ MASTER_PLAN.md
├─ WORK_BREAKDOWN.md
├─ QUALITY_GATES.md
├─ RISK_REGISTER.md
└─ docs/
   ├─ STAGE_BRIEFS/
   │  ├─ _TEMPLATE.md
   │  ├─ STAGE_A.md
   │  ├─ STAGE_B.md
   │  ├─ STAGE_C.md
   │  ├─ STAGE_D.md
   │  ├─ STAGE_E.md
   │  ├─ STAGE_F.md
   │  ├─ STAGE_G.md
   │  ├─ STAGE_H.md
   │  └─ STAGE_I.md
   └─ ADR/
      └─ ADR-000_TEMPLATE.md
```

---

## Stage-Based Governance Model

The project is executed through **sequential stages (A–I)**.

Rules:
- Only one stage may be active at a time.
- A stage may start only after the previous stage is formally closed.
- Each stage is governed by a **Stage Brief** document.
- No implementation is allowed without an approved governing document.

---

## Change Control

All non-trivial decisions must be documented.

### Architecture Decision Records (ADR)

An ADR is required when:
- scope boundaries change,
- architectural principles change,
- tooling or platform choices change,
- stage structure or lifecycle changes.

ADR templates are located at:
```
docs/ADR/
```

Unrecorded decisions are considered **invalid**.

---

## What This Repository Does NOT Contain

This repository does **not** contain:
- source code,
- infrastructure configuration,
- deployment instructions,
- environment setup steps,
- content for the final product.

Any such content belongs to execution stages and their dedicated repositories or workspaces.

---

## Authority Statement

If there is a conflict between:
- chat messages,
- notes in external tools,
- personal interpretations,

the **Git documents in this repository always win**.

---

## Document Status

Status: **Active**  
Owner: Project Governance  
Change control: **ADR required**
