from __future__ import annotations
from pathlib import Path
from typing import List
try:
    from ._docs_routes import extract_route_targets
    from ._entrypoint_contracts import (
        docs_contract_from_payload,
        load_entrypoint_contracts,
        resolve_docs_router_filename,
        resolve_primary_leaf_filename,
        validate_registry_paths,
    )
except ImportError:  # pragma: no cover - script-path execution
    from _docs_routes import extract_route_targets
    from _entrypoint_contracts import (
        docs_contract_from_payload,
        load_entrypoint_contracts,
        resolve_docs_router_filename,
        resolve_primary_leaf_filename,
        validate_registry_paths,
    )


def _validate_project_optional_leaf_routes(repo_root: Path) -> List[str]:
    errors: List[str] = []
    optional_routes = {
        "docs/project/architecture/protected-behavior.md": "docs/project/architecture/architecture_index.md",
    }
    for leaf_rel, router_rel in optional_routes.items():
        leaf = repo_root / leaf_rel
        router = repo_root / router_rel
        if not router.is_file():
            if not leaf.is_file():
                continue
            errors.append(f"Missing required file: {router_rel}")
            continue
        route_targets, route_errors = extract_route_targets(router.read_text(encoding="utf-8"))
        for issue in route_errors:
            errors.append(f"{router_rel}: {issue}")
        if leaf.is_file() and leaf.name not in route_targets:
            errors.append(f"{router_rel} must reference {leaf.name} when {leaf_rel} exists")
        for target in route_targets:
            if target.lower().endswith(".md") and not (router.parent / target).is_file():
                errors.append(f"{router_rel} references missing local route target: {target}")
    return errors


def _validate_project_doc_branch_routes(repo_root: Path, docs_contract, project_targets: List[str]) -> List[str]:
    errors: List[str] = []
    project_root = repo_root / "docs/project"
    if not project_root.is_dir():
        return errors

    for branch in sorted(path for path in project_root.iterdir() if path.is_dir()):
        router_name = resolve_docs_router_filename(branch.name, docs_contract)
        router_path = branch / router_name
        expected_project_route = f"{branch.name}/{router_name}"
        if expected_project_route not in project_targets:
            errors.append(f"docs/project/project_index.md must reference {expected_project_route}")
        if not router_path.is_file():
            errors.append(f"Missing required file: {router_path.relative_to(repo_root).as_posix()}")
            continue

        route_targets, route_errors = extract_route_targets(router_path.read_text(encoding="utf-8"))
        for issue in route_errors:
            errors.append(f"{router_path.relative_to(repo_root).as_posix()}: {issue}")

        leaf_paths = sorted(path for path in branch.glob("*.md") if path.name != router_name)
        for leaf_path in leaf_paths:
            if leaf_path.name not in route_targets:
                errors.append(f"{router_path.relative_to(repo_root).as_posix()} must reference {leaf_path.name}")
        for target in route_targets:
            if target.lower().endswith(".md") and not (router_path.parent / target).is_file():
                errors.append(f"{router_path.relative_to(repo_root).as_posix()} references missing local route target: {target}")
    return errors


def check_project_docs(repo_root: Path, governance_rel_path: str, governance_root: Path) -> List[str]:
    errors: List[str] = []
    payload, registry_errors = load_entrypoint_contracts(governance_root)
    errors.extend(registry_errors)
    errors.extend(validate_registry_paths(payload) if payload else [])
    if errors:
        return errors
    docs_contract = docs_contract_from_payload(payload)
    policy_path = governance_root / "docs/agents/25-docs-ssot-policy/docs-ssot-policy.md"
    if not policy_path.is_file():
        errors.append(f"Missing docs SSOT policy: {policy_path}")
    required_files = [
        "README.md",
        "docs/project/project_index.md",
        "docs/project/goal/goal_index.md",
        "docs/project/goal/goal.md",
        "docs/project/rules/rules_index.md",
        "docs/project/rules/rules.md",
        "docs/project/architecture/architecture_index.md",
        "docs/project/architecture/architecture.md",
        "docs/project/data-truth/data-truth_index.md",
        "docs/project/data-truth/data-truth.md",
        "docs/project/changelog/changelog_index.md",
        "docs/project/changelog/changelog.md",
        "docs/project/learning/learning_index.md",
        "docs/project/learning/learning.md",
    ]
    for rel in required_files:
        if not (repo_root / rel).is_file():
            errors.append(f"Missing required file: {rel}")
    governance_prefix = f"{governance_rel_path.rstrip('/')}/" if governance_rel_path else ""
    readme = repo_root / "README.md"
    if readme.is_file():
        readme_text = readme.read_text(encoding="utf-8")
        readme_text_lower = readme_text.lower()
        required_refs = [
            "docs/project/project_index.md",
            "AGENTS.md",
            f"{governance_prefix}scripts/check_docs_ssot.ps1",
            f"{governance_prefix}scripts/check_docs_router_contract/check_docs_router_contract_main.py",
            f"{governance_prefix}scripts/check_agents_manifest.ps1",
            f"{governance_prefix}scripts/check_project_docs.ps1",
            f"{governance_prefix}scripts/check_repo_hygiene.ps1",
            f"{governance_prefix}scripts/check_folder_architecture/check_folder_architecture_main.py",
            f"{governance_prefix}scripts/check_python_safety/check_python_safety_main.py",
        ]
        for ref in required_refs:
            if ref.lower() not in readme_text_lower:
                errors.append(f"README.md must reference: {ref}")
    project_router = repo_root / "docs/project/project_index.md"
    if project_router.is_file():
        project_targets, route_errors = extract_route_targets(project_router.read_text(encoding="utf-8"))
        for issue in route_errors:
            errors.append(f"{project_router}: {issue}")
        for child in ("goal", "rules", "architecture", "data-truth", "changelog", "learning"):
            expected = f"{child}/{resolve_docs_router_filename(child, docs_contract)}"
            if expected not in project_targets:
                errors.append(f"docs/project/project_index.md must reference {expected}")
        errors.extend(_validate_project_doc_branch_routes(repo_root, docs_contract, project_targets))
    for folder_name in ("goal", "rules", "architecture", "data-truth", "changelog", "learning"):
        dir_path = repo_root / "docs/project" / folder_name
        router_name = resolve_docs_router_filename(folder_name, docs_contract)
        router_path = dir_path / router_name
        if not router_path.is_file():
            errors.append(f"Missing required file: {router_path.relative_to(repo_root).as_posix()}")
            continue
        route_targets, route_errors = extract_route_targets(router_path.read_text(encoding="utf-8"))
        for issue in route_errors:
            errors.append(f"{router_path.relative_to(repo_root).as_posix()}: {issue}")
        expected_leaf = resolve_primary_leaf_filename(folder_name, docs_contract)
        if expected_leaf not in route_targets:
            errors.append(f"{router_path.relative_to(repo_root).as_posix()} must reference {expected_leaf}")
    errors.extend(_validate_project_optional_leaf_routes(repo_root))
    return errors
