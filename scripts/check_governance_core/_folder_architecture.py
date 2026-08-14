from __future__ import annotations

import re
from pathlib import Path
from pathlib import PurePosixPath

from scripts.check_governance_core._documents import DocumentStore
from scripts.check_governance_core._inventory import RepositoryInventory


MAX_PYTHON_FILE_LINES = 400
_PYTHON_ROOT_MARKER = re.compile(r"<!--\s*governance-core-python-root:\s*([^>]+?)\s*-->")


def _owner_declared_python_roots(
    governance_root: Path,
    store: DocumentStore,
) -> tuple[tuple[Path, ...], list[str]]:
    owner = governance_root / "docs/project/architecture/architecture.md"
    document, read_error = store.markdown(owner)
    if read_error:
        return (), [read_error]
    assert document is not None
    errors: list[str] = []
    roots: list[Path] = []
    seen: set[str] = set()
    marker_lines = [
        line.strip()
        for _line_no, line in document.operative_lines
        if "governance-core-python-root:" in line
    ]
    for line in marker_lines:
        marker = _PYTHON_ROOT_MARKER.fullmatch(line)
        if marker is None:
            errors.append(f"Invalid governance-core Python root marker in {owner}: {line!r}")
            continue
        value = marker.group(1).strip()
        relative = PurePosixPath(value)
        if (
            not value
            or "\\" in value
            or ":" in value
            or relative.is_absolute()
            or relative.as_posix() != value
            or any(part in {"", ".", ".."} or part != part.rstrip(" .") for part in relative.parts)
        ):
            errors.append(f"Invalid governance-core Python root in {owner}: {value!r}")
            continue
        key = value.casefold()
        if key in seen:
            errors.append(f"Duplicate governance-core Python root in {owner}: {value}")
            continue
        seen.add(key)
        candidate = governance_root
        for part in relative.parts:
            try:
                exact = next((child for child in candidate.iterdir() if child.name == part), None)
            except OSError as exc:
                errors.append(f"Unable to inspect declared governance-core Python root {value}: {exc}")
                exact = None
                break
            if exact is None:
                errors.append(
                    f"Declared governance-core Python root is missing or noncanonical: {value}"
                )
                break
            candidate = exact
        else:
            if not candidate.is_dir():
                errors.append(f"Declared governance-core Python root is not a directory: {candidate}")
                continue
            roots.append(candidate)
            continue
    if not roots:
        errors.append(f"{owner} must declare at least one governance-core-python-root marker")
    return tuple(roots), errors


def check_folder_architecture(
    governance_root: Path,
    store: DocumentStore,
    inventory: RepositoryInventory,
) -> tuple[list[str], list[str]]:
    """Validate the repository-owned Python structure without a shadow scope registry."""

    errors: list[str] = []
    warnings: list[str] = []
    scripts_root = governance_root / "scripts"
    if not scripts_root.is_dir():
        return [f"Missing scripts root: {scripts_root}"], warnings

    tree, tree_error = inventory.tree_entries(governance_root)
    if tree_error:
        return [tree_error], warnings
    entries = tuple(
        entry for entry in tree if entry.path == scripts_root or scripts_root in entry.path.parents
    )
    for path in (
        entry.path
        for entry in entries
        if not entry.is_directory
        and entry.path.parent == scripts_root
        and entry.path.suffix.lower() == ".py"
    ):
        errors.append(f"Top-level Python script must move behind scripts/<feature>/<feature>_main.py: {path}")

    for directory in (
        entry.path
        for entry in entries
        if entry.is_directory and entry.path.parent == scripts_root
    ):
        if directory.name.startswith(".") or directory.name == "__pycache__":
            continue
        direct_python = tuple(
            entry.path
            for entry in entries
            if not entry.is_directory
            and entry.path.parent == directory
            and entry.path.suffix.lower() == ".py"
        )
        if direct_python and not (directory / f"{directory.name}_main.py").is_file():
            errors.append(f"Script feature is missing its public entrypoint: scripts/{directory.name}/{directory.name}_main.py")

    files, inventory_error = inventory.python_files(governance_root)
    if inventory_error:
        return [inventory_error, *errors], warnings
    allowed_roots, policy_errors = _owner_declared_python_roots(governance_root, store)
    errors.extend(policy_errors)
    for path in files:
        if allowed_roots and not any(path == root or root in path.parents for root in allowed_roots):
            errors.append(
                "Python file is outside owner-declared governance source roots: "
                f"{path.relative_to(governance_root).as_posix()}"
            )
        text, read_error = store.read_text(path)
        if read_error:
            errors.append(read_error)
            continue
        assert text is not None
        line_count = len(text.splitlines())
        if line_count > MAX_PYTHON_FILE_LINES:
            warnings.append(
                f"Python file exceeds the {MAX_PYTHON_FILE_LINES}-line decomposition review trigger: "
                f"{path.relative_to(governance_root).as_posix()} ({line_count} lines)"
            )
    return errors, warnings
