# MASTER PLAN — Bloomscape AI Experiment

## Purpose
Build a pixel-perfect, reproducible WooCommerce storefront inspired by Bloomscape, **entirely driven by a team of AI Agents** (Architect, Foreman, Critic, Orchestrator) via a custom control interface (`app.py`).

## Core Goal
Prove that a coordinated multi-agent system can go from "Abstract Requirement" to "Deployed E-commerce Store" with minimal human intervention.

## Strategy: The "Refined Waterfall"
We follow a strict staged approach. We do not jump to coding until requirements are clear.

### Phase 1: Foundation & Definition (Current)
*   **Stage A: Foundation.** (Done) Repo structure, Git flow, Team Roles (ADR-001).
*   **Stage B: Discovery.** (Active) Defining the "What". Parsing the Bloomscape reference, defining the catalog structure, UX requirements, and technical constraints. **Output:** `docs/DISCOVERY/` artifacts.

### Phase 2: Infrastructure & Core
*   **Stage C: Platform Baseline.** Dockerizing WordPress + MySQL + Redis. Ensuring the "Foreman" can boot the stack via code.
*   **Stage D: Architecture & Theme.** Creating the child theme structure. Implementing the "Headless-feel" within a monolithic WP structure.

### Phase 3: Content & Commerce
*   **Stage E: Catalog Injection.** Programmatic creation of products, categories, and attributes (matches Bloomscape data model).
*   **Stage F: Checkout & Logic.** Customizing the cart/checkout flow to match the reference UX.

### Phase 4: Production & Handover
*   **Stage G: Operations.** Backups, Logging, Security Hardening.
*   **Stage H: Final Polish.** QA, UI Tweaks, Documentation finalization.

## Current State: STAGE B (Discovery)
We are currently "thinking before doing". The Foreman needs to analyze the reference site and map out the data structures before writing PHP.

## Rules of Engagement
1.  **Docs First:** No code is written without a corresponding requirement in `docs/DISCOVERY/` or a task in the Stage Brief.
2.  **No Manual GUI:** All configurations must be applied via CLI (WP-CLI) or file injection. We treat the WP Admin Panel as "Read Only" for verification.
3.  **Evidence:** Every successful step must be logged in `HISTORY.log`.