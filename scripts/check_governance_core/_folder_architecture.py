from __future__ import annotations

import re
from pathlib import Path
from pathlib import PurePosixPath

from scripts.check_governance_core._documents import DocumentStore, MarkdownDocument
from scripts.check_governance_core._inventory import RepositoryInventory


_ROOT_TOKEN = "governance-core-python-root:"
_EXCEPTION_TOKEN = "governance-core-python-package-exception:"
_PYTHON_ROOT_MARKER = re.compile(r"<!--\s*governance-core-python-root:\s*([^>]+?)\s*-->")
_PACKAGE_EXCEPTION_MARKER = re.compile(r"<!--\s*governance-core-python-package-exception:\s*([^>]+?)\s*-->")
_PACKAGE_ENTRY = "__init__.py"


def _marker_values(
    document: MarkdownDocument,
    owner: Path,
    *,
    token: str,
    pattern: re.Pattern[str],
    label: str,
) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    values: list[str] = []
    seen: set[str] = set()
    for line in (line.strip() for _line_no, line in document.operative_lines if token in line):
        marker = pattern.fullmatch(line)
        if marker is None:
            errors.append(f"Invalid {label} marker in {owner}: {line!r}")
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
            errors.append(f"Invalid {label} in {owner}: {value!r}")
            continue
        key = value.casefold()
        if key in seen:
            errors.append(f"Duplicate {label} in {owner}: {value}")
            continue
        seen.add(key)
        values.append(value)
    return values, errors


def _owner_declared_python_roots(
    governance_root: Path,
    store: DocumentStore,
) -> tuple[tuple[Path, ...], frozenset[Path], list[str]]:
    owner = governance_root / "docs/project/architecture/architecture.md"
    document, read_error = store.markdown(owner)
    if read_error:
        return (), frozenset(), [read_error]
    assert document is not None
    values, errors = _marker_values(
        document, owner, token=_ROOT_TOKEN, pattern=_PYTHON_ROOT_MARKER, label="governance-core Python root"
    )
    exceptions, exception_errors = _marker_values(
        document,
        owner,
        token=_EXCEPTION_TOKEN,
        pattern=_PACKAGE_EXCEPTION_MARKER,
        label="governance-core packaged-folder exception",
    )
    errors.extend(exception_errors)
    roots: dict[str, Path] = {}
    for value in values:
        candidate = governance_root
        for part in PurePosixPath(value).parts:
            try:
                exact = next((child for child in candidate.iterdir() if child.name == part), None)
            except OSError as exc:
                errors.append(f"Unable to inspect declared governance-core Python root {value}: {exc}")
                break
            if exact is None:
                errors.append(f"Declared governance-core Python root is missing or noncanonical: {value}")
                break
            candidate = exact
        else:
            if not candidate.is_dir():
                errors.append(f"Declared governance-core Python root is not a directory: {candidate}")
                continue
            roots[value] = candidate
    if not roots:
        errors.append(f"{owner} must declare at least one governance-core-python-root marker")
    for value in exceptions:
        if value not in values:
            errors.append(
                f"Declared governance-core packaged-folder exception is not a declared Python root: {value}"
            )
    return tuple(roots.values()), frozenset(roots[value] for value in exceptions if value in roots), errors


def _package_structure_errors(
    path: Path,
    root: Path,
    governance_root: Path,
    python_dirs: set[Path],
    package_dirs: set[Path],
) -> list[str]:
    """Record one module's package ancestry below an enforced source root."""

    if any(part.startswith(".") or part == "__pycache__" for part in path.relative_to(root).parts):
        return []
    relative = path.relative_to(governance_root).as_posix()
    if path.parent == root:
        if path.name == _PACKAGE_ENTRY:
            return [f"Declared Python source root must contain packages, not be one: {relative}"]
        return [f"Python module must live inside a package below its declared source root: {relative}"]
    if path.name == _PACKAGE_ENTRY:
        package_dirs.add(path.parent)
    current = path.parent
    while current != root and current not in python_dirs:
        python_dirs.add(current)
        current = current.parent
    return []


def check_folder_architecture(
    governance_root: Path,
    store: DocumentStore,
    inventory: RepositoryInventory,
    *,
    coding_policy_path: Path,
) -> tuple[list[str], list[str]]:
    """Validate native-package structure below owner-declared Python source roots."""

    path, error = inventory.validate_file(coding_policy_path)
    if error:
        return [error], []
    assert path is not None
    policy, error = store.markdown(path)
    if error:
        return [error], []
    assert policy is not None
    review_lines, policy_errors = policy.positive_integer_declaration(
        "code_decomposition_review_lines", "Coding principles"
    )
    if policy_errors:
        return policy_errors, []
    assert review_lines is not None

    errors: list[str] = []
    warnings: list[str] = []
    files, inventory_error = inventory.python_files(governance_root)
    if inventory_error:
        return [inventory_error], warnings
    roots, exception_roots, root_errors = _owner_declared_python_roots(governance_root, store)
    errors.extend(root_errors)
    warnings.extend(
        "Python source root is a declared packaged-folder exception; re-evaluate it through its owner record: "
        f"{root.relative_to(governance_root).as_posix()}"
        for root in sorted(exception_roots)
    )
    python_dirs: set[Path] = set()
    package_dirs: set[Path] = set()
    for path in files:
        root = next((candidate for candidate in roots if candidate in path.parents), None)
        if roots and root is None:
            errors.append(
                "Python file is outside owner-declared governance source roots: "
                f"{path.relative_to(governance_root).as_posix()}"
            )
        elif root is not None and root not in exception_roots:
            errors.extend(_package_structure_errors(path, root, governance_root, python_dirs, package_dirs))
        text, read_error = store.read_text(path)
        if read_error:
            errors.append(read_error)
            continue
        assert text is not None
        line_count = len(text.splitlines())
        if line_count > review_lines:
            warnings.append(
                f"Python file exceeds the {review_lines}-line decomposition review trigger: "
                f"{path.relative_to(governance_root).as_posix()} ({line_count} lines)"
            )
    errors.extend(
        "Python package folder is missing its native public entrypoint: "
        f"{(directory / _PACKAGE_ENTRY).relative_to(governance_root).as_posix()}"
        for directory in sorted(python_dirs - package_dirs)
    )
    return errors, warnings
