# ADR-001: AI Agent Team Workflow

- **Status:** Accepted
- **Date:** 2024-05-22
- **Decision Owner:** Architect
- **Stage:** A (Foundation / Restructuring)

## 1. Context
The project has shifted from a manual documentation execution model to an **AI-Agent driven experiment**. A custom application (`app.py`) has been introduced to facilitate interaction between four distinct roles: Architect, Foreman, Critic, and Orchestrator. We need to formalize how these agents interact to avoid chaos and ensure the Bloomscape clone is built effectively.

## 2. Decision
We define the following Responsibility Assignment Matrix (RACI) and workflow:

### Roles
1.  **ARCHITECT (Strategy & Governance):**
    *   Maintains `docs/MASTER_PLAN.md` and `docs/ADR/`.
    *   Defines technical standards and checks `docs/QUALITY_GATES.md`.
    *   Does NOT write implementation code.
    *   Output: Strategy docs, Stage Briefs updates.

2.  **FOREMAN (Implementation Design):**
    *   Translates Stage Briefs into concrete technical steps.
    *   Writes code (Python/PHP/JS), Docker configs, and bash commands.
    *   Output: Code blocks, shell commands for Orchestrator.

3.  **CRITIC (Quality & Security):**
    *   Reviews Foreman's proposed commands/code BEFORE execution.
    *   Checks against `docs/RISK_REGISTER.md` and security best practices.
    *   Output: Veto/Approve decisions, security warnings.

4.  **ORCHESTRATOR (Execution):**
    *   The "Hands". Executes approved commands via SSH on the VM.
    *   Manages git operations (sync logs, push changes).
    *   Output: Terminal logs, updated `logs/ssh_audit.log`.

### Workflow Loop
1.  **Architect** sets the Stage Brief in `docs/STAGE_BRIEFS/*_current.md`.
2.  **Foreman** reads the Brief and proposes a solution (Code + Commands).
3.  **Critic** verifies the solution (Security check).
4.  **Orchestrator** executes the command.
5.  **System** logs result to `HISTORY.log`.
6.  **Architect** reviews progress and updates Master Plan.

## 3. Consequences
*   **Positive:** Clear separation of concerns. The Architect doesn't get bogged down in syntax errors; the Foreman doesn't worry about long-term strategy.
*   **Negative:** Latency. Each step requires a context switch.
*   **Mitigation:** `app.py` is designed to provide shared context (Session State) to minimize hallucination.