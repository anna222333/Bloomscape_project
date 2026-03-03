# app/core/skill_engine.py
import os
import subprocess
import streamlit as st
from skillkit import SkillManager
from app.config import MODEL_PRO

# Инициализация SkillManager
def initialize_skill_manager():
    """
    Инициализирует SkillManager и создает необходимые директории.
    """
    try:
        if not os.path.exists("docs/skills/"):
            os.makedirs("docs/skills/", exist_ok=True)
        skill_manager = SkillManager()
        skill_manager.discover()
        return skill_manager
    except Exception as e:
        st.error(f"Ошибка SkillKit: {e}")
        return None

def load_instruction(role, skill_manager):
    """
    Загрузка инструкций для роли с подключением навыков.
    """
    base_text = ""
    path = f"docs/INSTRUCTIONS/{role}.txt"
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            base_text = f.read()
    else:
        base_text = f"You are the {role}. Act professionally as a member of the Bloomscape team."
    
    role_map = {
        "architect": ["system-design", "adr-writer"],
        "foreman": ["python-expert", "adr-writer", "bash-wizard"],
        "critic": ["security-auditor", "code-review"],
        "orch": ["bash-wizard"]
    }
    
    extra_skills = role_map.get(role, [])
    skills_content = ""

    # skill_manager может быть None если SkillKit не инициализировался
    if skill_manager is not None:
        for skill_name in extra_skills:
            try:
                skill = skill_manager.get_skill(skill_name)
                if skill:
                    skills_content += f"\n\n[CAPABILITY: {skill_name.upper()}]\n{skill.content}"
            except:
                continue

    return base_text + "\n\n" + skills_content

def search_skills(query, credentials, oslogin_service):
    """
    Поиск навыков через SkillKit.
    """
    try:
        from app.core.ssh_executor import execute_ssh
        command = f"skillkit find \"{query}\" || npx -y skillkit@latest find \"{query}\""
        return execute_ssh(command, credentials, oslogin_service, exec_timeout=60)
    except Exception as e:
        return f"❌ Ошибка поиска: {str(e)}"

def critic_verify_skill(skill_list, user_task, skill_manager, call_gemini_fn):
    """
    Критик анализирует найденные навыки на безопасность и соответствие проекту.

    Args:
        skill_list: Список найденных навыков (строка или список)
        user_task: Задача пользователя
        skill_manager: SkillManager instance
        call_gemini_fn: Функция вызова LLM (передаётся снаружи, без кругового импорта)
    """
    prompt = f"Пользователь хочет: {user_task}. SkillKit нашел: {skill_list}. Какой из них безопасен и лучше всего подходит? Ответь кратко."
    return call_gemini_fn(MODEL_PRO, prompt, load_instruction("critic", skill_manager))

def install_new_skill_everywhere(repo_path, skill_name=None, skill_manager=None, credentials=None, oslogin_service=None):
    """
    Автоматическая установка навыка на ВМ и на локальную машину одновременно.
    """
    from app.core.ssh_executor import execute_ssh
    skill_arg = f"--skills {skill_name}" if skill_name else "--all"
    base_command = f"npx -y skillkit@latest install {repo_path} {skill_arg}"
    final_command = f"yes | {base_command}"
    
    results = []
    
    with st.spinner(f"Установка на ВМ: {repo_path}..."):
        remote_out = execute_ssh(final_command, credentials, oslogin_service, exec_timeout=180)
        results.append(f"🖥️ **VM Output:**\n{remote_out}")
    
    with st.spinner(f"Локальная синхронизация навыка..."):
        try:
            loc_res = subprocess.run(final_command, shell=True, capture_output=True, text=True, timeout=180)
            if loc_res.returncode == 0:
                results.append(f"💻 **Local Output:**\n✅ Успешно установлено локально.")
                if skill_manager:
                    skill_manager.discover(path="docs/skills/")
            else:
                results.append(f"💻 **Local Output:**\n❌ Ошибка: {loc_res.stderr}")
        except subprocess.TimeoutExpired:
            results.append(f"💻 **Local Output:**\n❌ Ошибка: Timeout при локальной установке (>3 мин)")
        except Exception as e:
            results.append(f"💻 **Local Output:**\n❌ Ошибка локального процесса: {str(e)}")
    
    st.toast(f"Процесс установки завершен для {repo_path}")
    return "\n\n".join(results)
