from __future__ import annotations
import argparse
import json
import logging
import sys
from pathlib import Path, PurePosixPath
from _enumeration import iter_repo_python_files as _iter_repo_python_files
from _issues import Issue, PythonRoot
logger = logging.getLogger(__name__)
SCOPE_MANIFEST_PATH = "scripts/check_folder_architecture/scope.json"
VALID_SCOPE_MODES = {"allow_non_owner", "enforce", "support"}
MAX_PYTHON_FILE_LINES = 400
EXCLUDED_SCRIPT_FEATURE_DIRS = {"__pycache__"}
def _configure_logging() -> None:
    handler = logging.StreamHandler(stream=sys.stdout)
    handler.setFormatter(logging.Formatter("%(message)s"))
    logger.handlers.clear()
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


def _check_exists(root: Path, rel_path: str, issues: list[Issue]) -> None:
    if not (root / rel_path).exists():
        issues.append(Issue(path=rel_path, message="Missing required folder contract path."))


def _check_text_contains(
    root: Path,
    rel_path: str,
    required: list[str],
    forbidden: list[str],
    issues: list[Issue],
) -> None:
    path = root / rel_path
    if not path.is_file():
        issues.append(Issue(path=rel_path, message="Expected file for architecture assertion is missing."))
        return
    text = _read_text_file(path, rel_path, issues)
    if text is None:
        return
    for snippet in required:
        if snippet not in text:
            issues.append(Issue(path=rel_path, message=f"Missing required architecture reference: {snippet}"))
    for snippet in forbidden:
        if snippet in text:
            issues.append(Issue(path=rel_path, message=f"Found forbidden legacy reference: {snippet}"))
def _read_text_file(path: Path, rel_path: str, issues: list[Issue]) -> str | None:
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        issues.append(Issue(path=rel_path, message=f"Failed to read file for architecture check: {exc}"))
        return None
def python_entrypoint_filename(folder_name: str) -> str:
    return f"{folder_name}_main.py"
def _load_scope_manifest(governance_root: Path, issues: list[Issue]) -> list[PythonRoot]:
    manifest_path = governance_root / SCOPE_MANIFEST_PATH
    rel_path = manifest_path.relative_to(governance_root).as_posix()
    if not manifest_path.is_file():
        issues.append(Issue(path=rel_path, message="Missing folder-architecture scope manifest."))
        return []
    raw = _read_text_file(manifest_path, rel_path, issues)
    if raw is None:
        return []
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        issues.append(Issue(path=rel_path, message=f"Invalid JSON in scope manifest: {exc}"))
        return []
    if payload.get("version") != 1:
        issues.append(Issue(path=rel_path, message="Unsupported scope manifest version."))
    raw_roots = payload.get("python_roots")
    if not isinstance(raw_roots, list):
        issues.append(Issue(path=rel_path, message="Scope manifest must define a python_roots list."))
        return []
    roots: list[PythonRoot] = []
    seen_paths: set[str] = set()
    for index, entry in enumerate(raw_roots, start=1):
        if not isinstance(entry, dict):
            issues.append(Issue(path=rel_path, message=f"python_roots[{index}] must be an object."))
            continue
        raw_path = str(entry.get("path", "")).strip()
        if raw_path.startswith(("/", "\\")):
            issues.append(
                Issue(
                    path=rel_path,
                    message=f"python_roots[{index}] must be repo-relative, not rooted: {raw_path}",
                )
            )
            continue
        path_value = raw_path.strip("/")
        mode = str(entry.get("enforcement_mode", "")).strip()
        owner = str(entry.get("owner", "")).strip()
        if not path_value:
            issues.append(Issue(path=rel_path, message=f"python_roots[{index}] is missing path."))
            continue
        if "\\" in path_value:
            issues.append(Issue(path=rel_path, message=f"python_roots[{index}] must use forward slashes: {path_value}"))
            continue
        normalized = PurePosixPath(path_value)
        if normalized.is_absolute() or any(part in {"", ".", ".."} for part in normalized.parts):
            issues.append(Issue(path=rel_path, message=f"python_roots[{index}] must be a clean repo-relative path: {path_value}"))
            continue
        if ":" in normalized.parts[0]:
            issues.append(
                Issue(
                    path=rel_path,
                    message=f"python_roots[{index}] must be repo-relative, not drive-qualified: {path_value}",
                )
            )
            continue
        if path_value in seen_paths:
            issues.append(Issue(path=rel_path, message=f"Duplicate python scope path: {path_value}"))
            continue
        if mode not in VALID_SCOPE_MODES:
            issues.append(
                Issue(
                    path=rel_path,
                    message=f"python_roots[{index}] has invalid enforcement_mode: {mode}",
                )
            )
            continue
        if not owner:
            issues.append(Issue(path=rel_path, message=f"python_roots[{index}] is missing owner."))
            continue
        seen_paths.add(path_value)
        roots.append(PythonRoot(path=path_value, enforcement_mode=mode, owner=owner))
    for entry in roots:
        if not (governance_root / entry.path).exists():
            issues.append(
                Issue(
                    path=rel_path,
                    message=f"Declared python scope path does not exist: {entry.path}",
                )
            )
    return roots
