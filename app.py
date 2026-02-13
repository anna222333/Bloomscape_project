import streamlit as st
import os
from dotenv import load_dotenv
import io
import datetime
import base64
import json
import time
import subprocess
import paramiko
import requests
from google import genai
from google.genai import types
from google.cloud import secretmanager
from vertexai.preview.vision_models import ImageGenerationModel
from git import Repo
from skillkit import SkillManager  # Добавляем импорт SkillKit


# --- 1. CONFIGURATION ---
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
PROJECT_ID = os.getenv("PROJECT_ID")
SECRET_ID = os.getenv("SECRET_ID")
VM_IP = os.getenv("VM_IP")
VM_USER = os.getenv("VM_USER")
REPO_PATH = os.getcwd()
LOCATION = "us-central1"
SSH_LOG_FILE = "logs/ssh_audit.log"
MODEL_PRO = "models/gemini-3-pro-preview"
MODEL_FLASH = "models/gemini-3-flash-preview"

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "key.json"

# --- 2. CLIENTS INITIALIZATION ---
client_gemini = genai.Client(api_key=GEMINI_API_KEY)

# --- Инициализация SkillKit (Исправлено) ---
# Инициализируем без аргументов
skill_manager = SkillManager() 

# --- Инициализация SkillKit (Исправлено) ---
try:
    # Если папки нет, создаем её
    if not os.path.exists("docs/skills/"):
        os.makedirs("docs/skills/", exist_ok=True)
        
    # Передаем путь прямо при создании менеджера, если библиотека это поддерживает
    # Либо вызываем discover() без аргументов
    skill_manager = SkillManager() 
    skill_manager.discover() # Он сам найдет папку docs/skills, если она в корне
except Exception as e:
    st.error(f"Ошибка SkillKit: {e}")
# --- 2. SESSION STATE INITIALIZATION ---
if "last_cli_output_search" not in st.session_state:
    st.session_state.last_cli_output_search = ""
if "last_cli_output_install" not in st.session_state:
    st.session_state.last_cli_output_install = ""

# --- 3. CORE FUNCTIONS ---

def write_project_file(file_path, content):
    """
    Физическая запись файла на диск.
    Создает директории, если их нет.
    """
    try:
        # Защита от выхода за пределы проекта
        full_path = os.path.abspath(os.path.join(REPO_PATH, file_path))
        if not full_path.startswith(os.path.abspath(REPO_PATH)):
            st.error(f"⛔ Попытка записи вне репозитория: {file_path}")
            return False

        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)
        return True
    except Exception as e:
        st.error(f"❌ Ошибка записи файла {file_path}: {str(e)}")
        return False

# --- ОБНОВЛЕННАЯ ФУНКЦИЯ ЗАГРУЗКИ ИНСТРУКЦИЙ ---
def load_instruction(role):
    # 1. Загрузка базовой личности (Личность и характер)
    base_text = ""
    path = f"docs/INSTRUCTIONS/{role}.txt"
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            base_text = f.read()
    else:
        base_text = f"You are the {role}. Act professionally as a member of the Bloomscape team."

    # 2. Маппинг стека навыков (Инструментарий)
    role_map = {
        "architect": ["system-design", "adr-writer"],
        "foreman": ["python-expert", "adr-writer", "bash-wizard"],
        "critic": ["security-auditor", "code-review"],
        "orch": ["bash-wizard"]
    }
    
    extra_skills = role_map.get(role, [])
    skills_content = ""
    
    for skill_name in extra_skills:
        try:
            # Ищем навык в локальной папке docs/skills/
            skill = skill_manager.get_skill(skill_name)
            if skill:
                skills_content += f"\n\n[CAPABILITY: {skill_name.upper()}]\n{skill.content}"
        except:
            continue # Если навык еще не установлен, просто пропускаем

    return base_text + "\n\n" + skills_content

