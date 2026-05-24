from __future__ import annotations
import argparse
import json
import logging
import subprocess
import sys
from pathlib import Path, PurePosixPath
from _issues import Issue, PythonRoot
from _imports import TreeSpec, check_parent_only_imports
from _paths import is_excluded_non_git_python_path
logger = logging.getLogger(__name__)
SCOPE_MANIFEST_PATH = "scripts/check_folder_architecture/scope.json"
ENTRYPOINT_CONTRACTS_PATH = "scripts/entrypoint_contracts.json"
VALID_SCOPE_MODES = {"allow_non_owner", "enforce", "support"}
MAX_PYTHON_FILE_LINES = 400
def _configure_logging() -> None:
    handler = logging.StreamHandler(stream=sys.stdout)
    handler.setFormatter(logging.Formatter("%(message)s"))
    logger.handlers.clear()
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


def _check_exists(root: Path, rel_path: str, issues: list[Issue]) -> None:
    if not (root / rel_path).exists():
        issues.append(Issue(path=rel_path, message="Missing required folder contract path."))


def _check_absent(root: Path, rel_path: str, issues: list[Issue]) -> None:
    if (root / rel_path).exists():
        issues.append(Issue(path=rel_path, message="Legacy flat runtime file must be removed or folderized."))
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
def _load_entrypoint_contracts(governance_root: Path, issues: list[Issue]) -> dict[str, object]:
    registry_path = governance_root / ENTRYPOINT_CONTRACTS_PATH
    rel_path = registry_path.relative_to(governance_root).as_posix()
    raw = _read_text_file(registry_path, rel_path, issues)
    if raw is None:
        return {}
    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        issues.append(Issue(path=rel_path, message=f"Invalid JSON in entrypoint registry: {exc}"))
        return {}
def _registry_string(
    payload: dict[str, object],
    path_parts: tuple[str, ...],
    *,
    issues: list[Issue],
    registry_rel_path: str,
) -> str | None:
    current: object = payload
    rendered_path = ".".join(path_parts)
    for part in path_parts:
        if not isinstance(current, dict) or part not in current:
            issues.append(
                Issue(
                    path=registry_rel_path,
                    message=f"Missing entrypoint registry key '{rendered_path}'.",
                )
            )
            return None
        current = current[part]
    if not isinstance(current, str) or not current.strip():
        issues.append(
            Issue(
                path=registry_rel_path,
                message=f"Entry point registry key '{rendered_path}' must be a non-empty string.",
            )
        )
        return None
    return current
def _python_entrypoint_filename(
    folder_name: str, governance_root: Path, issues: list[Issue]
) -> str | None:
    payload = _load_entrypoint_contracts(governance_root, issues)
    if not payload:
        return None
    registry_rel_path = ENTRYPOINT_CONTRACTS_PATH
    pattern = _registry_string(
        payload,
        ("runtime_code", "filename_pattern"),
        issues=issues,
        registry_rel_path=registry_rel_path,
    )
    entrypoint_token = _registry_string(
        payload,
        ("runtime_code", "languages", "python", "artifact_kinds", "executable", "entrypoint_token"),
        issues=issues,
        registry_rel_path=registry_rel_path,
    )
    extension = _registry_string(
        payload,
        ("runtime_code", "languages", "python", "artifact_kinds", "executable", "extension"),
        issues=issues,
        registry_rel_path=registry_rel_path,
    )
    if pattern is None or entrypoint_token is None or extension is None:
        return None
    return (
        pattern.replace("<authority>", folder_name)
        .replace("<entrypoint_token>", entrypoint_token)
        .replace("<extension>", extension)
    )
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
def _iter_repo_python_files(root: Path, issues: list[Issue]) -> list[Path]:
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
        paths.append(root / raw.strip())
    return sorted(paths)
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
def _check_scripts_root(root: Path, governance_root: Path, issues: list[Issue]) -> None:
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
    required_paths: list[str] = []
    for folder_name in (
        "check_docs_router_contract",
        "check_folder_architecture",
        "check_governance_core",
        "check_python_safety",
    ):
        entrypoint = _python_entrypoint_filename(folder_name, governance_root, issues)
        if entrypoint is None:
            continue
        required_paths.append(f"scripts/{folder_name}/{entrypoint}")
    for required in required_paths:
        _check_exists(root, required, issues)
def _check_dual_entry_template(root: Path, issues: list[Issue]) -> None:
    required_paths = (
        "templates/python-dual-entry/myapp/myapp_main.py",
        "templates/python-dual-entry/myapp/cli/cli_main.py",
        "templates/python-dual-entry/myapp/core/core_main.py",
        "templates/python-dual-entry/myapp/gui/gui_main.py",
        "templates/python-dual-entry/myapp/runner/runner_main.py",
        "templates/python-dual-entry/myapp/runner/validation.py",
        "templates/python-dual-entry/myapp/runner/workflows.py",
        "templates/python-dual-entry/myapp/runner/text_transform.py",
    )
    for rel_path in required_paths:
        _check_exists(root, rel_path, issues)
    for legacy in (
        "templates/python-dual-entry/myapp/main.py",
        "templates/python-dual-entry/myapp/cli/main.py",
        "templates/python-dual-entry/myapp/core/main.py",
        "templates/python-dual-entry/myapp/gui/main.py",
        "templates/python-dual-entry/myapp/runner/main.py",
        "templates/python-dual-entry/myapp/cli_app.py",
        "templates/python-dual-entry/myapp/gui_app.py",
        "templates/python-dual-entry/myapp/runner.py",
        "templates/python-dual-entry/myapp/workflows.py",
        "templates/python-dual-entry/myapp/workflows/main.py",
        "templates/python-dual-entry/myapp/core/validators.py",
        "templates/python-dual-entry/myapp/core/text_transform.py",
    ):
        _check_absent(root, legacy, issues)
    _check_text_contains(
        root,
        "templates/python-dual-entry/myapp/myapp_main.py",
        required=["from myapp.cli.cli_main import build_cli_request, has_cli_intent", "from myapp.gui.gui_main import start_gui"],
        forbidden=["myapp.cli_app", "myapp.gui_app"],
        issues=issues,
    )
    _check_text_contains(
        root,
        "templates/python-dual-entry/myapp/runner/runner_main.py",
        required=["from .validation import validate_job_config", "from .workflows import get_workflow"],
        forbidden=["from myapp.core.validators import", "from myapp.workflows import", "from myapp.core.core_main import validate_job_config"],
        issues=issues,
    )
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
    _check_scripts_root(validation_root, governance_root, issues)
    _check_dual_entry_template(validation_root, issues)
    check_parent_only_imports(
        validation_root,
        TreeSpec(
            tree_root="templates/python-dual-entry/myapp",
            parent_main="templates/python-dual-entry/myapp/myapp_main.py",
            module_prefix="myapp",
            child_dirs=("cli", "core", "gui", "runner"),
        ),
        issues,
    )
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
