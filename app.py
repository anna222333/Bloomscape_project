import streamlit as st
import os
import app.config
from app.config import (
    LOCATION, MODEL_PRO, MODEL_FLASH, ADR_DIR, LOGS_DIR, SSH_LOG_FILE, REPO_PATH,
    GCP_INSTANCE_NAME, GCP_INSTANCE_ZONE, DEFAULT_VM_USERNAME
)
from app.core.auth import get_gemini_key
from app.core.gcp_helpers import get_instance_ip, validate_instance_exists, is_oslogin_enabled
from app.core.ssh_executor import execute_ssh, upload_to_vm
from app.core.git_manager import git_local_commit, git_push_to_github, git_sync_logs_only
from app.core.skill_engine import initialize_skill_manager, load_instruction, search_skills, critic_verify_skill, install_new_skill_everywhere
from app.core.llm_provider import GeminiInterface
from app.core.context_builder import ProjectFileManager, get_project_context, get_project_structure, get_architect_context
from app.core.validators import validate_bash_command
from app.core.logger import history_logger, app_logger
from app.ui.components import (
    init_session_state,
    render_architect_column,
    render_foreman_column,
    render_critic_column,
    render_orchestrator_column,
)
from google.cloud import secretmanager
import google.auth
import io
import datetime
import subprocess
import paramiko
import bashlex
from googleapiclient import discovery
from git import Repo
from skillkit import SkillManager


# --- 1. SECURE CONFIGURATION (Secret Manager + API Key) ---
try:
    credentials, project = google.auth.default()
    
    # --- Resolve PROJECT_ID ---
    # Priority: google.auth.default() → GOOGLE_CLOUD_PROJECT → PROJECT_ID env var
    resolved_project = (
        project
        or os.getenv("GOOGLE_CLOUD_PROJECT")
        or os.getenv("PROJECT_ID")
    )
    if not resolved_project:
        st.error("❌ PROJECT_ID не определён. Передайте через env PROJECT_ID или GOOGLE_CLOUD_PROJECT.")
        st.stop()
    app.config.PROJECT_ID = resolved_project
    app_logger.log_initialization("PROJECT_ID", "OK", f"Resolved: {resolved_project}")
    
    # --- 1a. Resolve VM IP ---
    VM_IP = os.getenv("VM_IP")
    if not VM_IP or VM_IP == "127.0.0.1":
        # Try to resolve via Compute API
        app_logger.log_info(f"VM_IP not set or localhost, resolving via Compute API: {GCP_INSTANCE_NAME}/{GCP_INSTANCE_ZONE}")
        VM_IP = get_instance_ip(GCP_INSTANCE_NAME, GCP_INSTANCE_ZONE, credentials, ip_type='external')
        if not VM_IP:
            # Fallback to internal IP if external not available
            VM_IP = get_instance_ip(GCP_INSTANCE_NAME, GCP_INSTANCE_ZONE, credentials, ip_type='internal')
        if VM_IP:
            app_logger.log_initialization("VM_IP_RESOLUTION", "OK", f"Resolved to {VM_IP}")
        else:
            app_logger.log_initialization("VM_IP_RESOLUTION", "FAILED", "Could not resolve VM IP")
    
    # --- 1b. Validate instance exists ---
    if not validate_instance_exists(GCP_INSTANCE_NAME, GCP_INSTANCE_ZONE, credentials):
        st.error(f"❌ GCP instance '{GCP_INSTANCE_NAME}' not found in zone '{GCP_INSTANCE_ZONE}'")
        st.stop()
    
    # --- 1c. Check if OS Login is enabled ---
    oslogin_enabled = is_oslogin_enabled(GCP_INSTANCE_NAME, GCP_INSTANCE_ZONE, credentials)
    if oslogin_enabled:
        app_logger.log_info("OS Login is enabled on instance")
    else:
        app_logger.log_info("OS Login is disabled; will use instance metadata SSH keys")
    
    # --- 1d. Initialize API clients & Gemini ---
    GEMINI_API_KEY = get_gemini_key(credentials)
    gemini_interface = GeminiInterface(api_key=GEMINI_API_KEY, credentials=credentials)
    oslogin_service = discovery.build('oslogin', 'v1', credentials=credentials)
    app_logger.log_initialization("GCP_AUTH", "OK", f"VM_IP={VM_IP} Instance={GCP_INSTANCE_NAME}")
except Exception as e:
    app_logger.log_initialization("GCP_AUTH", "FAILED", str(e))
    st.error(f"Критическая ошибка инициализации: {e}")
    st.stop()

# Store resolved VM_IP in session state for access in other modules
st.session_state.vm_ip = VM_IP

# --- 2. INITIALIZE SKILLKIT ---
skill_manager = initialize_skill_manager()

