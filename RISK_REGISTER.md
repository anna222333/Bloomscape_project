# RISK REGISTER

## 1. Document Purpose

This document is the project's **single Source of Truth (SoT)** for risk governance.

It:
- records risks, owners, triggers, and mitigations,
- defines review cadence by stage,
- supports quality gates and change control.

This document is governance-only and contains no implementation instructions.

---

## 2. Risk Management Rules

### 2.1 Risk IDs and Naming
Risk ID format:
- Global risks: `R-###` (e.g., `R-004`)
- Stage-specific risks (optional): `R-<STAGE>-##` (e.g., `R-B-01`)

### 2.2 Risk Fields (Minimum Set)
Each risk must define:
- description and impact,
- likelihood (L) and impact severity (I),
- risk score = L × I,
- triggers / early warning signals,
- mitigations (preventive) and contingency (reactive),
- owner role,
- status.

### 2.3 Scales
Likelihood (L): 1–5  
Impact (I): 1–5  
Score: 1–25

Interpretation:
- 1–6: Low
- 7–14: Medium
- 15–25: High

### 2.4 Review Cadence
- Reviewed at the start and closure of every stage.
- Any risk scored **≥ 15** must be explicitly addressed before closing the stage (via mitigation evidence or documented acceptance).

---

## 3. Risk Register (Active)

| ID | Risk | L | I | Score | Triggers / Early Signals | Mitigation (Preventive) | Contingency (Reactive) | Owner | Status |
|----|------|---:|---:|-----:|--------------------------|--------------------------|------------------------|-------|--------|
| R-001 | Requirements ambiguity leads to rework | 4 | 4 | 16 | Conflicting statements; inability to write testable requirements; frequent reinterpretations | Enforce Stage B acceptance tests; require traceable, testable requirement language | Pause downstream stages; create ADR to clarify scope baseline | Product/Project Owner | Active |
| R-002 | Decision drift (unrecorded decisions) | 4 | 4 | 16 | “We decided in chat”; undocumented tool/platform choices; inconsistent docs | ADR required for non-trivial changes; SoT rule enforced (Git only) | Block stage closure until decision is recorded; create corrective ADR | Project Governance | Active |
| R-003 | Incomplete documentation blocks handover | 3 | 4 | 12 | Missing links; unclear stage outputs; deliverables not discoverable from Stage Briefs | README navigation; Stage Brief deliverables tables; Quality Gates enforcement | Add documentation backlog; block next stage start until fixed | Project Governance | Active |
| R-004 | Scope creep (governance slipping into execution) | 5 | 5 | 25 | Requests for CLI steps; environment changes; “just implement quickly”; adding deliverables without approval | Strict allowed/forbidden rules; default-forbidden principle; ADR required for scope changes; iteration-level checks | Hard block: stop work and raise ADR request; revert/avoid scope-expanding changes | Project Governance | Active |
| R-005 | Reference/design mismatch creates inconsistent UX | 3 | 3 | 9 | Multiple conflicting references; unclear design system; inconsistent IA | Stage D traceability to requirements; explicit IA + UI rules | Freeze design changes; document conflicts and resolve via ADR | UX Owner | Active |
| R-006 | Tooling/platform choice changes late | 3 | 5 | 15 | New constraints discovered; performance/security concerns; vendor limits | Make key choices in Stage C/E with ADR; document constraints early in Stage B | Re-plan Stage E/F; record decision reversal via superseding ADR | Technical Owner | Active |
| R-007 | Quality gates bypassed due to schedule pressure | 4 | 4 | 16 | “Ship now”; missing AT evidence; stage closure without deliverables | QG-0 Governance Compliance Gate; explicit blockers; enforce closure rules | Block release; require remediation package; document exception via ADR | Project Governance | Active |
| R-008 | Stakeholder alignment risk (success criteria unclear) | 3 | 4 | 12 | Vague goals; shifting priorities; disagreements on “done” | Stage B: define success metrics and scope baseline; record decisions in Git | Run alignment review; document changes via ADR | Product/Project Owner | Active |
| R-009 | Repo bloat from storing evidence (screenshots/media) in Git | Med | Med | Med | Prefer compressed images; limit count; store only necessary evidence paths in reports; document exceptions | Repo size grows quickly; slow clones/PRs | Stage H / Maintainer |

---

## 4. Risk Acceptance Rules

Risk acceptance (choosing to proceed despite risk) requires:
- explicit statement of what is accepted and why,
- recorded owner and time horizon,
- recorded compensating controls (if any),
- (if acceptance affects scope or quality gates) an ADR.

Unrecorded risk acceptance is invalid.

---

## 5. Linkage to Governance

This register supports:
- `QUALITY_GATES.md` (blockers and closure criteria),
- Stage Briefs (stage risks section),
- ADRs (decision risks and tradeoffs).

---

## 6. Document Status

Status: **Active**  
Owner: Project Governance  
Change control: **ADR required**
