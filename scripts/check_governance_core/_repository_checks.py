from __future__ import annotations

import re
from pathlib import Path

from scripts.check_governance_core._documents import DocumentStore
from scripts.check_governance_core._inventory import RepositoryInventory


_NOISE = re.compile(r"(^|/)(__pycache__|\.DS_Store|Thumbs\.db)(/|$)", re.IGNORECASE)
_BYTECODE = re.compile(r"\.(pyc|pyo)$", re.IGNORECASE)
_SECRET = re.compile(r"(^|/)(\.env(?:\.(?:local|dev|prod|test))?|[^/]*(?:token|secret|credential)[^/]*\.(?:json|txt|env|ini|toml|ya?ml))$", re.IGNORECASE)
_CITATION = re.compile("(?:\ue200|îˆ€)(?:cite|entity|image_group)")


def check_repository(
    repo_root: Path,
    store: DocumentStore,
    inventory: RepositoryInventory,
    *,
    enforce_tracked_ignored: bool = False,
) -> list[str]:
    tracked, inventory_error = inventory.tracked_paths(repo_root)
    if inventory_error:
        return [inventory_error]
    errors: list[str] = []
    tracked_ignored: set[str] = set()
    if enforce_tracked_ignored:
        ignored, ignored_error = inventory.tracked_ignored_paths(repo_root)
        if ignored_error:
            return [ignored_error]
        tracked_ignored = {value.replace("\\", "/").casefold() for value in ignored}
    for value in tracked:
        normalized = value.replace("\\", "/")
        if normalized.casefold() in tracked_ignored:
            errors.append(f"Tracked local-only/ignored file: {value}")
        elif _NOISE.search(normalized) or _BYTECODE.search(normalized):
            errors.append(f"Tracked generated/noise file: {value}")
        elif _SECRET.search(normalized):
            errors.append(f"Tracked secret-like file: {value}")

    docs_root = repo_root / "docs"
    if docs_root.is_dir():
        markdown_files, markdown_error = inventory.markdown_files(docs_root)
        if markdown_error:
            errors.append(markdown_error)
            return errors
        for path in markdown_files:
            text, read_error = store.read_text(path)
            if read_error:
                errors.append(read_error)
                continue
            assert text is not None
            for line_no, line in enumerate(text.splitlines(), start=1):
                if _CITATION.search(line):
                    errors.append(f"Unresolved citation token in {path.relative_to(repo_root).as_posix()}:{line_no}")
    return errors