def get_ssh_recent_memory(n=100):
    """Получить последние SSH команды из лога"""
    if not os.path.exists(SSH_LOG_FILE):
        return "История SSH пуста."
    try:
        with open(SSH_LOG_FILE, "r", encoding="utf-8") as f:
            # Читаем последние 10 000 символов файла, чтобы не перегружать память
            f.seek(0, os.SEEK_END)
            file_size = f.tell()
            f.seek(max(0, file_size - 10000)) # Вот здесь настраивается "глубина" в символах
            
            content = f.read()
            entries = content.split('-'*40)
            recent = [e.strip() for e in entries if e.strip()][-n:]
            
            return "\n\n--- ПОСЛЕДНИЕ ДЕЙСТВИЯ НА СЕРВЕРЕ ---\n" + "\n---\n".join(recent) if recent else "Нет недавних команд."
    except Exception as e:
        return f"Ошибка чтения лога: {e}"


# Сбор логов и истории

def append_to_history(action_text):
    """Запись действия в HISTORY.log используя логгер"""
    return history_logger.log_action(action_text)

def sync_docs_and_history():
    """Слушатель: сопоставляет лог и бриф стадии"""
    try:
        history_path = "logs/HISTORY.log"
        stage_path = "docs/STAGE_BRIEFS/STAGE_B.md"
        
        if not os.path.exists(history_path) or not os.path.exists(stage_path):
            return "⚠️ Файлы истории или брифа не найдены."

        with open(history_path, "r") as f:
            history = f.read()[-2000:]
        with open(stage_path, "r") as f:
            current_stage = f.read()

        prompt = f"HISTORY LOG:\n{history}\n\nCURRENT STAGE BRIEF:\n{current_stage}\n\nTask: Update checkboxes [ ] to [x] for completed tasks. Return ONLY full markdown."
        updated_content = call_gemini(MODEL_FLASH, prompt, "You are a synchronization agent.")
        
        ProjectFileManager.write_file(stage_path, updated_content)
        return "✅ Бриф стадии актуализирован."
    except Exception as e:
        return f"❌ Ошибка синхронизатора: {str(e)}"



# Функции контекста перенесены в app.core.context_builder

def call_gemini(model_id, prompt, system_instruction, image_bytes=None):
    """
    Вызывает LLM и обрабатывает структурированные теги в ответе.
    """
    try:
        # 1. Получаем ответ из Gemini
        text = gemini_interface.generate_content(model_id, prompt, system_instruction, image_bytes)
        
        if text.startswith("❌"):
            return text
        
        # 2. Парсим теги из ответа
        tags = gemini_interface.parse_tags(text)
        
        # 3. Обрабатываем найденные теги, получаем дополнительный текст для ответа
        extra_text = process_parsed_tags(tags)
        if extra_text:
            text += extra_text
        
        return text
    except Exception as e:
        return f"❌ Ошибка Gemini: {str(e)}"

