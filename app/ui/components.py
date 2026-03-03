"""
Streamlit Component Functions

Declarative UI components for Bloom Control Center.
Each function handles rendering and interaction for a specific agent column.
"""

import streamlit as st
from app.config import MODEL_PRO, MODEL_FLASH
from app.core.ssh_executor import execute_ssh, upload_to_vm
from app.core.git_manager import git_local_commit, git_push_to_github, git_sync_logs_only
from app.core.skill_engine import load_instruction, search_skills
from app.core.context_builder import get_project_context, get_architect_context
from app.core.validators import validate_bash_command
from app.core.chat_history_manager import load_history, save_history
from app.core.pipeline import run_pipeline, PipelineResult


# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================

def init_session_state():
    """
    Initialize all session state variables at application startup.
    This function is called once per page load to ensure all required keys exist.
    Persistent histories (arch, foreman, orch) are loaded from chat_history.json
    on the very first Streamlit script run of each browser session.
    """
    # Load persisted histories once per session (only when keys are absent)
    _history_keys = ("arch_history", "foreman_history", "orch_history")
    if any(k not in st.session_state for k in _history_keys):
        saved = load_history()
        for key in _history_keys:
            if key not in st.session_state:
                st.session_state[key] = saved.get(key, [])

    # Critic has no persistent history (review state is ephemeral)
    if "critic_history" not in st.session_state:
        st.session_state.critic_history = []
    
    # Initialize command review state
    if "pending_cmd" not in st.session_state:
        st.session_state.pending_cmd = None
    
    if "critic_report" not in st.session_state:
        st.session_state.critic_report = None
    
    if "is_cmd_blocked" not in st.session_state:
        st.session_state.is_cmd_blocked = False
    
    # Initialize skill search results
    if "last_cli_output_search" not in st.session_state:
        st.session_state.last_cli_output_search = ""
    
    if "last_cli_output_install" not in st.session_state:
        st.session_state.last_cli_output_install = ""
    
    # Initialize architect inbox
    if "arch_inbox" not in st.session_state:
        st.session_state.arch_inbox = None
    
    # Initialize manual critiques input
    if "crit_manual" not in st.session_state:
        st.session_state.crit_manual = ""
    
    # Initialize SSH and network configuration
    if "ssh_private_key" not in st.session_state:
        st.session_state.ssh_private_key = None
    
    if "vm_ip" not in st.session_state:
        st.session_state.vm_ip = None

    # ── Auto-pipeline state ────────────────────────────────────────────────
    # pipeline_auto: bool  – is the automated Foreman→Critic→Orchestrator chain enabled
    # pipeline_results: list[dict] – log of all pipeline runs this session
    if "pipeline_auto" not in st.session_state:
        st.session_state.pipeline_auto = False

    if "pipeline_results" not in st.session_state:
        st.session_state.pipeline_results = []


# ============================================================================
# HELPER FUNCTIONS (used by components)
# ============================================================================

def save_chat_history() -> None:
    """Persist current session histories to chat_history.json."""
    save_history({
        "arch_history":    st.session_state.get("arch_history", []),
        "foreman_history": st.session_state.get("foreman_history", []),
        "orch_history":    st.session_state.get("orch_history", []),
    })


def _get_bash_code_from_message(message_content: str) -> str:
    """Extract bash code block from a message, or empty string if not found."""
    if "```bash" in message_content:
        return message_content.split("```bash")[1].split("```")[0].strip()
    return ""


def _render_chat_history(history: list):
    """Render a chat message history."""
    for message in history:
        st.chat_message(message["role"]).write(message["content"])


# ============================================================================
# ARCHITECT COLUMN
# ============================================================================