def search_skills(query):
    """Используем глобальный skillkit вместо npx для скорости"""
    try:
        # Пытаемся вызвать напрямую, если не выйдет - откатываемся на npx
        command = f"skillkit find \"{query}\" || npx -y skillkit@latest find \"{query}\""
        return execute_ssh(command, exec_timeout=60) # Добавляем явный тайм-аут
    except Exception as e:
        return f"❌ Ошибка поиска: {str(e)}"

def critic_verify_skill(skill_list, user_task):
    """Критик анализирует найденные навыки на безопасность и соответствие проекту"""
    prompt = f"Пользователь хочет: {user_task}. SkillKit нашел: {skill_list}. Какой из них безопасен и лучше всего подходит? Ответь кратко."
    # Используем Pro модель для глубокого анализа
    return call_gemini(MODEL_PRO, prompt, load_instruction("critic"))

def install_new_skill_everywhere(repo_path, skill_name=None):
    """
    Автоматическая установка навыка на ВМ и на локальную машину одновременно.
    """
    # Формируем аргументы для SkillKit
    skill_arg = f"--skills {skill_name}" if skill_name else "--all"
    base_command = f"npx -y skillkit@latest install {repo_path} {skill_arg}"
    final_command = f"yes | {base_command}"
    
    results = []

    # 1. Установка на удаленный сервер (ВМ) через SSH
    with st.spinner(f"Установка на ВМ: {repo_path}..."):
        remote_out = execute_ssh(final_command, exec_timeout=180)
        results.append(f"🖥️ **VM Output:**\n{remote_out}")

    # 2. Установка локально (на твой ПК) через subprocess
    # Это нужно для того, чтобы SkillManager.discover() увидел новые файлы в docs/skills/
    with st.spinner(f"Локальная синхронизация навыка..."):
        try:
            # Выполняем команду в локальном терминале
            loc_res = subprocess.run(final_command, shell=True, capture_output=True, text=True, timeout=180)
            if loc_res.returncode == 0:
                results.append(f"💻 **Local Output:**\n✅ Успешно установлено локально.")
                # Обновляем менеджер навыков, чтобы он подхватил обновку
                skill_manager.discover(path="docs/skills/")
            else:
                results.append(f"💻 **Local Output:**\n❌ Ошибка: {loc_res.stderr}")
        except subprocess.TimeoutExpired:
            results.append(f"💻 **Local Output:**\n❌ Ошибка: Timeout при локальной установке (>3 мин)")
        except Exception as e:
            results.append(f"💻 **Local Output:**\n❌ Ошибка локального процесса: {str(e)}")

    # 3. Уведомление пользователя
    st.toast(f"Процесс установки завершен для {repo_path}")
    
    # 4. Финальный отчет для истории Оркестратора
    return "\n\n".join(results)

def get_ssh_key():
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{PROJECT_ID}/secrets/{SECRET_ID}/versions/latest"
    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode("UTF-8")



def get_ssh_recent_memory(n=100):
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


# Cбор логов и истории