def _is_path_within(rel_path: str, root_path: str) -> bool:
    return rel_path == root_path or rel_path.startswith(root_path + "/")
def _check_python_scope(
    validation_root: Path, governance_root: Path, python_files: list[Path], issues: list[Issue]
) -> None:
    scope_roots = _load_scope_manifest(governance_root, issues)
    if not scope_roots:
        return
    for file_path in python_files:
        rel_path = file_path.relative_to(validation_root).as_posix()
        if any(_is_path_within(rel_path, entry.path) for entry in scope_roots):
            continue
        issues.append(
            Issue(
                path=rel_path,
                message=(
                    "Python file is outside the declared folder-architecture scope. "
                    f"Add it to {SCOPE_MANIFEST_PATH} or move it under an existing declared root."
                ),
            )
        )
def _check_python_file_line_limits(validation_root: Path, python_files: list[Path], issues: list[Issue]) -> None:
    for file_path in python_files:
        rel_path = file_path.relative_to(validation_root).as_posix()
        try:
            line_count = len(file_path.read_text(encoding="utf-8").splitlines())
        except (OSError, UnicodeDecodeError) as exc:
            issues.append(Issue(path=rel_path, message=f"Failed to read Python file for LOC check: {exc}"))
            continue
        if line_count > MAX_PYTHON_FILE_LINES:
            issues.append(
                Issue(
                    path=rel_path,
                    message=f"Python file exceeds {MAX_PYTHON_FILE_LINES} LOC hard gate: {line_count} lines.",
                )
            )
def _has_direct_python_file(folder: Path) -> bool:
    return any(child.is_file() and child.suffix == ".py" for child in folder.iterdir())


def _discover_script_feature_folders(scripts_root: Path) -> list[Path]:
    return [
        child
        for child in sorted(scripts_root.iterdir(), key=lambda path: path.name.lower())
        if child.is_dir()
        and not child.name.startswith(".")
        and child.name not in EXCLUDED_SCRIPT_FEATURE_DIRS
        and _has_direct_python_file(child)
    ]


def _check_scripts_root(root: Path, issues: list[Issue]) -> None:
    scripts_root = root / "scripts"
    if not scripts_root.is_dir():
        issues.append(Issue(path="scripts", message="Scripts root is missing."))
        return
    for child in sorted(scripts_root.glob("*.py")):
        issues.append(
            Issue(
                path=str(child.relative_to(root)),
                message="Top-level Python script found; move behavior behind scripts/<feature>/<authority>_main.py.",
            )
        )
    for feature_dir in _discover_script_feature_folders(scripts_root):
        required = f"scripts/{feature_dir.name}/{python_entrypoint_filename(feature_dir.name)}"
        _check_exists(root, required, issues)
def _check_scope_manifest_reference(root: Path, issues: list[Issue]) -> None:
    _check_text_contains(
        root,
        "docs/project/architecture/architecture.md",
        required=[SCOPE_MANIFEST_PATH],
        forbidden=[],
        issues=issues,
    )
def _governance_validation_root(repo_root: Path, governance_root: Path) -> Path:
    return governance_root if repo_root != governance_root else repo_root
def _check_governance_owned_contracts(repo_root: Path, governance_root: Path, issues: list[Issue]) -> None:
    validation_root = _governance_validation_root(repo_root, governance_root)
    python_files = _iter_repo_python_files(validation_root, issues)
    _check_python_scope(validation_root, governance_root, python_files, issues)
    _check_python_file_line_limits(validation_root, python_files, issues)
    _check_scripts_root(validation_root, issues)
    if repo_root == governance_root:
        _check_scope_manifest_reference(repo_root, issues)
def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate repo folder-architecture hard-gate invariants.")
    parser.add_argument("--root", default=".", help="Repository root to validate.")
    args = parser.parse_args(argv)
    _configure_logging()
    repo_root = Path(args.root).resolve()
    governance_root = Path(__file__).resolve().parents[2]
    issues: list[Issue] = []
    _check_governance_owned_contracts(repo_root, governance_root, issues)
    if issues:
        for issue in issues:
            logger.error("ERROR %s %s", issue.path, issue.message)
        logger.error("Folder architecture checks failed: %s issue(s).", len(issues))
        return 1
    logger.info("Folder architecture checks passed.")
    return 0
if __name__ == "__main__":
    raise SystemExit(main())
