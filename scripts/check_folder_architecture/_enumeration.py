from __future__ import annotations

import subprocess
from pathlib import Path

from _issues import Issue
from _paths import is_excluded_non_git_python_path


def iter_repo_python_files(root: Path, issues: list[Issue]) -> list[Path]:
    if not (root / ".git").exists():
        return sorted(
            path
            for path in root.rglob("*.py")
            if not is_excluded_non_git_python_path(path, root)
        )
    command = [
        "git",
        "-C",
        str(root),
        "ls-files",
        "--cached",
        "--others",
        "--exclude-standard",
        "--",
        "*.py",
    ]
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True, cwd=root, timeout=10)
    except FileNotFoundError:
        issues.append(Issue(path="git", message="git is required for deterministic Python file enumeration."))
        return []
    except subprocess.TimeoutExpired:
        issues.append(Issue(path="git", message="git ls-files timed out during Python file enumeration."))
        return []
    except subprocess.CalledProcessError as exc:
        details = " ".join(part.strip() for part in (exc.stderr, exc.stdout) if part and part.strip())
        if details:
            issues.append(
                Issue(path="git", message=f"git ls-files failed during Python file enumeration: {details[:500]}")
            )
        else:
            issues.append(Issue(path="git", message=f"git ls-files failed during Python file enumeration: {exc}"))
        return []
    paths: list[Path] = []
    for raw in result.stdout.splitlines():
        if not raw.strip():
            continue
        path = root / raw.strip()
        if path.is_file():
            paths.append(path)
    return sorted(paths)