def execute_ssh(command, exec_timeout=None):
    try:
        os.makedirs(os.path.dirname(SSH_LOG_FILE), exist_ok=True)
        key_string = get_ssh_key()
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        key_file_obj = io.StringIO(key_string)
        try:
            pkey = paramiko.RSAKey.from_private_key(key_file_obj)
        except:
            key_file_obj.seek(0)
            pkey = paramiko.Ed25519Key.from_private_key(key_file_obj)

        ssh.connect(hostname=VM_IP, username=VM_USER, pkey=pkey, timeout=10)
        # Передаём exec_timeout в exec_command, если он указан
        stdin, stdout, stderr = ssh.exec_command(command, get_pty=True, timeout=exec_timeout)
        res, err = stdout.read().decode(), stderr.read().decode()
        ssh.close()
        output = res if res else err
        with open(SSH_LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[{datetime.datetime.now()}] {command}\n{output}\n{'-'*40}\n")
        if len(output) > 2000:
            output = f"...[truncated]...\n{output[-2000:]}"
        return output
    except Exception as e:
        return f"SSH Error: {e}"

def git_sync_logs_only():
    """Оркестратор: работает ТОЛЬКО с файлом логов, не трогая код"""
    log_file = "logs/ssh_audit.log"
    try:
        if not os.path.exists("git.txt"): return "❌ Нет токена"
        with open("git.txt", "r") as f: token = f.read().strip()
        
        repo = Repo(REPO_PATH)
        # 1. Скрываем (stash) другие изменения, чтобы не захватить код Прораба
        stashed = False
        if repo.is_dirty():
            repo.git.stash('save', 'temp_before_logs')
            stashed = True
        
        # 2. Добавляем и коммитим ТОЛЬКО логи
        repo.git.add(log_file)
        repo.index.commit(f"sys: update ssh logs {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}")
        
        # 3. Пушим логи
        remote_url = repo.remotes.origin.url
        clean_url = remote_url.split('@')[-1].replace("https://", "")
        auth_url = f"https://{token}@{clean_url}"
        repo.git.push(auth_url, repo.active_branch.name)
        
        # 4. Возвращаем изменения кода обратно
        if stashed:
            repo.git.stash('pop')
            
        return "✅ Логи SSH синхронизированы."
    except Exception as e:
        return f"❌ Ошибка логов: {str(e)}"
    
def append_to_history(action_text):
    """Физическая запись действия в HISTORY.log"""
    try:
        path = os.path.join(REPO_PATH, "docs/HISTORY.log")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        with open(path, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {action_text}\n")
        return "✅ Запись добавлена в HISTORY.log"
    except Exception as e:
        return f"❌ Ошибка записи лога: {str(e)}"

def sync_docs_and_history():
    """Слушатель: сопоставляет лог и бриф стадии"""
    try:
        history_path = "docs/HISTORY.log"
        stage_path = "docs/STAGE_BRIEFS/STAGE_B.md"
        
        if not os.path.exists(history_path) or not os.path.exists(stage_path):
            return "⚠️ Файлы истории или брифа не найдены."

        with open(history_path, "r") as f:
            history = f.read()[-2000:]
        with open(stage_path, "r") as f:
            current_stage = f.read()

        prompt = f"HISTORY LOG:\n{history}\n\nCURRENT STAGE BRIEF:\n{current_stage}\n\nTask: Update checkboxes [ ] to [x] for completed tasks. Return ONLY full markdown."
        updated_content = call_gemini(MODEL_FLASH, prompt, "You are a synchronization agent.")
        
        write_project_file(stage_path, updated_content)
        return "✅ Бриф стадии актуализирован."
    except Exception as e:
        return f"❌ Ошибка синхронизатора: {str(e)}"

 # --- Функция для локального коммита изменений       

def git_local_commit(commit_message, file_paths=None):
    """Фиксация изменений в локальном репозитории"""
    try:
        repo = Repo(REPO_PATH)
        if file_paths:
            for fp in file_paths:
                clean_path = os.path.normpath(fp).lstrip('./').lstrip('/')
                repo.git.add(clean_path)
        else:
            repo.git.add(A=True)

        if not repo.is_dirty(untracked_files=True):
            return "ℹ️ Нет изменений для коммита."

        repo.index.commit(commit_message)
        return f"✅ Локальный коммит: {commit_message}"
    except Exception as e:
        return f"❌ Ошибка Git: {str(e)}"

 # --- Функция для пуша в GitHub       

def git_push_to_github():
    """Пуш накопленных коммитов в удаленный репозиторий"""
    try:
        if not os.path.exists("git.txt"): return "❌ Файл git.txt с токеном не найден"
        with open("git.txt", "r") as f: token = f.read().strip()

        repo = Repo(REPO_PATH)
        remote_url = repo.remotes.origin.url
        # Очистка URL для авторизации по токену
        clean_url = remote_url.split('@')[-1].replace("https://", "")
        auth_url = f"https://{token}@{clean_url}"
        
        current_branch = repo.active_branch.name
        repo.git.push(auth_url, current_branch, "-f")
        return "🚀 Все изменения успешно отправлены на GitHub!"
    except Exception as e:
        return f"❌ Ошибка Push: {str(e)}"

def get_project_context():
    context_sections = []
    
    # 1. ГЛОБАЛЬНЫЕ ЦЕЛИ (Master Plan & Success Criteria)
    context_sections.append("=== GLOBAL STRATEGY ===")
    global_paths = [
        "docs/MASTER_PLAN.md", 
        "docs/DISCOVERY/SUCCESS_CRITERIA.md",
        "docs/DISCOVERY/SCOPE_BASELINE.md"
    ]
    for path in global_paths:
        full_path = os.path.join(REPO_PATH, path)
        if os.path.exists(full_path):
            with open(full_path, "r", encoding="utf-8") as f:
                context_sections.append(f"[{path}]:\n{f.read()[:10000]}")

    # 2. АВТО-ОПРЕДЕЛЕНИЕ ТЕКУЩЕГО БРИФА (По маркеру _current)
    context_sections.append("\n=== CURRENT ACTIVE STAGE BRIEF ===")
    stage_dir = os.path.join(REPO_PATH, "docs/STAGE_BRIEFS/")
    
    if os.path.exists(stage_dir):
        # Ищем файлы, которые содержат '_current' в названии
        briefs = [f for f in os.listdir(stage_dir) if "_current" in f and f.endswith(".md")]
        
        if briefs:
            # Если вдруг таких файлов несколько (ошибка), берем первый из списка
            current_brief = briefs[0] 
            full_path = os.path.join(stage_dir, current_brief)
            try:
                with open(full_path, "r", encoding="utf-8") as f:
                    context_sections.append(f"[ACTIVE TASK LIST - {current_brief}]:\n{f.read()[:1500]}")
            except Exception as e:
                context_sections.append(f"⚠️ Ошибка чтения брифа: {e}")
        else:
            context_sections.append("⚠️ ВНИМАНИЕ: Текущий бриф (*_current.md) не найден в docs/STAGE_BRIEFS/")
    else:
        context_sections.append("⚠️ Директория STAGE_BRIEFS отсутствует.")

    # 3. АРХИТЕКТУРНЫЕ РЕШЕНИЯ (ADR)
    context_sections.append("\n=== ARCHITECTURE DECISIONS (ADR) ===")
    adr_dir = os.path.join(REPO_PATH, "docs/ADR/")
    if os.path.exists(adr_dir):
        adrs = sorted([f for f in os.listdir(adr_dir) if f.startswith("ADR-")], reverse=True)[:3]
        for adr in adrs:
            with open(os.path.join(adr_dir, adr), "r", encoding="utf-8") as f:
                context_sections.append(f"[{adr}]:\n{f.read()[:500]}")

    # 4. ТЕХНИЧЕСКИЙ СТАТУС (Инструменты и Навыки)
    skills_path = os.path.join(REPO_PATH, "docs/skills/")
    if os.path.exists(skills_path):
        skills = [d for d in os.listdir(skills_path) if os.path.isdir(os.path.join(skills_path, d))]
        context_sections.append(f"\n[AVAILABLE SKILLS]: {', '.join(skills)}")

    # 5. Последние записи аудита SSH (короткий хвост)
    log_path = os.path.join(REPO_PATH, "logs/ssh_audit.log")
    if os.path.exists(log_path):
        with open(log_path, "r", encoding="utf-8") as f:
            # Берем последние 1000 символов, чтобы не перегружать контекст
            context_sections.append(f"\n=== RECENT SSH AUDIT LOG ===\n{f.read()[-1000:]}")
    return "\n\n".join(context_sections)


def get_project_structure():
    """Генерирует текстовое дерево проекта для Архитектора"""
    exclude = {'.git', 'venv', '__pycache__', '.codex', 'lib', 'bin', 'include'}
    lines = ["Project Structure:"]
    for root, dirs, files in os.walk(REPO_PATH):
        dirs[:] = [d for d in dirs if d not in exclude]
        level = root.replace(REPO_PATH, '').count(os.sep)
        indent = ' ' * 4 * level
        lines.append(f"{indent}{os.path.basename(root)}/")
        sub_indent = ' ' * 4 * (level + 1)
        for f in files:
            lines.append(f"{sub_indent}{f}")
    # Ограничим по строкам/длине, чтобы не перегружать модель
    return "\n".join(lines)[:2000]


def get_architect_context():
    """Специальный расширенный контекст для Архитектора"""
    # 1. Структура проекта
    structure = get_project_structure()
    
    # 2. Базовый контекст (Master Plan, ADR, Skills, SSH Logs)
    base_context = get_project_context()

    # 3. Проверка ворот качества (Quality Gates)
    q_gates = ""
    q_path = os.path.join(REPO_PATH, "QUALITY_GATES.md")
    if os.path.exists(q_path):
        with open(q_path, "r", encoding="utf-8") as f:
            q_gates = f"\n\n=== QUALITY GATES ===\n{f.read()[:1000]}"
            
    # Убрали несуществующую переменную read_only_data
    return f"{structure}\n\n{base_context}\n{q_gates}"

def call_gemini(model_id, prompt, system_instruction, image_bytes=None):
    try:
        contents = []
        if image_bytes:
            contents.append(types.Part.from_bytes(data=image_bytes, mime_type="image/png"))
        contents.append(prompt)
        response = client_gemini.models.generate_content(
            model=model_id, 
            config=types.GenerateContentConfig(system_instruction=system_instruction), 
             contents=contents
        )
        text = response.text if response and response.text else "⚠️ Пустой ответ."
        

       # --- ЛОГИКА АРХИТЕКТОРА ---
        updated_arch_docs = []
        
        # Список путей, куда Архитектору вход ЗАПРЕЩЕН
        FORBIDDEN_PATHS = ["docs/INSTRUCTIONS", "docs/skills"]

        def is_write_prohibited(path):
            # Проверяем, не начинается ли путь с одного из запрещенных префиксов
            return any(path.startswith(forbidden) for forbidden in FORBIDDEN_PATHS)

        # Обработка ADR (специфический тег)
        if "[WRITE_ADR:" in text:
            parts = text.split("[WRITE_ADR:")[1].split("]")[0].split("|")
            if len(parts) >= 2:
                adr_name, content = parts[0].strip(), "|".join(parts[1:]).strip()
                path = f"docs/ADR/{adr_name}"
                # Тут проверка обычно не нужна (ADR разрешены), но для системности:
                if not is_write_prohibited(path):
                    write_project_file(path, content)
                    updated_arch_docs.append(path)
                    st.toast(f"🏛 ADR зафиксирован: {adr_name}")

        # Универсальный тег записи для Архитектора (теперь он может писать любые файлы в docs)
        # Формат: [WRITE_DOC: path/to/file.md | content]
        if "[WRITE_DOC:" in text:
            parts = text.split("[WRITE_DOC:")[1].split("]")[0].split("|")
            if len(parts) >= 2:
                path, content = parts[0].strip(), "|".join(parts[1:]).strip()
                
                # Проверка: путь должен быть внутри docs и не быть в черном списке
                if path.startswith("docs/") and not is_write_prohibited(path):
                    write_project_file(path, content)
                    updated_arch_docs.append(path)
                    st.toast(f"🏛 Файл обновлен: {path}")
                else:
                    st.error(f"⛔ Доступ запрещен! Архитектор не может изменять: {path}")

        # Специфический тег для Мастер-плана (оставляем для удобства)
        if "[UPDATE_MASTER:" in text:
            content = text.split("[UPDATE_MASTER:")[1].split("]")[0].strip()
            path = "docs/MASTER_PLAN.md"
            write_project_file(path, content)
            updated_arch_docs.append(path)
            st.toast("🏛 MASTER_PLAN обновлен")

        # --- ФИНАЛИЗАЦИЯ (Commit & Push) ---
        if updated_arch_docs:
            git_local_commit("arch: strategic documentation update", file_paths=updated_arch_docs)
            if "[GIT_PUSH]" in text:
                push_res = git_push_to_github()
                st.toast(push_res)
                text += f"\n\n**Системное уведомление:** {push_res}"
                
                # --- ЛОГИКА ЧТЕНИЯ ФАЙЛОВ ПО ЗАПРОСУ ---
        if "[READ_FILE:" in text:
            try:
                # Извлекаем путь: [READ_FILE: src/main.py] -> src/main.py
                file_path_to_read = text.split("[READ_FILE:")[1].split("]")[0].strip()
                full_path = os.path.join(REPO_PATH, file_path_to_read)
                
                if os.path.exists(full_path) and os.path.isfile(full_path):
                    with open(full_path, "r", encoding="utf-8") as f:
                        content = f.read()
                    
                    # Ограничиваем объем, чтобы не "взорвать" контекстное окно
                    if len(content) > 100000:
                        content = content[:100000] + "\n... [Файл обрезан из-за размера]"
                    
                    file_feedback = f"\n\n Содержимое файла `{file_path_to_read}`:\n```python\n{content}\n```"
                    # Добавляем содержимое прямо в текущий ответ, чтобы пользователь видел, 
                    # что Архитектор "прочитал" файл.
                    text += file_feedback
                    st.toast(f"📖 Файл {file_path_to_read} прочитан")
                else:
                    text += f"\n\n⚠️ Ошибка: Файл `{file_path_to_read}` не найден."
            except Exception as e:
                text += f"\n\n❌ Ошибка при чтении: {str(e)}"

        # --- ЛОГИКА АВТОМАТИЧЕСКОГО ЛОГИРОВАНИЯ ---
        if "[LOG_ACTION:" in text:
            # Извлекаем данные между [LOG_ACTION: и ]
            action_data = text.split("[LOG_ACTION:")[1].split("]")[0].strip()
            # Дописываем в историю (функция append_to_history должна быть в коде)
            res = append_to_history(action_data)
            st.toast(res)
            
        return text
    except Exception as e:
        return f"❌ Ошибка Gemini: {str(e)}"

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

# --- 4. UI SETUP ---
st.set_page_config(page_title="Bloom Control Center", layout="wide")

for role in ["arch", "foreman", "critic", "orch"]:
    if f"{role}_history" not in st.session_state:
        st.session_state[f"{role}_history"] = []
if "pending_cmd" not in st.session_state:
    st.session_state.pending_cmd = None
if "critic_report" not in st.session_state:
    st.session_state.critic_report = None


# --- 5. LAYOUT ---
col_arch, col_fore, col_crit, col_orch = st.columns([1, 1, 1, 1.2], gap="small")

with col_arch:
    st.markdown("### 🏛️ Архитектор")
    with st.container(height=500, border=True):
        for m in st.session_state.arch_history:
            st.chat_message(m["role"]).write(m["content"])

    if p := st.chat_input("Глобальная стратегия...", key="in_arch"):
        # 1. Сначала сохраняем сообщение пользователя в историю
        st.session_state.arch_history.append({"role": "user", "content": p})
        
        # 2. Формируем контекст истории (берем последние 10 сообщений ДО текущего)
        # Мы не берем самое последнее сообщение p, так как оно пойдет в CURRENT REQUEST
        history_context = "\n".join([
            f"{'User' if m['role'] == 'user' else 'Architect'}: {m['content']}" 
            for m in st.session_state.arch_history[-11:-1]
        ])

        # 3. Получаем контекст проекта
        full_context = get_architect_context()

        # 4. Собираем финальный промпт
        prompt = f"""
PROJECT CONTEXT & STRUCTURE:
{full_context}

RECENT CHAT HISTORY:
{history_context if history_context else "No previous conversation."}

CURRENT REQUEST:
{p}
"""

        with st.spinner("Архитектор анализирует структуру и документацию..."):
            res = call_gemini(MODEL_PRO, prompt, load_instruction("architect"))
            
        # 5. Сохраняем ответ и обновляем интерфейс
        st.session_state.arch_history.append({"role": "assistant", "content": res})
        st.rerun()

with col_fore:
    st.markdown("### 👷 Прораб")
    up_file = st.file_uploader("Скриншот", type=["png", "jpg", "jpeg"])
    with st.container(height=400, border=True):
        for idx, m in enumerate(st.session_state.foreman_history):
            with st.chat_message(m["role"]):
                st.write(m["content"])
                # ПРОВЕРКА: Если в сообщении есть код, выводим кнопки управления
                if m["role"] == "assistant" and "```bash" in m["content"]:
                    # Извлекаем команду, очищая от лишних символов
                    cmd = m["content"].split("```bash")[1].split("```")[0].strip()
                    
                    c1, c2 = st.columns(2)
                    # Кнопка отправки Критику (не выполняет сразу!)
                    if c1.button("⚖️ Критику", key=f"c_btn_{idx}"):
                        st.session_state.pending_cmd = cmd
                        # Сразу запрашиваем аудит у Gemini
                        with st.spinner("Критик анализирует безопасность..."):
                            # Вместо простого контекста (ADR/DISCOVERY) даем полный срез
                            full_context = get_project_context() # Та самая функция, которую мы обновили
                            prompt = f"""
АНАЛИЗ ВЛИЯНИЯ НА ПРОЕКТ:
Предложенное действие: {cmd}

ГЛОБАЛЬНЫЙ КОНТЕКСТ (Планы, Цели, ADR):
{full_context}

ЗАДАЧА:
Оцени, как это действие соотносится с MASTER_PLAN и не нарушает ли оно архитектурную целостность.
"""
                            report = call_gemini(MODEL_PRO, prompt, load_instruction("critic"))
                            st.session_state.critic_report = report
                        st.rerun()
                    
                    # Кнопка прямой отправки в Оркестратор
                    if c2.button("🚀 В Оркестратор", key=f"o_btn_{idx}"):
                        with st.spinner("Выполнение команды (может занять до 2-х минут)..."):
                            # Увеличиваем таймаут для длительных операций (установка навыков, скачивание)
                            out = execute_ssh(cmd, exec_timeout=120)
                            st.session_state.orch_history.append(f"$ {cmd}\n{out}")
                            feedback = f"РЕЗУЛЬТАТ КОМАНДЫ `{cmd}`:\n```\n{out}\n```"
                            st.session_state.foreman_history.append({"role": "user", "content": feedback})
                        st.rerun()
    if p := st.chat_input("Задание...", key="in_fore"):
        # 1. Сбор контекста (ADR, Код, SSH логи)
        mem, ssh_mem = get_project_context(), get_ssh_recent_memory(5)
        
        # 2. Вызов Gemini
        st.session_state.foreman_history.append({"role": "user", "content": p})
        res = call_gemini(MODEL_PRO, f"{mem}\n\n{ssh_mem}\n\nTask: {p}", load_instruction("foreman"))
        st.session_state.foreman_history.append({"role": "assistant", "content": res})

        # 3. ЛОГИКА АВТО-ПОИСКА НАВЫКОВ
        if "[NEED_SKILL:" in res:
            # Извлекаем запрос между [NEED_SKILL: и ]
            skill_query = res.split("[NEED_SKILL:")[1].split("]")[0].strip()
            st.toast(f"🔎 Оркестратор ищет навык: {skill_query}")
            
            # Оркестратор (Flash) ищет варианты через SkillKit
            search_results = search_skills(skill_query)
            
            # Сохраняем результаты в сессию, чтобы вывести их в окне Оркестратора
            st.session_state.last_cli_output_search = search_results
            
            # Добавляем системное сообщение для тебя/Критика
            orch_msg = f"🤖 Нашел навыки для задачи '{skill_query}'. Выберите лучший для установки ниже."
            st.session_state.orch_history.append(orch_msg)
        
        st.rerun()

with col_crit:
    st.markdown("### 🔍 Критик")
    with st.container(height=500, border=True):
        if st.session_state.pending_cmd:
            st.info(f"**Команда на проверке:**\n`{st.session_state.pending_cmd}`")
            
            # Отображаем отчет, если он есть
            if st.session_state.critic_report:
                st.markdown("#### 📝 Отчет по безопасности:")
                st.write(st.session_state.critic_report)
            
            crit_manual = st.text_input("Дополнительные правки (опционально):", key="crit_man")
            
            st.markdown("---")
            # Ряд кнопок управления
            c1, c2, c3 = st.columns(3)
            
            if c1.button("✅ Approve", help="Выполнить в Оркестраторе"):
                with st.spinner("Выполнение..."):
                    out = execute_ssh(st.session_state.pending_cmd)
                    st.session_state.orch_history.append(f"$ {st.session_state.pending_cmd}\n{out}")
                    st.session_state.foreman_history.append({"role": "user", "content": f"РЕЗУЛЬТАТ `{st.session_state.pending_cmd}`:\n{out}"})
                st.session_state.pending_cmd = None
                st.session_state.critic_report = None
                st.rerun()

            if c2.button("🔄 Revision", help="Отправить Прорабу на пересмотр"):
                feedback = f"КРИТИК ОТКЛОНИЛ КОМАНДУ `{st.session_state.pending_cmd}`.\n\nОТЧЕТ КРИТИКА:\n{st.session_state.critic_report}\n\nПРАВКИ: {crit_manual}"
                st.session_state.foreman_history.append({"role": "user", "content": feedback})
                st.session_state.pending_cmd = None
                st.session_state.critic_report = None
                st.rerun()
                
            if c3.button("❌ Cancel", help="Удалить задачу"):
                st.session_state.pending_cmd = None
                st.session_state.critic_report = None
                st.rerun()
        else:
            st.info("Нет активных задач для проверки.")

with col_orch:
    st.markdown("### 🤖 Оркестратор")
    with st.container(height=400, border=True):
        st.code("\n".join(st.session_state.orch_history), language="bash")

    # Единая кнопка синхронизации и обновления статуса
    if st.button("🔄 Sync & Update Project Status", use_container_width=True, type="primary"):
        with st.spinner("Синхронизация документации и логов..."):
            # 1. Запуск "Слушателя" (Обновление STAGE_B.md на основе HISTORY.log)
            status_msg = sync_docs_and_history() 
            st.toast(status_msg)
            
            # 2. Локальный коммит обновленного брифа и истории
            git_local_commit("docs: update stage progress and history log", 
                             file_paths=["docs/STAGE_BRIEFS/STAGE_B.md", "docs/HISTORY.log"])
            
            # 3. Пуш логов SSH и документов в GitHub
            # Используем нашу изолированную функцию, чтобы не затронуть черновики Прораба
            res = git_sync_logs_only() 
            
            if "✅" in res:
                st.success("Статус обновлен, логи синхронизированы!")
            else:
                st.error(f"Ошибка синхронизации: {res}")
