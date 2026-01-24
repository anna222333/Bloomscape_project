# STAGE BRIEF — E: Checkout & Payments

## Purpose
Deliver an end-to-end checkout demo using sandbox payments, EN/EUR locale, and worldwide shipping.

## Scope
- **In scope:** cart, checkout steps, shipping, and tax wiring at a minimal level.
- **Out of scope:** live payments or legal compliance reviews.

## Deliverables
- Test payment description and e2e checkout report.

## Definition of Done
- Test order completes successfully.
- Form validation errors communicated.
- Admin shows the test order data.

## Acceptance Tests
- AT-E1: Place a test order.
- AT-E2: Admin order view matches submission.
- AT-E3: Shipping configuration does not break checkout.

## Dependencies
- Depends on Stages D and B.

## Tasks
- E-01: Configure test payment method.
- E-02: Run checkout scenario.
- E-03: Document shipping/tax behavior.

## Risks
- R-003: Payment plugin instability.

## Handoff
Stage Chat E delivers scenario steps and results evidence.