def process_parsed_tags(tags):
    """
    Обрабатывает найденные структурированные теги из LLM ответа.
    
    Args:
        tags: Словарь с распарсенными тегами из GeminiInterface.parse_tags()
    
    Returns:
        str: Дополнительный текст для добавления к ответу (или пустая строка)
    """
    updated_arch_docs = []
    extra_text_parts = []
    
    # Используем безопасный менеджер файлов с проверкой FORBIDDEN_PATHS
    FORBIDDEN_PATHS = ProjectFileManager.FORBIDDEN_PATHS
    
    def is_write_prohibited(file_path):
        return ProjectFileManager.is_write_prohibited(file_path)
    
    # Обработка [WRITE_ADR:]
    if "write_adr" in tags:
        adr_info = tags["write_adr"]
        adr_name = adr_info["name"]
        content = adr_info["content"]
        path = f"docs/ADR/{adr_name}"
        if not is_write_prohibited(path):
            ProjectFileManager.write_file(path, content, check_forbidden=False)
            updated_arch_docs.append(path)
            st.toast(f"🏛 ADR зафиксирован: {adr_name}")
    
    # Обработка [WRITE_DOC:]
    if "write_doc" in tags:
        doc_info = tags["write_doc"]
        path = doc_info["path"]
        content = doc_info["content"]
        if path.startswith("docs/") and not is_write_prohibited(path):
            ProjectFileManager.write_file(path, content, check_forbidden=False)
            updated_arch_docs.append(path)
            st.toast(f"🏛 Файл обновлен: {path}")
        else:
            st.error(f"⛔ Доступ запрещен! Архитектор не может изменять: {path}")
    
    # Обработка [UPDATE_MASTER:]
    if "update_master" in tags:
        content = tags["update_master"]
        path = "docs/MASTER_PLAN.md"
        ProjectFileManager.write_file(path, content, check_forbidden=False)
        updated_arch_docs.append(path)
        st.toast("🏛 MASTER_PLAN обновлен")
    
    # Коммит документов Архитектора (независимо от GIT_PUSH)
    if updated_arch_docs:
        git_local_commit("arch: strategic documentation update", file_paths=updated_arch_docs)
    
    # Обработка [GIT_PUSH] — пуш только по явному запросу
    if tags.get("git_push"):
        push_res = git_push_to_github()
        st.toast(push_res)
        extra_text_parts.append(f"\n\n**Системное уведомление:** {push_res}")
    
    # Обработка [READ_FILE:] — tags["read_file"] — список путей
    if "read_file" in tags:
        file_paths_to_read = tags["read_file"]
        # parse_tags возвращает список путей
        if isinstance(file_paths_to_read, str):
            file_paths_to_read = [file_paths_to_read]
        for file_path_to_read in file_paths_to_read:
            try:
                full_path = os.path.join(REPO_PATH, file_path_to_read)
                if os.path.exists(full_path) and os.path.isfile(full_path):
                    with open(full_path, "r", encoding="utf-8") as f:
                        content = f.read()
                    if len(content) > 100000:
                        content = content[:100000] + "\n... [Файл обрезан из-за размера]"
                    # Возвращаем содержимое файла в ответ, чтобы пользователь видел его в чате
                    extra_text_parts.append(f"\n\n📖 Содержимое файла `{file_path_to_read}`:\n```\n{content}\n```")
                    st.toast(f"📖 Файл {file_path_to_read} прочитан")
                else:
                    extra_text_parts.append(f"\n\n⚠️ Ошибка: Файл `{file_path_to_read}` не найден.")
            except Exception as e:
                extra_text_parts.append(f"\n\n❌ Ошибка при чтении: {str(e)}")
    
    # Обработка [GENERATE_IMAGE:]
    if "generate_image" in tags:
        img_prompt = tags["generate_image"]
        try:
            with st.spinner(f"Imagen 3 генерирует: {img_prompt}..."):
                img_res = generate_image_with_imagen(img_prompt)
            st.info(img_res)
        except Exception as e:
            st.error(f"Ошибка генерации изображения: {e}")
    
    # Обработка [PUBLISH_IMAGE:]
    if "publish_image" in tags:
        pub_prompt = tags["publish_image"]
        try:
            with st.spinner(f"Imagen 3 генерирует для публикации: {pub_prompt}..."):
                img_msg = generate_image_with_imagen(pub_prompt)
            if "✅" in img_msg:
                local_file_path = img_msg.split(": ")[1].strip()
                file_name = os.path.basename(local_file_path)
                remote_file_path = f"/var/www/html/assets/products/{file_name}"
                upload_status = upload_to_vm(local_file_path, remote_file_path, credentials, oslogin_service)
                append_to_history(f"Прораб опубликовал товар: {file_name}")
        except Exception as e:
            st.error(f"Ошибка процесса публикации: {e}")
    
    # Обработка [LOG_ACTION:]
    if "log_action" in tags:
        action_data = tags["log_action"]
        res = append_to_history(action_data)
        st.toast(res)
    
    return "\n".join(extra_text_parts) if extra_text_parts else ""

def generate_image_with_imagen(prompt):
    try:
        model = ImageGenerationModel.from_pretrained("imagen-3.0-generate-001")
        images = model.generate_images(prompt=prompt, number_of_images=1)
        os.makedirs("docs/assets", exist_ok=True)
        file_path = f"docs/assets/gen_{datetime.datetime.now().strftime('%s')}.png"
        images[0].save(location=file_path, include_generation_parameters=False)
        return f"✅ Imagen 3: {file_path}"
    except Exception as e:
        return f"❌ Imagen 3 Error: {str(e)}"

# ============================================================================
# UI SETUP & PAGE CONFIGURATION
# ============================================================================

st.set_page_config(page_title="Bloom Control Center", layout="wide")

# Initialize all session state variables
init_session_state()

# ============================================================================
# MAIN APPLICATION LAYOUT
# ============================================================================

col_arch, col_fore, col_crit, col_orch = st.columns([1, 1, 1, 1.2], gap="small")

with col_arch:
    render_architect_column(call_gemini, skill_manager, credentials)

with col_fore:
    render_foreman_column(
        call_gemini,
        validate_bash_command,
        search_skills,
        skill_manager,
        credentials,
        oslogin_service,
        get_ssh_recent_memory_fn=get_ssh_recent_memory,
    )

with col_crit:
    render_critic_column(credentials, oslogin_service)

with col_orch:
    render_orchestrator_column(sync_docs_and_history, append_to_history)
