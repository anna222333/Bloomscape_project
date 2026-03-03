import streamlit as st
import os
import datetime
from app.config import MODEL_FLASH, LOGS_DIR, SSH_LOG_FILE, REPO_PATH
from app.core.auth import get_gemini_key
from app.core.ssh_executor import upload_to_vm
from app.core.git_manager import git_local_commit, git_push_to_github
from app.core.skill_engine import initialize_skill_manager, search_skills
from app.core.llm_provider import GeminiInterface
from app.core.context_builder import ProjectFileManager
from app.core.validators import validate_bash_command
from app.core.logger import history_logger, app_logger
from vertexai.preview.vision_models import ImageGenerationModel
from app.ui.components import (
    init_session_state,
    save_chat_history,
    render_architect_column,
    render_foreman_column,
    render_critic_column,
    render_orchestrator_column,
)
import google.auth
from googleapiclient import discovery


# --- 1. SECURE CONFIGURATION (Secret Manager + API Key) ---
# @st.cache_resource: инициализируется один раз на весь сеанс сервера,
# не пересоздаётся при каждом взаимодействии пользователя с UI.

@st.cache_resource
def _init_gcp():
    """Инициализирует GCP-зависимости и возвращает (credentials, gemini_interface, oslogin_service)."""
    creds, _project = google.auth.default()
    api_key = get_gemini_key(creds)
    g_interface = GeminiInterface(api_key=api_key, credentials=creds)
    oslogin_svc = discovery.build('oslogin', 'v1', credentials=creds)
    app_logger.log_initialization("GCP_AUTH", "OK")
    return creds, g_interface, oslogin_svc

@st.cache_resource
def _init_skill_manager():
    """Инициализирует SkillManager один раз на сеанс."""
    return initialize_skill_manager()

try:
    credentials, gemini_interface, oslogin_service = _init_gcp()
except Exception as e:
    app_logger.log_initialization("GCP_AUTH", "FAILED", str(e))
    st.error(f"Критическая ошибка инициализации: {e}")
    st.stop()

# --- 2. INITIALIZE SKILLKIT ---
skill_manager = _init_skill_manager()
if skill_manager is None:
    st.warning("⚠️ SkillKit не инициализирован. Роли будут работать без навыков — проверьте docs/skills/ и запустите приложение снова.")

def get_ssh_recent_memory(n=100):
    if not os.path.exists(SSH_LOG_FILE):
        return "История SSH пуста."
    try:
        import re
        with open(SSH_LOG_FILE, "r", encoding="utf-8") as f:
            f.seek(0, os.SEEK_END)
            file_size = f.tell()
            f.seek(max(0, file_size - 10000))
            content = f.read()

        # Новый формат логгера: каждая запись начинается со строки с timestamp
        # Пример: "2026-03-01 14:23:45 | ssh | INFO | EXECUTION | ..."
        # Группируем: INFO/WARNING/ERROR строки — заголовок записи,
        # следующие DEBUG строки (OUTPUT:) — тело этой же записи.
        entry_pattern = re.compile(
            r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} \| ssh \| (?!DEBUG)',
            re.MULTILINE
        )

        # Находим позиции всех заголовков записей
        boundaries = [m.start() for m in entry_pattern.finditer(content)]

        if not boundaries:
            # Файл может содержать старый формат или быть пустым
            return "История SSH пуста или формат не распознан."

        # Нарезаем записи по найденным границам
        entries = []
        for i, start in enumerate(boundaries):
            end = boundaries[i + 1] if i + 1 < len(boundaries) else len(content)
            entries.append(content[start:end].strip())

        recent = entries[-n:]
        return "\n\n--- ПОСЛЕДНИЕ ДЕЙСТВИЯ НА СЕРВЕРЕ ---\n" + "\n---\n".join(recent)
    except Exception as e:
        return f"Ошибка чтения лога: {e}"


# Сбор логов и истории

def append_to_history(action_text):
    """Запись действия в HISTORY.log используя логгер"""
    return history_logger.log_action(action_text)

def sync_docs_and_history():
    """Слушатель: сопоставляет лог и бриф стадии"""
    try:
        history_path = os.path.join(LOGS_DIR, "HISTORY.log")  # logs/HISTORY.log — туда пишет history_logger
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
        
        # 3. Обрабатываем найденные теги и получаем содержимое прочитанных файлов
        extra_text = process_parsed_tags(tags)
        
        # 4. Добавляем содержимое файлов к ответу — теперь Архитектор «видит» их в чате
        if extra_text:
            text = text + extra_text
        
        return text
    except Exception as e:
        return f"❌ Ошибка Gemini: {str(e)}"

def process_parsed_tags(tags):
    """
    Обрабатывает найденные структурированные теги из LLM ответа.
    Возвращает дополнительный текст для добавления к ответу (например, содержимое прочитанных файлов).
    
    Args:
        tags: Словарь с распарсенными тегами из GeminiInterface.parse_tags()
    
    Returns:
        str: Дополнительный текст для добавления к ответу (пустая строка если ничего нет)
    """
    updated_arch_docs = []
    extra_text = ""  # накапливаем содержимое прочитанных файлов
    
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
    
    # Обработка [GIT_PUSH]
    # Локальный коммит — всегда, если что-то было записано (независимо от тега)
    if updated_arch_docs:
        git_local_commit("arch: strategic documentation update", file_paths=updated_arch_docs)
    # Пуш в remote — только если модель явно добавила тег [GIT_PUSH]
    if tags.get("git_push"):
        push_res = git_push_to_github()
        st.toast(push_res)
    
    # Обработка [READ_FILE:] — поддержка нескольких файлов в одном ответе
    if "read_file" in tags:
        file_paths_to_read = tags["read_file"]  # всегда список
        for file_path_to_read in file_paths_to_read:
            try:
                full_path = os.path.join(REPO_PATH, file_path_to_read)
                if os.path.exists(full_path) and os.path.isfile(full_path):
                    with open(full_path, "r", encoding="utf-8") as f:
                        content = f.read()
                    if len(content) > 100000:
                        content = content[:100000] + "\n... [Файл обрезан из-за размера]"
                    # Вклеиваем содержимое в ответ — именно так Архитектор его «видит»
                    extra_text += f"\n\n📖 **Содержимое файла `{file_path_to_read}`:**\n```\n{content}\n```"
                    st.toast(f"📖 Файл {file_path_to_read} прочитан")
                else:
                    extra_text += f"\n\n⚠️ Файл `{file_path_to_read}` не найден."
                    st.warning(f"⚠️ Файл `{file_path_to_read}` не найден.")
            except Exception as e:
                extra_text += f"\n\n❌ Ошибка при чтении `{file_path_to_read}`: {str(e)}"
                st.error(f"❌ Ошибка при чтении {file_path_to_read}: {str(e)}")
    
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
    
    return extra_text

def generate_image_with_imagen(prompt):
    try:
        model = ImageGenerationModel.from_pretrained("imagen-3.0-generate-001")
        images = model.generate_images(prompt=prompt, number_of_images=1)
        os.makedirs("docs/assets", exist_ok=True)
        file_path = f"docs/assets/gen_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
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

# --- AUTOSAVE ---
# Streamlit re-runs the entire script on every user interaction,
# so this call persists the latest state to chat_history.json each time.
save_chat_history()
