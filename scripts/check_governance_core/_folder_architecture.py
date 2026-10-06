from __future__ import annotations

from pathlib import Path

from scripts.check_governance_core._declared_paths import canonical_relative, resolve_declared_directory
from scripts.check_governance_core._documents import PROJECT_DOCS_ROOT, DocumentStore, MarkdownDocument
from scripts.check_governance_core._inventory import RepositoryInventory
from scripts.check_governance_core._package_interface import PACKAGE_ENTRY, interface_errors


_ROOT_TOKEN = "governance-core-python-root:"
_EXCEPTION_TOKEN = "governance-core-python-package-exception:"
# Project-owned path: each project's own architecture record declares its own Python roots.
_ROOT_OWNER = PROJECT_DOCS_ROOT / "architecture/architecture.md"


def _marker_values(document: MarkdownDocument, owner: Path, *, token: str, label: str) -> tuple[list[str], list[str]]:
    raw_values, errors = document.markers(token)
    errors = [f"Invalid {label} marker in {owner}: {error}" for error in errors]
    values: list[str] = []
    seen: set[str] = set()
    for value in raw_values:
        if canonical_relative(value) is None:
            errors.append(f"Invalid {label} in {owner}: {value!r}")
            continue
        key = value.casefold()
        if key in seen:
            errors.append(f"Duplicate {label} in {owner}: {value}")
            continue
        seen.add(key)
        values.append(value)
    return values, errors


def _record_roots(
    record_root: Path,
    store: DocumentStore,
    *,
    require_root: bool,
) -> tuple[dict[str, Path], list[str], list[str]]:
    """Resolve one architecture record's root and exception markers against its own root."""

    owner = record_root / _ROOT_OWNER
    document, read_error = store.markdown(owner)
    if read_error:
        return {}, [], [read_error]
    assert document is not None
    values, errors = _marker_values(document, owner, token=_ROOT_TOKEN, label="governance-core Python root")
    exceptions, exception_errors = _marker_values(
        document, owner, token=_EXCEPTION_TOKEN, label="governance-core packaged-folder exception"
    )
    errors.extend(exception_errors)
    roots: dict[str, Path] = {}
    for value in values:
        candidate, error = resolve_declared_directory(record_root, value)
        if error:
            errors.append(f"Declared governance-core Python root {value!r} in {owner}: {error}")
            continue
        assert candidate is not None
        roots[value] = candidate
    if require_root and not roots:
        errors.append(f"{owner} must declare at least one governance-core-python-root marker")
    for value in exceptions:
        if value not in values:
            errors.append(
                f"Declared governance-core packaged-folder exception in {owner} is not a declared Python root: {value}"
            )
    return roots, [value for value in exceptions if value in roots], errors


def _owner_declared_python_roots(
    repo_root: Path,
    governance_root: Path,
    store: DocumentStore,
) -> tuple[tuple[Path, ...], frozenset[Path], list[str]]:
    """Merge the pack record at the governance root with the host record at the repository root.

    One record is read once when the roots coincide. The pack record declares at least one
    root; a host record declares only the host's own roots, so a host root inside the
    governance root is rejected (one owner per root) and a Python-free host declares none.
    """

    pack_roots, pack_exceptions, errors = _record_roots(governance_root, store, require_root=True)
    roots = list(pack_roots.values())
    exception_roots = {pack_roots[value] for value in pack_exceptions}
    if repo_root != governance_root:
        host_roots, host_exceptions, host_errors = _record_roots(repo_root, store, require_root=False)
        errors.extend(host_errors)
        for value, candidate in host_roots.items():
            if candidate == governance_root or governance_root in candidate.parents:
                errors.append(
                    f"Declared governance-core Python root {value!r} in {repo_root / _ROOT_OWNER} lies inside the "
                    f"governance root; its owner is {governance_root / _ROOT_OWNER}"
                )
                continue
            roots.append(candidate)
        exception_roots.update(host_roots[value] for value in host_exceptions if host_roots[value] in roots)
    for inner in sorted(roots):
        for outer in sorted(roots):
            if outer in inner.parents:
                errors.append(
                    "Declared governance-core Python roots must not nest: "
                    f"{inner.relative_to(repo_root).as_posix()!r} is inside {outer.relative_to(repo_root).as_posix()!r}"
                )
    return tuple(roots), frozenset(exception_roots), errors


def _package_structure_errors(
    path: Path,
    root: Path,
    relative: str,
    python_dirs: set[Path],
    package_dirs: set[Path],
) -> list[str]:
    """Record one module's package ancestry below an enforced source root."""

    if path.parent == root:
        if path.name == PACKAGE_ENTRY:
            return [f"Declared Python source root must contain packages, not be one: {relative}"]
        return [f"Python module must live inside a package below its declared source root: {relative}"]
    if path.name == PACKAGE_ENTRY:
        package_dirs.add(path.parent)
    current = path.parent
    while current != root and current not in python_dirs:
        python_dirs.add(current)
        current = current.parent
    return []


def check_folder_architecture(
    repo_root: Path,
    governance_root: Path,
    store: DocumentStore,
    inventory: RepositoryInventory,
    *,
    coding_policy_path: Path,
) -> tuple[list[str], list[str]]:
    """Validate native-package structure and interfaces below the Python roots declared by both records.

    Python is scanned under the repository root, which contains the vendored pack; root and
    exception markers come from the pack record at the governance root and, when the roots
    differ, the host record at the repository root, each resolved against its own root.
    """

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
    files, inventory_error = inventory.python_files(repo_root)
    if inventory_error:
        return [inventory_error], warnings
    roots, exception_roots, root_errors = _owner_declared_python_roots(repo_root, governance_root, store)
    errors.extend(root_errors)
    warnings.extend(
        "Python source root is a declared packaged-folder exception; re-evaluate it through its owner record: "
        f"{root.relative_to(repo_root).as_posix()}"
        for root in sorted(exception_roots)
    )
    import_bases = tuple(sorted({root.parent for root in roots}))
    entry_dirs = frozenset(path.parent for path in files if path.name == PACKAGE_ENTRY)
    python_dirs: set[Path] = set()
    package_dirs: set[Path] = set()
    for path in files:
        relative = path.relative_to(repo_root).as_posix()
        root = next((candidate for candidate in roots if candidate in path.parents), None)
        if roots and root is None:
            record = governance_root if governance_root in path.parents else repo_root
            errors.append(
                f"Python file is outside the Python source roots declared in {record / _ROOT_OWNER}: {relative}"
            )
        elif root is not None and root not in exception_roots and not any(
            part.startswith(".") or part == "__pycache__" for part in path.relative_to(root).parts
        ):
            errors.extend(_package_structure_errors(path, root, relative, python_dirs, package_dirs))
            errors.extend(interface_errors(path, root, import_bases, relative, store, entry_dirs))
        text, read_error = store.read_text(path)
        if read_error:
            errors.append(read_error)
            continue
        assert text is not None
        line_count = len(text.splitlines())
        if line_count > review_lines:
            warnings.append(
                f"Python file exceeds the {review_lines}-line decomposition review trigger: "
                f"{relative} ({line_count} lines)"
            )
    errors.extend(
        "Python package folder is missing its native public entrypoint: "
        f"{(directory / PACKAGE_ENTRY).relative_to(repo_root).as_posix()}"
        for directory in sorted(python_dirs - package_dirs)
    )
    return list(dict.fromkeys(errors)), warnings
