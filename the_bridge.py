import os
import io
import paramiko
from google import genai
from google.genai import types
from google.cloud import secretmanager

# --- 1. Конфигурация ---
PROJECT_ID = "positive-leaf-462823-h2"
LOCATION = "us-central1"
SECRET_ID = "bloomscape_key" # Проверь это имя в Console!
VM_IP = "34.121.114.145"
VM_USER = "anna_sonny48"
MODEL_ID = "publishers/google/models/gemini-3-pro-preview"

# Путь к твоему JSON-ключу сервисного аккаунта (Оркестратор)
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "key.json"

def get_ssh_key():
    print("--- Step 1: Fetching Key from Secret Manager ---")
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{PROJECT_ID}/secrets/{SECRET_ID}/versions/latest"
    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode("UTF-8")

def ask_gemini(prompt):
    print("--- Step 2: Asking Gemini ---")

    # 1. Инициализация клиента
    client = genai.Client(vertexai=True, project=PROJECT_ID, location=LOCATION)

    # 2. Листинг доступных моделей (перемещено сюда)
    print("--- Listing available models ---")
    try:
        for model in client.models.list():
            print(f"Available: {model.name}")
    except Exception as e:
        print(f"Could not list models: {e}")

    sys_instr = "You are a Linux Expert. Output ONLY the short shell command. No markdown, no comments."

    # 3. Генерация контента
    try:
        response = client.models.generate_content(
            model=MODEL_ID,
            config=types.GenerateContentConfig(system_instruction=sys_instr),
            contents=prompt
        )

        if response.text:
            cmd = response.text.strip().replace('`', '')
            print(f"Gemini suggested: {cmd}")
            return cmd

    except Exception as e:
        print(f"Gemini Error (Vertex AI): {e}")

    return None

def execute_ssh(key_string, command):
    print(f"--- Step 3: Executing on VM ({VM_IP}) ---")
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # Универсальный способ чтения ключа (Auto-detect format)
        key_file_obj = io.StringIO(key_string)
        try:
            # Сначала пробуем RSA
            pkey = paramiko.RSAKey.from_private_key(key_file_obj)
        except paramiko.ssh_exception.SSHException:
            # Если не RSA, пробуем Ed25519 (современный стандарт)
            key_file_obj.seek(0)
            pkey = paramiko.Ed25519Key.from_private_key(key_file_obj)

        ssh.connect(hostname=VM_IP, username=VM_USER, pkey=pkey, timeout=10)
        stdin, stdout, stderr = ssh.exec_command(command)

        res = stdout.read().decode()
        err = stderr.read().decode()
        ssh.close()
        return res if res else err
    except Exception as e:
        return f"SSH Error: {e}"

if __name__ == "__main__":
    print("--- STARTING THE BRIDGE ---")
    try:
        ssh_key = get_ssh_key()
        command_to_run = ask_gemini("Узнать версию Docker")

        if command_to_run:
            output = execute_ssh(ssh_key, command_to_run)
            print("\n--- FINAL RESULT FROM VM ---")
            print(output)
        else:
            print("Failed to get response from AI.")
    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
