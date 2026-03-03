"""
Chat History Manager

Provides load/save operations for persistent multi-agent chat history.
History is stored as a JSON file at the project root.

Format:
{
  "arch_history":    [{"role": "user"|"assistant", "content": "..."}, ...],
  "foreman_history": [{"role": "user"|"assistant", "content": "..."}, ...],
  "orch_history":    ["$ command\noutput", ...]   <- list of strings
}
"""

import json
import os
import tempfile

from app.config import REPO_PATH

CHAT_HISTORY_FILE = os.path.join(REPO_PATH, "chat_history.json")

# Keys that will be persisted
HISTORY_KEYS = ("arch_history", "foreman_history", "orch_history")


def load_history() -> dict:
    """
    Load chat history from JSON file.

    Returns a dict with whichever of HISTORY_KEYS are present in the file.
    Returns an empty dict if the file is absent, unreadable or in an old
    flat-list format.
    """
    if not os.path.exists(CHAT_HISTORY_FILE):
        return {}
    try:
        with open(CHAT_HISTORY_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError:
        # Preserve the corrupted file so it isn't silently overwritten later
        os.rename(CHAT_HISTORY_FILE, CHAT_HISTORY_FILE + ".corrupted.bak")
        return {}
    except IOError:
        return {}

    # Old format was a flat list (single-agent) — ignore it to avoid type errors
    if not isinstance(data, dict):
        return {}

    return {k: data[k] for k in HISTORY_KEYS if k in data}


def save_history(histories: dict) -> None:
    """
    Save chat histories to JSON file.

    Args:
        histories: dict mapping history key → list, e.g.
                   {"arch_history": [...], "foreman_history": [...], "orch_history": [...]}
    """
    payload = {k: histories.get(k, []) for k in HISTORY_KEYS}
    try:
        # Write to a temp file on the same filesystem, then atomically replace
        dir_name = os.path.dirname(CHAT_HISTORY_FILE)
        fd, temp_path = tempfile.mkstemp(dir=dir_name, text=True)
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
        os.replace(temp_path, CHAT_HISTORY_FILE)
    except IOError as e:
        pass  # Saving is best-effort; never crash the app
