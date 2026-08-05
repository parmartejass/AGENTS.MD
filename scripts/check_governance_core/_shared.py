from __future__ import annotations

import logging
import os
import sys
from pathlib import Path
from typing import Tuple

logger = logging.getLogger(__name__)
GIT_LS_FILES_TIMEOUT_SEC = 30
PYTHON_SAFETY_TIMEOUT_SEC = 120


def configure_logging() -> None:
    handler = logging.StreamHandler(stream=sys.stdout)
    handler.setFormatter(logging.Formatter("%(message)s"))
    logger.handlers.clear()
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


def resolve_path(path: str | None, default: Path) -> Path:
    if not path:
        return default.resolve()
    return Path(path).expanduser().resolve()


def context(
    repo_root_arg: str | None, governance_root_arg: str | None, script_root: Path
) -> Tuple[Path, Path, str]:
    governance_root = resolve_path(governance_root_arg, script_root.parent.parent)
    repo_root = resolve_path(repo_root_arg, governance_root)

    if not governance_root.is_dir():
        raise RuntimeError(f"Governance root does not exist or is not a directory: {governance_root}")
    if not repo_root.is_dir():
        raise RuntimeError(f"Repo root does not exist or is not a directory: {repo_root}")

    if repo_root_arg is None and governance_root.name == ".governance":
        raise RuntimeError(
            "RepoRoot is required when running from a vendored governance submodule. "
            "Use --repo-root <target repo root> (for example: --repo-root .)."
        )

    try:
        rel_path = governance_root.relative_to(repo_root)
        rel = "." if str(rel_path) == "." else rel_path.as_posix()
    except ValueError:
        rel = os.path.relpath(governance_root, repo_root).replace("\\", "/")

    governance_rel = "" if rel in {".", ""} else rel
    return repo_root, governance_root, governance_rel