def render_architect_column(
    call_gemini_fn,
    skill_manager,
    credentials,
):
    """
    Render the Architect column.
    
    The Architect analyzes project structure, creates ADRs, and makes strategic decisions.
    
    Args:
        call_gemini_fn: Function to call Gemini LLM
        skill_manager: SkillManager instance
        credentials: Google Cloud credentials
    """
    st.markdown("### 🏛️ Архитектор")
    
    # Chat message display area
    with st.container(height=500, border=True):
        _render_chat_history(st.session_state.arch_history)

    # User input
    if p := st.chat_input("Глобальная стратегия...", key="in_arch"):
        # 1. Save user message
        st.session_state.arch_history.append({"role": "user", "content": p})
        save_chat_history()
        
        # 2. Build context history (last 10 messages before current)
        history_context = "\n".join([
            f"{'User' if m['role'] == 'user' else 'Architect'}: {m['content']}" 
            for m in st.session_state.arch_history[-11:-1]
        ])

        # 3. Get project context
        full_context = get_architect_context()

        # 4. Build final prompt
        prompt = f"""
PROJECT CONTEXT & STRUCTURE:
{full_context}

RECENT CHAT HISTORY:
{history_context if history_context else "No previous conversation."}

CURRENT REQUEST:
{p}
"""

        with st.spinner("Архитектор анализирует структуру и документацию..."):
            res = call_gemini_fn(
                MODEL_PRO,
                prompt,
                load_instruction("architect", skill_manager)
            )
            
        # 5. Save response
        st.session_state.arch_history.append({"role": "assistant", "content": res})
        save_chat_history()
        st.rerun()


# ============================================================================
# FOREMAN COLUMN
# ============================================================================

@st.fragment
def _render_foreman_command_buttons(
    message_content: str,
    message_index: int,
    call_gemini_fn,
    validate_bash_fn,
    skill_manager,
    credentials,
    oslogin_service,
):
    """
    Render command execution buttons for a foreman message.
    Fragment allows reactive updates without full page rerun for button clicks.
    """
    bash_code = _get_bash_code_from_message(message_content)
    if not bash_code:
        return

    c1, c2 = st.columns(2)
    
    # Send to Critic button
    if c1.button("⚖️ Критику", key=f"c_btn_{message_index}"):
        st.session_state.pending_cmd = bash_code
        
        with st.spinner("Критик ищет подвох..."):
            # 1. Automatic validation
            is_safe, tech_report = validate_bash_fn(bash_code)
            
            # 2. AI analysis
            full_context = get_project_context()
            prompt = f"АНАЛИЗ КОМАНДЫ: {bash_code}\n\nОТЧЕТ ВАЛИДАТОРА: {tech_report}\n\nКОНТЕКСТ: {full_context}"
            ai_report = call_gemini_fn(
                MODEL_PRO,
                prompt,
                load_instruction("critic", skill_manager)
            )
            
            # 3. Combine reports
            st.session_state.critic_report = f"{tech_report}\n\n---\n**AI Анализ:**\n{ai_report}"
            st.session_state.is_cmd_blocked = not is_safe
        
        st.rerun()
    
    # Direct to Orchestrator button
    if c2.button("🚀 В Оркестратор", key=f"o_btn_{message_index}"):
        with st.spinner("Выполнение команды (может занять до 2-х минут)..."):
            out = execute_ssh(bash_code, credentials, oslogin_service, exec_timeout=120)
            st.session_state.orch_history.append(f"$ {bash_code}\n{out}")
            feedback = f"РЕЗУЛЬТАТ КОМАНДЫ `{bash_code}`:\n```\n{out}\n```"
            st.session_state.foreman_history.append({"role": "user", "content": feedback})
            save_chat_history()
        st.rerun()


@st.fragment
def _render_foreman_doc_to_arch_button(
    message_content: str,
    message_index: int,
    call_gemini_fn,
    skill_manager,
):
    """
    Render button to send documentation to Architect.
    Fragment allows reactive updates without full page rerun.
    """
    if "[DOC_TO_ARCH]" not in message_content:
        return

    if st.button(
        "🏛️ Отправить Архитектору",
        key=f"send_to_arch_{message_index}",
        use_container_width=True
    ):
        # 1. Clean content from tags
        clean_content = (
            message_content
            .replace("[DOC_TO_ARCH]", "")
            .replace("[/DOC_TO_ARCH]", "")
            .strip()
        )
        
        # 2. Build message for Architect
        from_foreman_msg = f"ВВОД ОТ ПРОРАБА:\n{clean_content}"
        
        # 3. Add to Architect's history
        st.session_state.arch_history.append({"role": "user", "content": from_foreman_msg})
        save_chat_history()
        
        # 4. Get Architect's response
        with st.spinner("Архитектор обрабатывает данные от Прораба..."):
            full_context = get_architect_context()
            prompt = f"{full_context}\n\n{from_foreman_msg}"
            res = call_gemini_fn(
                MODEL_PRO,
                prompt,
                load_instruction("architect", skill_manager)
            )
        
        st.session_state.arch_history.append({"role": "assistant", "content": res})
        save_chat_history()
        st.toast("Документация передана и обработана Архитектором")
        st.rerun()


