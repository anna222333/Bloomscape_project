# app/core/git_manager.py
import os
import datetime
from functools import lru_cache
from git import Repo
from app.config import REPO_PATH
import streamlit as st
from app.core.logger import history_logger

GCP_PROJECT_ID = os.getenv("PROJECT_ID", "positive-leaf-462823-h2")
GITHUB_PAT_SECRET = os.getenv("GITHUB_PAT_SECRET_NAME", "github-pat")


def _get_github_token() -> str:
    """
    Получает GitHub PAT из Google Secret Manager через ADC.
    Токен никогда не хранится на диске — запрашивается при каждом пуше.
    """
    try:
        from google.cloud import secretmanager
        client = secretmanager.SecretManagerServiceClient()
        name = f"projects/{GCP_PROJECT_ID}/secrets/{GITHUB_PAT_SECRET}/versions/latest"
        response = client.access_secret_version(request={"name": name})
        return response.payload.data.decode("utf-8").strip()
    except Exception as e:
        raise RuntimeError(f"Secret Manager недоступен: {e}")


def _build_auth_url(repo: Repo, token: str) -> str:
    """Встраивает токен в remote URL, не изменяя сохранённый origin."""
    base_url = repo.remotes.origin.url
    # Удаляем старый токен, если он уже есть в URL
    if "@" in base_url:
        base_url = "https://" + base_url.split("@")[-1]
    elif base_url.startswith("https://"):
        base_url = base_url
    return base_url.replace("https://", f"https://{token}@")

def git_local_commit(commit_message, file_paths=None):
    """
    Фиксация стратегических изменений.
    """
    try:
        repo = Repo(REPO_PATH)
        if file_paths:
            for fp in file_paths:
                repo.git.add(os.path.normpath(fp).lstrip('./'))
        else:
            repo.git.add(A=True)
        if repo.is_dirty(untracked_files=True):
            repo.index.commit(commit_message)
            history_logger.log_git_operation("commit", str(file_paths), commit_message)
            return f"✅ Коммит: {commit_message}"
        return "ℹ️ Нет изменений"
    except Exception as e:
        history_logger.log_git_operation("commit_error", str(file_paths), str(e))
        return f"❌ Git Error: {e}"

def git_push_to_github():
    """
    Пуш накопленных коммитов в удалённый репозиторий.
    PAT получается из GCP Secret Manager через ADC — не хранится на диске.
    Перед pull --rebase прячет незакоммиченные изменения в stash и восстанавливает после.
    """
    stashed = False
    try:
        token = _get_github_token()
        repo = Repo(REPO_PATH)
        auth_url = _build_auth_url(repo, token)
        current_branch = repo.active_branch.name
        # Прячем незакоммиченные изменения — иначе rebase откажет
        if repo.is_dirty(untracked_files=False):
            repo.git.stash('save', 'temp_before_push')
            stashed = True
        repo.git.pull(auth_url, current_branch, "--rebase")
        repo.git.push(auth_url, current_branch)
        if stashed:
            repo.git.stash('pop')
        history_logger.log_git_operation("push", message=f"Branch: {current_branch}")
        return "🚀 Все изменения успешно отправлены на GitHub!"
    except Exception as e:
        if stashed:
            try:
                Repo(REPO_PATH).git.stash('pop')
            except Exception:
                pass
        history_logger.log_git_operation("push_error", message=str(e))
        safe_error = str(e).replace(_get_safe_token_prefix(), "***")
        return f"❌ Ошибка Push: {safe_error}"

def git_sync_logs_only():
    """
    Оркестратор: работает ТОЛЬКО с файлом логов, не трогая код.
    PAT получается из GCP Secret Manager через ADC — не хранится на диске.
    """
    log_file = "logs/ssh_audit.log"
    try:
        token = _get_github_token()
        repo = Repo(REPO_PATH)
        stashed = False
        if repo.is_dirty():
            repo.git.stash('save', 'temp_before_logs')
            stashed = True
        repo.git.add(log_file)
        repo.index.commit(f"sys: update ssh logs {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}")
        auth_url = _build_auth_url(repo, token)
        repo.git.pull(auth_url, repo.active_branch.name, "--rebase")
        repo.git.push(auth_url, repo.active_branch.name)
        if stashed:
            repo.git.stash('pop')
        return "✅ Логи SSH синхронизированы."
    except Exception as e:
        return f"❌ Ошибка логов: {str(e)}"


def _get_safe_token_prefix() -> str:
    """Возвращает первые 8 символов токена для фильтрации из логов."""
    try:
        return _get_github_token()[:8]
    except Exception:
        return "github_p"
