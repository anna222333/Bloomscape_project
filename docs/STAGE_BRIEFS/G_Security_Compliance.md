# STAGE BRIEF — G: Security & Compliance

## Purpose
Establish a security baseline covering secrets, access, and hardening checklists.

## Scope
- **In scope:** least-privilege, secrets handling, updates/assessments.
- **Out of scope:** formal certification programs.

## Deliverables
- Secrets handling rules, role matrix, hardening checklist, and evidence.

## Definition of Done
- No secrets stored in Git.
- Roles documented and aligned to least privilege.
- Hardening checklist executed and recorded.

## Acceptance Tests
- AT-G1: Repository scans return no secrets.
- AT-G2: Roles align with least-privilege expectations.

## Dependencies
- Depends on Stage B and partially Stage F for logs/controls.

## Tasks
- G-01: Document secrets policy.
- G-02: Define role matrix.
- G-03: Run hardening checklist.

## Risks
- R-006: Secrets leakage.

## Handoff
Stage Chat G hands over checklist with confirmations and evidence.
