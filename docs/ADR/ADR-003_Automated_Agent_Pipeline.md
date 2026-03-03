# ADR-003: Automated Agent Pipeline (Foreman → Critic → Orchestrator)

- **Status:** Accepted
- **Date:** 2026-03-03
- **Decision Owner:** Architect
- **Stage:** B (Post-Refactoring / Automation)
- **Related:**
  - Previous ADR: ADR-001_AI_Team_Workflow.md (§2.2 Workflow Loop — superseded in part)
  - Source modules: `app/core/pipeline.py`, `app/ui/components.py`
  - Instructions: `docs/INSTRUCTIONS/critic.txt`

---

## 1. Context

ADR-001 defined the agent workflow as a **manual loop**: Foreman generates a bash command → user clicks "⚖️ Критику" → Critic reviews → user clicks "✅ Approve" → Orchestrator executes.

This model has three operational bottlenecks:

1. **Every pipeline step requires a manual button click.** For iterative tasks (e.g. deploying a service in multiple steps), this creates significant friction and cognitive load.
2. **The Critic's verdict was inferred from free-form LLM text** using a keyword list (`_BLOCK_KEYWORDS`). This was brittle: phrases like "команда выглядит рискованно" or "не рекомендую" would not trigger a block, because neither phrase matched any keyword.
3. **The entire pipeline ran under a single `st.spinner`** with no intermediate progress signal. Users had no visibility into which step was executing during a 30–60 second wait.

A decision was needed on how to automate the pipeline while preserving the Critic's authority and maintaining user observability.

---

## 2. Decision Drivers

- **Reduced manual overhead** — allow the user to delegate repetitive multi-step execution to the agent chain
- **Deterministic Critic verdict** — LLM free-text is unreliable as a boolean signal; a structured output is needed
- **Observability** — the user must be able to see which agent is working at any given moment
- **Backward compatibility** — manual mode (individual buttons) must continue to work unchanged
- **No circular imports** — `pipeline.py` must not import `streamlit`; Streamlit state must stay in `components.py`

---

## 3. Considered Options

### Option A — Button-based flow (status quo)
- Summary: Keep manual "Send to Critic" / "Approve" buttons; no automation.
- Pros: Simple, already implemented, fully user-controlled.
- Cons: Unusable for multi-step autonomous tasks; every step requires user presence.
- Risks: Blocks future autonomous/agentic work.

### Option B — Fully automatic, no toggle
- Summary: Every Foreman bash-code response is automatically sent through the pipeline.
- Pros: Zero manual clicks.
- Cons: User cannot opt out; unexpected executions possible; hard to debug.
- Risks: Unsafe for exploratory or draft commands.

### Option C — Opt-in toggle + structured Critic verdict (chosen)
- Summary: A UI toggle `⚡ Авто-пайплайн` enables the automatic chain. The Critic is required to end its response with `[BLOCK]` or `[ALLOW]`. Progress is reported step-by-step via `st.status`.
- Pros: User retains full control via toggle; Critic verdict is unambiguous; observability is high; backward compatible.
- Cons: Requires updating `docs/INSTRUCTIONS/critic.txt`; adds `on_step` callback pattern to `run_pipeline()`.
- Risks: If Critic instruction is not loaded (missing file), keyword fallback activates — acceptable degradation.

---

## 4. Decision

**We decided to implement Option C.**

### 4.1 New module: `app/core/pipeline.py`

A standalone, Streamlit-free module encapsulating the full automated chain:

```
run_pipeline(bash_command, call_gemini_fn, skill_manager,
             credentials, oslogin_service, exec_timeout, on_step)
    │
    ├── Step 1: validate_bash_command()        ← static analysis (shellcheck + bashlex)
    │           on_step("🔎 Шаг 1/3 — статический анализ...")
    │
    ├── Step 2: call_gemini_fn(critic prompt)  ← AI review
    │           on_step("🤔 Шаг 2/3 — Критик анализирует...")
    │           _ai_wants_block(ai_report) → checks [BLOCK]/[ALLOW] tag first,
    │                                         falls back to keyword scan
    │   is_blocked=True  → on_step("⛔ Заблокировано") → return PipelineResult
    │
    └── Step 3: execute_ssh()                  ← SSH execution
                on_step("🚀 Шаг 3/3 — Оркестратор выполняет...")
                → return PipelineResult(execution_output=...)
```

`on_step` is an optional `Callable[[str], None]` injected from the UI layer (`_status.write`), keeping Streamlit out of `core/`.

**`PipelineResult` dataclass fields:**

| Field | Type | Description |
|-------|------|-------------|
| `command` | `str` | The bash command that ran through the pipeline |
| `validator_report` | `str` | Output from static analysis |
| `ai_critic_report` | `str` | Full LLM response from the Critic |
| `is_blocked` | `bool` | True if Critic or validator blocked the command |
| `execution_output` | `Optional[str]` | SSH stdout/stderr (None if blocked or error) |
| `error` | `Optional[str]` | Exception message if pipeline itself failed |

Computed properties: `full_critic_report`, `success`, `status_emoji`, `foreman_feedback()`.

### 4.2 Critic verdict: structured tags

**`docs/INSTRUCTIONS/critic.txt`** now requires the Critic to end every response with exactly one tag on a separate line:

