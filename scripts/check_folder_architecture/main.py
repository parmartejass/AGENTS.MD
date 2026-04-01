from __future__ import annotations

import argparse
import ast
import json
import logging
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path, PurePosixPath


logger = logging.getLogger(__name__)
SCOPE_MANIFEST_PATH = "scripts/check_folder_architecture/scope.json"
VALID_SCOPE_MODES = {"allow_non_owner", "enforce", "support"}


@dataclass(frozen=True)
class Issue:
    path: str
    message: str


@dataclass(frozen=True)
class TreeSpec:
    tree_root: str
    parent_main: str
    module_prefix: str
    child_dirs: tuple[str, ...]


@dataclass(frozen=True)
class PythonRoot:
    path: str
    enforcement_mode: str
    owner: str


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

        path_value = str(entry.get("path", "")).strip().strip("/")
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


def _iter_repo_python_files(root: Path) -> list[Path]:
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
        result = subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True,
            cwd=root,
            timeout=10,
        )
    except (FileNotFoundError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return sorted(
            path
            for path in root.rglob("*.py")
            if ".git" not in path.parts and "__pycache__" not in path.parts and ".venv" not in path.parts
        )

    paths: list[Path] = []
    for raw in result.stdout.splitlines():
        if not raw.strip():
            continue
        paths.append(root / raw.strip())
    return sorted(paths)


def _check_python_scope(repo_root: Path, governance_root: Path, issues: list[Issue]) -> None:
    scope_roots = _load_scope_manifest(governance_root, issues)
    if not scope_roots:
        return

    for file_path in _iter_repo_python_files(repo_root):
        rel_path = file_path.relative_to(repo_root).as_posix()
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


def _check_scripts_root(root: Path, issues: list[Issue]) -> None:
    scripts_root = root / "scripts"
    if not scripts_root.is_dir():
        issues.append(Issue(path="scripts", message="Scripts root is missing."))
        return

    for child in sorted(scripts_root.glob("*.py")):
        issues.append(
            Issue(
                path=str(child.relative_to(root)),
                message="Top-level Python script found; move behavior behind scripts/<feature>/main.py.",
            )
        )

    for required in (
        "scripts/check_docs_router_contract/main.py",
        "scripts/check_folder_architecture/main.py",
        "scripts/check_governance_core/main.py",
        "scripts/check_python_safety/main.py",
    ):
        _check_exists(root, required, issues)


def _check_dual_entry_template(root: Path, issues: list[Issue]) -> None:
    required_paths = (
        "templates/python-dual-entry/myapp/cli/main.py",
        "templates/python-dual-entry/myapp/core/main.py",
        "templates/python-dual-entry/myapp/gui/main.py",
        "templates/python-dual-entry/myapp/runner/main.py",
        "templates/python-dual-entry/myapp/runner/validation.py",
        "templates/python-dual-entry/myapp/runner/workflows.py",
        "templates/python-dual-entry/myapp/runner/text_transform.py",
    )
    for rel_path in required_paths:
        _check_exists(root, rel_path, issues)

    for legacy in (
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
        "templates/python-dual-entry/myapp/main.py",
        required=["from myapp.cli.main import build_cli_request, has_cli_intent", "from myapp.gui.main import start_gui"],
        forbidden=["myapp.cli_app", "myapp.gui_app"],
        issues=issues,
    )
    _check_text_contains(
        root,
        "templates/python-dual-entry/myapp/runner/main.py",
        required=["from .validation import validate_job_config", "from .workflows import get_workflow"],
        forbidden=["from myapp.core.validators import", "from myapp.workflows import", "from myapp.core.main import validate_job_config"],
        issues=issues,
    )


def _check_pr_control_plane_template(root: Path, issues: list[Issue]) -> None:
    required_paths = (
        "templates/pr-control-plane/scripts/main.py",
        "templates/pr-control-plane/scripts/check_review_state/main.py",
        "templates/pr-control-plane/scripts/harness_gap/main.py",
        "templates/pr-control-plane/scripts/remediation_loop/main.py",
        "templates/pr-control-plane/scripts/request_rerun/main.py",
        "templates/pr-control-plane/scripts/resolve_bot_threads/main.py",
        "templates/pr-control-plane/scripts/risk_policy_gate/main.py",
        "templates/pr-control-plane/scripts/validate_browser_evidence/main.py",
    )
    for rel_path in required_paths:
        _check_exists(root, rel_path, issues)

    for legacy in (
        "templates/pr-control-plane/scripts/check_review_state.py",
        "templates/pr-control-plane/scripts/common.py",
        "templates/pr-control-plane/scripts/harness_gap.py",
        "templates/pr-control-plane/scripts/remediation_loop.py",
        "templates/pr-control-plane/scripts/request_rerun.py",
        "templates/pr-control-plane/scripts/resolve_bot_threads.py",
        "templates/pr-control-plane/scripts/risk_policy_gate.py",
        "templates/pr-control-plane/scripts/validate_browser_evidence.py",
    ):
        _check_absent(root, legacy, issues)

    _check_text_contains(
        root,
        "templates/pr-control-plane/scripts/main.py",
        required=[
            'def _load_child_module(child_name: str):',
            '_load_child_module("check_review_state")',
            '_load_child_module("risk_policy_gate")',
            'subparsers.add_parser("risk-policy-gate"',
        ],
        forbidden=["from common import", "from check_review_state.main import", "from risk_policy_gate.main import"],
        issues=issues,
    )


def _parse_python_module(root: Path, path: Path, issues: list[Issue]) -> ast.Module | None:
    rel_path = path.relative_to(root).as_posix()
    raw = _read_text_file(path, rel_path, issues)
    if raw is None:
        return None
    try:
        return ast.parse(raw, filename=str(path))
    except SyntaxError as exc:
        issues.append(Issue(path=rel_path, message=f"Could not parse Python for architecture check: {exc}"))
        return None


def _resolve_relative_import_targets(path: Path, tree_root: Path, module_prefix: str, node: ast.ImportFrom) -> list[str]:
    parent_parts = list(path.relative_to(tree_root).parent.parts)
    current_package_parts = [module_prefix, *parent_parts]
    ascend = node.level - 1
    if len(current_package_parts) - ascend < 1:
        return []

    base_parts = current_package_parts[: len(current_package_parts) - ascend]
    if node.module is not None:
        return [".".join([*base_parts, *node.module.split(".")])]
    return [".".join([*base_parts, alias.name]) for alias in node.names]


def _check_parent_only_imports(root: Path, spec: TreeSpec, issues: list[Issue]) -> None:
    tree_root = root / spec.tree_root
    parent_main = root / spec.parent_main
    if not tree_root.is_dir() or not parent_main.is_file():
        return

    child_prefixes = {child: f"{spec.module_prefix}.{child}" for child in spec.child_dirs}

    for file_path in sorted(tree_root.rglob("*.py")):
        rel_path = file_path.relative_to(root).as_posix()
        if file_path == parent_main:
            owner = "parent"
        else:
            relative_parts = file_path.relative_to(tree_root).parts
            if not relative_parts:
                continue
            owner = relative_parts[0]
            if owner not in spec.child_dirs:
                continue

        tree = _parse_python_module(root, file_path, issues)
        if tree is None:
            continue

        imports: list[str] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.level == 0 and node.module is not None:
                    imports.append(node.module)
                elif node.level > 0:
                    imports.extend(_resolve_relative_import_targets(file_path, tree_root, spec.module_prefix, node))

        for imported in imports:
            matched_child = next(
                (
                    child
                    for child, prefix in child_prefixes.items()
                    if imported == prefix or imported.startswith(prefix + ".")
                ),
                None,
            )
            if matched_child is None or owner == "parent" or owner == matched_child:
                continue
            issues.append(
                Issue(
                    path=rel_path,
                    message=(
                        f"Cross-child import detected ({owner} -> {matched_child}). "
                        "Only the parent entrypoint may connect feature folders."
                    ),
                )
            )


def _check_scope_manifest_reference(root: Path, issues: list[Issue]) -> None:
    _check_text_contains(
        root,
        "docs/project/architecture/architecture.md",
        required=[SCOPE_MANIFEST_PATH],
        forbidden=[],
        issues=issues,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate repo folder-architecture hard-gate invariants.")
    parser.add_argument("--root", default=".", help="Repository root to validate.")
    args = parser.parse_args(argv)

    _configure_logging()

    repo_root = Path(args.root).resolve()
    governance_root = Path(__file__).resolve().parents[2]
    issues: list[Issue] = []

    _check_python_scope(repo_root, governance_root, issues)
    _check_scripts_root(repo_root, issues)
    _check_dual_entry_template(repo_root, issues)
    _check_pr_control_plane_template(repo_root, issues)
    _check_parent_only_imports(
        repo_root,
        TreeSpec(
            tree_root="templates/python-dual-entry/myapp",
            parent_main="templates/python-dual-entry/myapp/main.py",
            module_prefix="myapp",
            child_dirs=("cli", "core", "gui", "runner"),
        ),
        issues,
    )
    _check_parent_only_imports(
        repo_root,
        TreeSpec(
            tree_root="templates/pr-control-plane/scripts",
            parent_main="templates/pr-control-plane/scripts/main.py",
            module_prefix="scripts",
            child_dirs=(
                "check_review_state",
                "harness_gap",
                "remediation_loop",
                "request_rerun",
                "resolve_bot_threads",
                "risk_policy_gate",
                "validate_browser_evidence",
            ),
        ),
        issues,
    )
    _check_scope_manifest_reference(repo_root, issues)

    if issues:
        for issue in issues:
            logger.error("ERROR %s %s", issue.path, issue.message)
        logger.error("Folder architecture checks failed: %s issue(s).", len(issues))
        return 1

    logger.info("Folder architecture checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