def render_foreman_column(
    call_gemini_fn,
    validate_bash_fn,
    search_skills_fn,
    skill_manager,
    credentials,
    oslogin_service,
    get_ssh_recent_memory_fn=None,
):
    """
    Render the Foreman column.
    
    The Foreman executes tasks, generates commands, and communicates with other agents.
    
    Args:
        call_gemini_fn: Function to call Gemini LLM
        validate_bash_fn: Function to validate bash commands
        search_skills_fn: Function to search for skills
        skill_manager: SkillManager instance
        credentials: Google Cloud credentials
        oslogin_service: OS Login service
        get_ssh_recent_memory_fn: Function to retrieve recent SSH log entries
    """
    st.markdown("### 👷 Прораб")
    
    # File upload for screenshots
    up_file = st.file_uploader("Скриншот", type=["png", "jpg", "jpeg"])
    
    # Chat message display area
    with st.container(height=400, border=True):
        for idx, m in enumerate(st.session_state.foreman_history):
            with st.chat_message(m["role"]):
                st.write(m["content"])
                
                # Render command buttons if message contains bash code
                _render_foreman_command_buttons(
                    m["content"],
                    idx,
                    call_gemini_fn,
                    validate_bash_fn,
                    skill_manager,
                    credentials,
                    oslogin_service,
                )
                
                # Render doc-to-arch button if message has tag
                _render_foreman_doc_to_arch_button(
                    m["content"],
                    idx,
                    call_gemini_fn,
                    skill_manager,
                )

    # ── Auto-pipeline toggle ──────────────────────────────────────────────
    st.session_state.pipeline_auto = st.toggle(
        "⚡ Авто-пайплайн  (Прораб → Критик → Оркестратор)",
        value=st.session_state.get("pipeline_auto", False),
        help=(
            "При включении каждая bash-команда Прораба автоматически "
            "проходит проверку Критика и, если безопасна, выполняется "
            "Оркестратором — без ручных нажатий."
        ),
    )

    # User input
    if p := st.chat_input("Задание...", key="in_fore"):
        # 1. Get context
        mem = get_project_context()
        ssh_mem = get_ssh_recent_memory_fn(5) if get_ssh_recent_memory_fn else ""

        # 2. Extract screenshot bytes if uploaded
        image_bytes = up_file.read() if up_file else None

        # 3. Call Gemini
        st.session_state.foreman_history.append({"role": "user", "content": p})
        save_chat_history()
        res = call_gemini_fn(
            MODEL_PRO,
            f"{mem}\n\n{ssh_mem}\n\nTask: {p}",
            load_instruction("foreman", skill_manager),
            image_bytes=image_bytes,
        )
        st.session_state.foreman_history.append({"role": "assistant", "content": res})
        save_chat_history()

        # 4. Auto-skill search logic
        if "[NEED_SKILL:" in res:
            skill_query = res.split("[NEED_SKILL:")[1].split("]")[0].strip()
            st.toast(f"🔎 Оркестратор ищет навык: {skill_query}")
            search_results = search_skills_fn(skill_query, credentials, oslogin_service)
            st.session_state.last_cli_output_search = search_results
            orch_msg = f"🤖 Нашел навыки для задачи '{skill_query}'. Выберите лучший для установки ниже."
            st.session_state.orch_history.append(orch_msg)
            save_chat_history()

        # 5. ── Auto-pipeline ──────────────────────────────────────────────
        if st.session_state.pipeline_auto:
            bash_code = _get_bash_code_from_message(res)
            if bash_code:
                with st.status("⚡ Авто-пайплайн...", expanded=True) as _status:
                    pipeline_result: PipelineResult = run_pipeline(
                        bash_command=bash_code,
                        call_gemini_fn=call_gemini_fn,
                        skill_manager=skill_manager,
                        credentials=credentials,
                        oslogin_service=oslogin_service,
                        on_step=_status.write,
                    )
                    _final_label = (
                        "⛔ Заблокировано Критиком"
                        if pipeline_result.is_blocked
                        else ("❌ Ошибка" if pipeline_result.error else "✅ Выполнено")
                    )
                    _final_state = (
                        "error" if (pipeline_result.is_blocked or pipeline_result.error) else "complete"
                    )
                    _status.update(label=f"⚡ Авто-пайплайн — {_final_label}", state=_final_state)

                # Store result for Orchestrator column display
                st.session_state.pipeline_results.append(
                    {
                        "command": pipeline_result.command,
                        "critic_report": pipeline_result.full_critic_report,
                        "is_blocked": pipeline_result.is_blocked,
                        "execution_output": pipeline_result.execution_output,
                        "error": pipeline_result.error,
                        "status_emoji": pipeline_result.status_emoji,
                    }
                )

                # Feed result back to Foreman so LLM can react on next turn
                feedback = pipeline_result.foreman_feedback()
                st.session_state.foreman_history.append(
                    {"role": "user", "content": feedback}
                )
                save_chat_history()

                # Mirror execution in Orchestrator SSH log
                if pipeline_result.execution_output:
                    st.session_state.orch_history.append(
                        f"$ {pipeline_result.command}\n{pipeline_result.execution_output}"
                    )

                state_label = (
                    "заблокировано Критиком"
                    if pipeline_result.is_blocked
                    else ("выполнено" if pipeline_result.success else "ошибка")
                )
                st.toast(f"{pipeline_result.status_emoji} Пайплайн завершён: {state_label}")

        st.rerun()


