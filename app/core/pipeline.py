"""
Automated Foreman → Critic → Orchestrator Pipeline

Runs the full validation and execution cycle in a single synchronous chain,
eliminating manual button clicks between agents.

Flow:
  1. Extract bash command from Foreman response
  2. Critic: static rule-based validation (validators.py)
  3. Critic: AI review via Gemini
  4. If safe  → Orchestrator: execute via SSH, feed result back to Foreman
  5. If blocked → feed Critic report back to Foreman for revision
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Optional

from app.config import MODEL_PRO
from app.core.skill_engine import load_instruction
from app.core.validators import validate_bash_command
from app.core.ssh_executor import execute_ssh
from app.core.context_builder import get_project_context


# ---------------------------------------------------------------------------
# Result dataclass
# ---------------------------------------------------------------------------

@dataclass
class PipelineResult:
    """Immutable result carried through the Foreman→Critic→Orchestrator run."""

    command: str
    validator_report: str = ""
    ai_critic_report: str = ""
    is_blocked: bool = False
    execution_output: Optional[str] = None
    error: Optional[str] = None

    @property
    def full_critic_report(self) -> str:
        """Combined static + AI critic report."""
        if self.ai_critic_report:
            return f"{self.validator_report}\n\n---\n**AI Анализ:**\n{self.ai_critic_report}"
        return self.validator_report

    @property
    def success(self) -> bool:
        """True when command was executed without known errors."""
        return (
            not self.is_blocked
            and self.execution_output is not None
            and not (self.execution_output or "").startswith("❌")
            and self.error is None
        )

    @property
    def status_emoji(self) -> str:
        if self.error:
            return "❌"
        if self.is_blocked:
            return "⛔"
        if self.success:
            return "✅"
        return "⚠️"

    def foreman_feedback(self) -> str:
        """Message to inject into Foreman history as follow-up context."""
        if self.is_blocked:
            return (
                f"КРИТИК ЗАБЛОКИРОВАЛ КОМАНДУ `{self.command}`.\n\n"
                f"{self.full_critic_report}\n\n"
                "Пожалуйста, предложи исправленный вариант или альтернативный подход."
            )
        if self.error:
            return (
                f"ОШИБКА ПАЙПЛАЙНА для `{self.command}`:\n{self.error}\n\n"
                "Предложи исправленный вариант."
            )
        return (
            f"РЕЗУЛЬТАТ ВЫПОЛНЕНИЯ `{self.command}`:\n"
            f"```\n{self.execution_output}\n```"
        )


# ---------------------------------------------------------------------------
# Critic verdict parsing
# ---------------------------------------------------------------------------

# Primary mechanism: Critic must end its reply with [BLOCK] or [ALLOW].
# Keyword list is kept only as a fallback when neither tag is present
# (e.g. old instructions, network hiccups, truncated response).
_BLOCK_KEYWORDS = (
    "блокирую", "запрещено", "не рекомендую", "недопустимо",
    "требует доработки", "опасно", "вето",
    "blocked", "dangerous", "forbidden", "deny", "unsafe", "reject",
)


def _ai_wants_block(ai_report: str) -> bool:
    """Return True when Critic's response signals the command should be blocked.

    Decision priority:
      1. Explicit [BLOCK] / [ALLOW] tag (reliable, parseable)
      2. Keyword scan of the full response (fallback for untagged replies)
    """
    if "[BLOCK]" in ai_report:
        return True
    if "[ALLOW]" in ai_report:
        return False
    # Fallback: scan for blocking keywords
    lower = ai_report.lower()
    return any(kw in lower for kw in _BLOCK_KEYWORDS)


# ---------------------------------------------------------------------------
# Core pipeline function
# ---------------------------------------------------------------------------

def run_pipeline(
    bash_command: str,
    call_gemini_fn: Callable,
    skill_manager,
    credentials,
    oslogin_service,
    exec_timeout: int = 120,
    on_step: Optional[Callable[[str], None]] = None,
) -> PipelineResult:
    """
    Run the full Foreman → Critic → Orchestrator pipeline for *bash_command*.

    Args:
        bash_command:    Shell command produced by Foreman.
        call_gemini_fn:  LLM call function from streamlit_app (avoids circular import).
        skill_manager:   SkillManager instance (may be None).
        credentials:     GCP credentials.
        oslogin_service: OS Login service.
        exec_timeout:    SSH execution timeout in seconds.
        on_step:         Optional callback invoked with a status string before each
                         pipeline step — used to feed st.status.write() from the UI
                         without importing Streamlit inside this module.

    Returns:
        PipelineResult with all intermediate results and final output.
    """
    def _step(msg: str) -> None:
        if on_step:
            on_step(msg)
    try:
        # ── Step 1: Static validation (Critic) ─────────────────────────────
        _step("🔎 Шаг 1/3 — статический анализ команды...")
        is_safe, validator_report = validate_bash_command(bash_command)

        # ── Step 2: AI Critic review ────────────────────────────────────────
        _step("🤔 Шаг 2/3 — Критик анализирует команду...")
        context = get_project_context()
        critic_prompt = (
            f"АНАЛИЗ КОМАНДЫ: {bash_command}\n\n"
            f"ОТЧЕТ ВАЛИДАТОРА: {validator_report}\n\n"
            f"КОНТЕКСТ ПРОЕКТА:\n{context}"
        )
        ai_report = call_gemini_fn(
            MODEL_PRO,
            critic_prompt,
            load_instruction("critic", skill_manager),
        )

        is_blocked = (not is_safe) or _ai_wants_block(ai_report)

        result = PipelineResult(
            command=bash_command,
            validator_report=validator_report,
            ai_critic_report=ai_report,
            is_blocked=is_blocked,
        )

        if is_blocked:
            _step("⛔ Критик заблокировал команду.")
            return result

        # ── Step 3: Execute in Orchestrator ────────────────────────────────
        _step("🚀 Шаг 3/3 — Оркестратор выполняет команду...")
        output = execute_ssh(bash_command, credentials, oslogin_service, exec_timeout=exec_timeout)
        result.execution_output = output
        return result

    except Exception as exc:
        _step(f"❌ Ошибка пайплайна: {exc}")
        return PipelineResult(
            command=bash_command,
            error=str(exc),
        )