```
[BLOCK]  — command is unsafe, violates rules, or requires revision
[ALLOW]  — command is safe and approved for execution
```

**`_ai_wants_block()` decision priority:**
1. `[BLOCK]` present in response → block (reliable)
2. `[ALLOW]` present in response → allow (reliable)
3. Neither tag → keyword scan of full response (fallback for missing/truncated instructions)

Keyword list expanded to include: `"не рекомендую"`, `"недопустимо"`, `"требует доработки"`, `"unsafe"`, `"reject"`.

### 4.3 UI changes in `app/ui/components.py`

**Foreman column:**
- Added `st.toggle("⚡ Авто-пайплайн …")` above the chat input. State stored in `st.session_state.pipeline_auto`.
- When toggle is ON and Foreman response contains a ```` ```bash ``` ```` block: `run_pipeline()` is called automatically.
- On completion: `PipelineResult` is appended to `st.session_state.pipeline_results`; `pipeline_result.foreman_feedback()` is injected into `foreman_history` so the LLM can react on the next turn.
- Single `st.spinner` replaced by **`st.status(expanded=True)`** — updates label and `state` (`"complete"` / `"error"`) upon completion.

**Orchestrator column:**
- New expander **"⚡ Авто-пайплайн — N запусков"** shows a structured log of every pipeline run: command, Critic report (collapsible), execution output or block reason.
- "🗑️ Очистить лог пайплайна" button clears `pipeline_results` without affecting SSH log.
- SSH log container height reduced from 400px → 300px to accommodate the pipeline log above it.

**Session state additions** (initialized in `init_session_state()`):

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `pipeline_auto` | `bool` | `False` | Toggle state |
| `pipeline_results` | `list[dict]` | `[]` | Log of all pipeline runs this session |

### 4.4 Manual mode unchanged

The "⚖️ Критику" and "🚀 В Оркестратор" buttons on each Foreman message remain fully functional and unaffected by the toggle state.

---

## 5. Consequences

### Positive
- Multi-step tasks can be executed without manual intervention at each step.
- Critic verdict is unambiguous — boolean, not inferred from prose.
- User sees real-time step progress instead of a frozen spinner.
- `pipeline.py` is independently testable (no Streamlit dependency).
- `PipelineResult.foreman_feedback()` closes the loop: Foreman receives execution results automatically, enabling iterative autonomous work.
- Backward compatible: toggle default is `False`; existing manual workflow unchanged.

### Negative
- When `pipeline_auto=True`, a bash command in Foreman's response is **executed without user confirmation**. Requires user awareness of the toggle state.
- Two sequential Gemini (MODEL_PRO) calls + SSH execution per pipeline run ≈ 20–60 seconds total latency.
- `PipelineResult` log is session-only (not persisted to `chat_history.json`).

### Mitigations
- `is_cmd_blocked` safety: static validator (`validate_bash_command`) runs before the LLM Critic — known-dangerous commands (rm -rf, mkfs, dd) are caught before spending tokens.
- `st.status` with intermediate step labels provides the user a clear signal that work is in progress and at which stage.
- Toggle is opt-in and its state is visible in the UI at all times above the Foreman input.

---

## 6. Validation

- **Criterion 1:** A bash command sent through `run_pipeline()` with `[BLOCK]` in Critic response must set `PipelineResult.is_blocked = True` and must not call `execute_ssh()`.
- **Criterion 2:** A bash command sent through `run_pipeline()` with `[ALLOW]` in Critic response and `is_safe=True` from validator must call `execute_ssh()` and populate `execution_output`.
- **Criterion 3:** `_ai_wants_block()` must return `False` when LLM responds "команда выглядит рискованно" without `[BLOCK]` tag (keyword fallback must not match ambiguous phrasing — confirm by expanding keyword list conservatively).
- **Criterion 4:** `st.status` must display at least 3 intermediate labels before reaching final state.
- **Rollback:** Toggle to `False`; pipeline module can be removed without affecting `components.py` (import is isolated to the toggle-active code path).

---

## 7. Change Control

Files changed by this ADR:

| File | Change type |
|------|-------------|
| `app/core/pipeline.py` | **Created** — new module |
| `app/ui/components.py` | **Modified** — toggle, `st.status`, pipeline log in Orchestrator, session state |
| `docs/INSTRUCTIONS/critic.txt` | **Modified** — added mandatory `[BLOCK]`/`[ALLOW]` verdict section |

Related documents that may need review following this decision:
- `docs/ADR/ADR-001_AI_Team_Workflow.md` §2.2 — the workflow loop is now optionally automated; no contradiction, but §2.2 should be noted as partial in future revision.
- `docs/RISK_REGISTER.md` — new risk: uncontrolled execution when `pipeline_auto=True` (mitigated by toggle default and static validator).

---

## 8. Notes

- The `on_step` callback pattern was chosen over a generator/async approach to remain compatible with Streamlit's synchronous execution model.
- `call_gemini_fn` is passed into `run_pipeline()` as a parameter (not imported) to avoid circular imports: `components.py` → `pipeline.py` → `streamlit_app.py` would create a cycle.
- Future extension point: `run_pipeline()` signature already supports adding an `arch_review: bool` parameter (Step 4 — Architect post-execution review) without breaking existing callers.