# ============================================================================
# CRITIC COLUMN
# ============================================================================

@st.fragment
def _render_critic_command_review(credentials, oslogin_service):
    """
    Render the command review panel in the Critic column.
    Fragment allows reactive updates for button clicks without full rerun.
    
    Args:
        credentials: Google Cloud credentials
        oslogin_service: OS Login service
    """
    if not st.session_state.pending_cmd:
        st.info("Нет активных задач для проверки.")
        return

    st.info(f"**Команда на проверке:**\n`{st.session_state.pending_cmd}`")
    
    # Отображаем отчёт Критика, если он есть
    if st.session_state.critic_report:
        st.markdown("#### 📝 Отчет по безопасности:")
        st.write(st.session_state.critic_report)
    
    # Check if command is blocked
    if st.session_state.get('is_cmd_blocked', False):
        st.error("⛔ Approve заблокирован: команда нарушает правила безопасности.")
        st.button("✅ Approve", disabled=True)
    else:
        c1, c2 = st.columns(2)
        
        # Approve button
        if c1.button("✅ Approve", help="Выполнить в Оркестраторе"):
            with st.spinner("Выполнение..."):
                out = execute_ssh(st.session_state.pending_cmd, credentials, oslogin_service)
                st.session_state.orch_history.append(
                    f"$ {st.session_state.pending_cmd}\n{out}"
                )
                st.session_state.foreman_history.append({
                    "role": "user",
                    "content": f"РЕЗУЛЬТАТ `{st.session_state.pending_cmd}`:\n{out}"
                })
                save_chat_history()
            
            # Clear pending command
            st.session_state.pending_cmd = None
            st.session_state.critic_report = None
            st.rerun()
        
        # Revision button
        if c2.button("🔄 Revision", help="Отправить Прорабу на пересмотр"):
            feedback = (
                f"КРИТИК ОТКЛОНИЛ КОМАНДУ `{st.session_state.pending_cmd}`.\n\n"
                f"ОТЧЕТ КРИТИКА:\n{st.session_state.critic_report}\n\n"
                f"ПРАВКИ: {st.session_state.crit_manual}"
            )
            st.session_state.foreman_history.append({"role": "user", "content": feedback})
            save_chat_history()
            
            # Clear pending command
            st.session_state.pending_cmd = None
            st.session_state.critic_report = None
            st.rerun()
    
    # Cancel button (always available)
    col1, col2, col3 = st.columns(3)
    with col3:
        if st.button("❌ Cancel", help="Удалить задачу"):
            st.session_state.pending_cmd = None
            st.session_state.critic_report = None
            st.rerun()


