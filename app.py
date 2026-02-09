import streamlit as st
import os
import io
import datetime
import base64
import json
import time
import paramiko
from google import genai
from google.genai import types
from google.cloud import secretmanager
from vertexai.preview.vision_models import ImageGenerationModel
from git import Repo

# --- 1. CONFIGURATION ---
PROJECT_ID = "positive-leaf-462823-h2"
LOCATION = "us-central1"
SECRET_ID = "bloomscape_key"
VM_IP = "34.121.114.145"
VM_USER = "anna_sonny48"
REPO_PATH = "./"
GEMINI_API_KEY = "AIzaSyDWXjNwZlv7k2B2WmxAdI9aCVFeDiF3blg"
SSH_LOG_FILE = "logs/ssh_audit.log"

MODEL_PRO = "models/gemini-3-pro-preview"
MODEL_FLASH = "models/gemini-3-flash-preview"

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "key.json"

# --- 2. CLIENTS INITIALIZATION ---
client_gemini = genai.Client(api_key=GEMINI_API_KEY)

# --- 3. CORE FUNCTIONS ---

def load_instruction(role):
    path = f"docs/instructions/{role}.txt"
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    return f"You are the {role}. Act professionally based on project context."

def get_ssh_key():
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{PROJECT_ID}/secrets/{SECRET_ID}/versions/latest"
    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode("UTF-8")

def execute_ssh(command):
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
        stdin, stdout, stderr = ssh.exec_command(command, get_pty=True)
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

def get_ssh_recent_memory(n=5):
    if not os.path.exists(SSH_LOG_FILE):
        return "История SSH пуста."
    try:
        with open(SSH_LOG_FILE, "r", encoding="utf-8") as f:
            entries = f.read().split('-'*40)
            recent = [e.strip() for e in entries if e.strip()][-n:]
            return "\n\n--- ПОСЛЕДНИЕ ДЕЙСТВИЯ НА СЕРВЕРЕ ---\n" + "\n---\n".join(recent) if recent else "Нет недавних команд."
    except Exception as e:
        return f"Ошибка чтения лога: {e}"

def sync_to_git(commit_message, file_path):
    """Синхронизация с глубокой очисткой битых объектов индекса"""
    try:
        if not os.path.exists("git.txt"): return "❌ git.txt не найден"
        with open("git.txt", "r") as f: token = f.read().strip()

        os.environ['GIT_TERMINAL_PROMPT'] = '0'
        repo = Repo(REPO_PATH)

        # 1. Настройка авторизации
        remote_url = repo.remotes.origin.url
        clean_url = remote_url.split('@')[-1].replace("https://", "")
        auth_url = f"https://{token}@{clean_url}"
        repo.remotes.origin.set_url(auth_url)

        # 2. ОЧИСТКА ИНДЕКСА (Лечение hasDot ошибки)
        # Это удаляет битый объект 7f6ce8... из очереди
        repo.git.reset()

        # 3. Принудительное добавление
        repo.git.add(file_path, force=True)

        if not repo.is_dirty(untracked_files=True):
            return "ℹ️ Изменений не обнаружено после сброса индекса."

        # 4. Создание коммита
        repo.index.commit(commit_message)
        current_branch = repo.active_branch.name

        # 5. Пуш с явным указанием ветки
        # Если обычный пуш не пройдет, здесь можно добавить флаг force=True
        repo.git.push(auth_url, current_branch)

        # Возврат URL для безопасности
        repo.remotes.origin.set_url(remote_url)

        return f"✅ {file_path} синхронизирован!"
    except Exception as e:
        return f"❌ Git Error: {str(e)}"
def get_project_context():
    context_text = "CURRENT PROJECT CONTEXT (ADR & DISCOVERY):\n"
    for path in ["docs/ADR/", "docs/DISCOVERY/"]:
        full_path = os.path.join(REPO_PATH, path)
        if os.path.exists(full_path):
            files = sorted([f for f in os.listdir(full_path) if f.endswith(".md")], reverse=True)[:3]
            for file in files:
                with open(os.path.join(full_path, file), "r", encoding="utf-8") as f:
                    context_text += f"\n--- File: {file} ---\n{f.read()[:1500]}\n"
    return context_text

def call_gemini(model_id, prompt, system_instruction, image_bytes=None):
    try:
        contents = []
        if image_bytes:
            contents.append(types.Part.from_bytes(data=image_bytes, mime_type="image/png"))
        contents.append(prompt)
        response = client_gemini.models.generate_content(
            model=model_id, config=types.GenerateContentConfig(system_instruction=system_instruction), contents=contents
        )
        return response.text if response and response.text else "⚠️ Пустой ответ."
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

