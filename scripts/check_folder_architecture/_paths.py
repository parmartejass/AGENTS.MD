from __future__ import annotations

from pathlib import Path


NON_GIT_EXCLUDED_DIRS = {".git", "__pycache__", ".venv", "venv"}
NON_GIT_EXCLUDED_PREFIXES = (".tmp",)


def is_excluded_non_git_python_path(path: Path, root: Path) -> bool:
    for part in path.relative_to(root).parts:
        if part in NON_GIT_EXCLUDED_DIRS:
            return True
        if any(part.startswith(prefix) for prefix in NON_GIT_EXCLUDED_PREFIXES):
            return True
    return False