def render_critic_column(credentials, oslogin_service):
    """
    Render the Critic column.
    
    The Critic reviews commands for safety and provides detailed security analysis.
    
    Args:
        credentials: Google Cloud credentials
        oslogin_service: OS Login service
    """
    st.markdown("### 🔍 Критик")
    
    # Command review panel
    with st.container(height=500, border=True):
        _render_critic_command_review(credentials, oslogin_service)
    
    # Manual critique notes input
    st.session_state.crit_manual = st.text_area(
        "Замечания критика",
        value=st.session_state.crit_manual,
        height=100,
        key="crit_notes_input"
    )


# ============================================================================
# ORCHESTRATOR COLUMN
# ============================================================================

@st.fragment
def _render_orchestrator_sync_button(
    sync_docs_fn,
    append_to_history_fn,
):
    """
    Render the sync and update button for the Orchestrator.
    Fragment allows reactive updates without full page rerun.
    """
    if st.button(
        "🔄 Sync & Update Project Status",
        use_container_width=True,
        type="primary"
    ):
        with st.spinner("Синхронизация документации и логов..."):
            # 1. Sync documentation
            status_msg = sync_docs_fn()
            st.toast(status_msg)
            
            # 2. Local commit
            git_local_commit(
                "docs: update stage progress and history log",
                file_paths=[
                    "docs/STAGE_BRIEFS/STAGE_B.md",
                    "logs/HISTORY.log"
                ]
            )
            
            # 3. Sync logs only (without code drafts)
            res = git_sync_logs_only()
            
            if "✅" in res:
                st.success("Статус обновлен, логи синхронизированы!")
            else:
                st.error(f"Ошибка синхронизации: {res}")


def render_orchestrator_column(
    sync_docs_fn,
    append_to_history_fn,
):
    """
    Render the Orchestrator column.

    The Orchestrator executes commands, syncs documentation, and manages project state.
    When the auto-pipeline is active, also renders a live log of pipeline runs.

    Args:
        sync_docs_fn: Function to sync documentation and history
        append_to_history_fn: Function to append actions to history log
    """
    st.markdown("### 🤖 Оркестратор")

    # ── Pipeline run log (visible only when there are results) ────────────
    if st.session_state.get("pipeline_results"):
        with st.expander(
            f"⚡ Авто-пайплайн — {len(st.session_state.pipeline_results)} запусков",
            expanded=True,
        ):
            for i, pr in enumerate(reversed(st.session_state.pipeline_results), 1):
                status = pr["status_emoji"]
                st.markdown(f"**{i}. {status} `{pr['command']}`**")

                if pr["critic_report"]:
                    with st.expander("📝 Отчёт Критика", expanded=pr["is_blocked"]):
                        st.markdown(pr["critic_report"])

                if pr["is_blocked"]:
                    st.error("⛔ Команда заблокирована Критиком. Прораб получил фидбек.")
                elif pr["error"]:
                    st.error(f"❌ Ошибка пайплайна: {pr['error']}")
                elif pr["execution_output"] is not None:
                    with st.expander("💻 Вывод Оркестратора", expanded=True):
                        st.code(pr["execution_output"], language="bash")

                st.divider()

            if st.button("🗑️ Очистить лог пайплайна", use_container_width=True):
                st.session_state.pipeline_results = []
                st.rerun()

    # ── SSH log (manual executions) ───────────────────────────────────────
    with st.container(height=300, border=True):
        output = "\n".join(st.session_state.orch_history)
        st.code(output, language="bash")

    # Sync and update button
    _render_orchestrator_sync_button(
        sync_docs_fn,
        append_to_history_fn,
    )