# --- 5. LAYOUT ---
col_arch, col_fore, col_crit, col_orch = st.columns([1, 1, 1, 1.2], gap="small")

with col_arch:
    st.markdown("### 🏛️ Архитектор")
    with st.container(height=500, border=True):
        for m in st.session_state.arch_history:
            st.chat_message(m["role"]).write(m["content"])
    if p := st.chat_input("Глобальная стратегия...", key="in_arch"):
        st.session_state.arch_history.append({"role": "user", "content": p})
        res = call_gemini(MODEL_PRO, p, load_instruction("architect"))
        st.session_state.arch_history.append({"role": "assistant", "content": res})
        st.rerun()

with col_fore:
    st.markdown("### 👷 Прораб")
    up_file = st.file_uploader("Скриншот", type=["png", "jpg", "jpeg"])
    with st.container(height=400, border=True):
        for idx, m in enumerate(st.session_state.foreman_history):
            with st.chat_message(m["role"]):
                st.write(m["content"])
                if m["role"] == "assistant" and "```bash" in m["content"]:
                    cmd = m["content"].split("```bash")[1].split("```")[0].strip()
                    c1, c2 = st.columns(2)
                    if c1.button("⚖️ Критику", key=f"c_btn_{idx}"):
                        st.session_state.pending_cmd = cmd
                    if c2.button("🚀 В Оркестратор", key=f"o_btn_{idx}"):
                        with st.spinner("Executing..."):
                            out = execute_ssh(cmd)
                            st.session_state.orch_history.append(f"$ {cmd}\n{out}")
                            feedback = f"РЕЗУЛЬТАТ КОМАНДЫ `{cmd}`:\n```\n{out}\n```"
                            st.session_state.foreman_history.append({"role": "user", "content": feedback})
                        st.rerun()
    if p := st.chat_input("Задание...", key="in_fore"):
        mem, ssh_mem = get_project_context(), get_ssh_recent_memory(5)
        st.session_state.foreman_history.append({"role": "user", "content": p})
        res = call_gemini(MODEL_PRO, f"{mem}\n\n{ssh_mem}\n\nTask: {p}", load_instruction("foreman"), image_bytes=(up_file.read() if up_file else None))
        st.session_state.foreman_history.append({"role": "assistant", "content": res})
        if res and "generate image" in res.lower():
            st.session_state.orch_history.append(generate_image_with_imagen(res))
        st.rerun()

    if st.button("📦 Global Sync (Code/ADR)", use_container_width=True):
        with st.spinner("Pushing global changes..."):
            summary = call_gemini(MODEL_PRO, f"History: {st.session_state.foreman_history[-2:]}", "Summarize for commit.")
            st.toast(sync_to_git(f"feat: {summary[:50]}", "docs/ADR/"))

with col_crit:
    st.markdown("### 🔍 Критик")
    with st.container(height=500, border=True):
        if st.session_state.pending_cmd:
            st.warning(f"На проверке: `{st.session_state.pending_cmd}`")
            crit_manual = st.text_input("Ручные правки:", key="crit_man")
            c1, c2 = st.columns(2)
            if c1.button("✅ Approve", use_container_width=True):
                with st.spinner("Executing..."):
                    out = execute_ssh(st.session_state.pending_cmd)
                    st.session_state.orch_history.append(f"$ {st.session_state.pending_cmd}\n{out}")
                    st.session_state.foreman_history.append({"role": "user", "content": f"РЕЗУЛЬТАТ `{st.session_state.pending_cmd}`:\n{out}"})
                st.session_state.pending_cmd = None
                st.rerun()
            if c2.button("❌ Reject", use_container_width=True):
                if crit_manual: st.session_state.foreman_history.append({"role": "user", "content": f"КРИТИКА: {crit_manual}"})
                st.session_state.pending_cmd = None
                st.rerun()
        else: st.info("Нет задач.")

with col_orch:
    st.markdown("### 🤖 Оркестратор")
    with st.container(height=400, border=True):
        st.code("\n".join(st.session_state.orch_history), language="bash")
    if st.button("🧹 Clear Terminal", use_container_width=True):
        st.session_state.orch_history = []; st.rerun()

    if st.button("📦 Sync Audit Log to Git", use_container_width=True):
        with st.spinner("Pushing audit log..."):
            # Теперь пушит ровно по пути logs/ssh_audit.log
            status = sync_to_git(
                commit_message=f"audit: log update {datetime.datetime.now()}",
                file_path=SSH_LOG_FILE
            )
            st.toast(status)
