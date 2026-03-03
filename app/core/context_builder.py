# app/core/context_builder.py
import os
import streamlit as st
from app.config import REPO_PATH

class ProjectFileManager:
    """
    Единый класс для безопасной работы с файловой системой проекта.
    Проверяет запрещённые пути перед записью.
    """
    
    # Пути, куда запрещена запись (защищённые системные директории)
    FORBIDDEN_PATHS = ["docs/INSTRUCTIONS", "docs/skills"]
    
    @staticmethod
    def is_write_prohibited(file_path):
        """
        Проверяет, разрешена ли запись в указанный путь.
        
        Args:
            file_path: Путь файла для проверки
        
        Returns:
            True если запись запрещена, False если разрешена
        """
        return any(file_path.startswith(forbidden) for forbidden in ProjectFileManager.FORBIDDEN_PATHS)
    
    @staticmethod
    def write_file(file_path, content, check_forbidden=True):
        """
        Безопасно записывает содержимое в файл проекта.
        
        Args:
            file_path: Относительный путь файла (от корня проекта)
            content: Содержимое для записи
            check_forbidden: Проверлять ли запрещённые пути
        
        Returns:
            True если успешно, False если ошибка
        """
        try:
            # Проверка запрещённых путей
            if check_forbidden and ProjectFileManager.is_write_prohibited(file_path):
                st.error(f"⛔ Доступ запрещен! Нельзя изменять: {file_path}")
                return False
            
            # Защита от выхода за пределы проекта
            full_path = os.path.abspath(os.path.join(REPO_PATH, file_path))
            if not full_path.startswith(os.path.abspath(REPO_PATH)):
                st.error(f"⛔ Попытка записи вне репозитория: {file_path}")
                return False
            
            # Создание директорий и запись файла
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(content)
            return True
        except Exception as e:
            st.error(f"❌ Ошибка записи файла {file_path}: {str(e)}")
            return False
    
    @staticmethod
    def read_file(file_path):
        """
        Читает содержимое файла проекта.
        
        Args:
            file_path: Относительный путь файла
        
        Returns:
            Содержимое файла или None если ошибка
        """
        try:
            full_path = os.path.abspath(os.path.join(REPO_PATH, file_path))
            if not full_path.startswith(os.path.abspath(REPO_PATH)):
                st.error(f"⛔ Попытка чтения вне репозитория: {file_path}")
                return None
            
            if not os.path.exists(full_path) or not os.path.isfile(full_path):
                return None
            
            with open(full_path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            st.error(f"❌ Ошибка чтения файла {file_path}: {str(e)}")
            return None

@st.cache_data(ttl=60)
def get_project_context():
    """
    Собирает контекст проекта из документации, ADR, навыков и логов.
    Включает глобальные цели, активные задачи, архитектурные решения и логи.
    Кешируется на 60 секунд — файлы проекта меняются редко.
    """
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
        briefs = [f for f in os.listdir(stage_dir) if "_current" in f and f.endswith(".md")]
        
        if briefs:
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
            context_sections.append(f"\n=== RECENT SSH AUDIT LOG ===\n{f.read()[-1000:]}")
    
    return "\n\n".join(context_sections)

def get_project_structure():
    """
    Генерирует текстовое дерево структуры проекта для Архитектора.
    Исключает системные директории (git, venv, etc).
    """
    exclude = {'.git', 'venv', '__pycache__', '.codex', 'lib', 'bin', 'include', 'node_modules'}
    lines = ["Project Structure:"]
    
    for root, dirs, files in os.walk(REPO_PATH):
        dirs[:] = [d for d in dirs if d not in exclude]
        level = root.replace(REPO_PATH, '').count(os.sep)
        indent = ' ' * 4 * level
        lines.append(f"{indent}{os.path.basename(root)}/")
        sub_indent = ' ' * 4 * (level + 1)
        for f in files:
            lines.append(f"{sub_indent}{f}")
    
    return "\n".join(lines)[:2000]

@st.cache_data(ttl=60)
def get_architect_context():
    """
    Собирает расширенный контекст для Архитектора:
    структуру проекта, документацию, решения (ADR) и ворота качества.
    Кешируется на 60 секунд.
    """
    # 1. Структура проекта
    structure = get_project_structure()
    
    # 2. Базовый контекст (Master Plan, ADR, Skills, SSH Logs)
    base_context = get_project_context()

    # 3. Проверка ворот качества (Quality Gates)
    q_gates = ""
    q_path = os.path.join(REPO_PATH, "docs/QUALITY_GATES.md")
    if os.path.exists(q_path):
        with open(q_path, "r", encoding="utf-8") as f:
            q_gates = f"\n\n=== QUALITY GATES ===\n{f.read()[:1000]}"
    
    return f"{structure}\n\n{base_context}\n{q_gates}"
