from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, List, Tuple

try:
    from ._docs_routes import extract_route_targets, is_header_exempt_markdown, targets_child
    from ._entrypoint_contracts import (
        docs_contract_from_payload,
        load_entrypoint_contracts,
        resolve_docs_router_filename,
        resolve_primary_leaf_filename,
        validate_registry_paths,
    )
except ImportError:  # pragma: no cover - script-path execution
    from _docs_routes import extract_route_targets, is_header_exempt_markdown, targets_child
    from _entrypoint_contracts import (
        docs_contract_from_payload,
        load_entrypoint_contracts,
        resolve_docs_router_filename,
        resolve_primary_leaf_filename,
        validate_registry_paths,
    )


def check_agents_manifest(governance_root: Path) -> List[str]:
    errors: List[str] = []
    manifest = governance_root / "agents-manifest.yaml"
    if not manifest.is_file():
        return [f"Missing agents-manifest.yaml at governance root: {manifest}"]

    lines = manifest.read_text(encoding="utf-8").splitlines()
    in_path_list = False
    path_list_indent = 0
    path_list_key: str | None = None

    in_profiles = False
    profiles_indent = 0
    profile_key_indent: int | None = None
    current_profile: str | None = None

    paths_by_list: Dict[str, List[str]] = {}

    for idx, line in enumerate(lines, start=1):
        trimmed = line.strip()
        if not trimmed or trimmed.startswith("#"):
            continue

        indent = len(line) - len(line.lstrip(" "))

        if in_profiles:
            if indent <= profiles_indent and re.match(r"^[A-Za-z0-9_]+:\s*", trimmed):
                in_profiles = False
                profiles_indent = 0
                profile_key_indent = None
                current_profile = None
            else:
                match = re.match(r"^([A-Za-z0-9_]+):\s*$", trimmed)
                if match:
                    if profile_key_indent is None:
                        if indent > profiles_indent:
                            profile_key_indent = indent
                            current_profile = match.group(1)
                    elif indent == profile_key_indent:
                        current_profile = match.group(1)

        if not in_profiles:
            profiles_match = re.match(r"^(\s*)profiles:\s*$", line)
            if profiles_match:
                in_profiles = True
                profiles_indent = len(profiles_match.group(1))
                profile_key_indent = None
                current_profile = None

        if in_path_list:
            is_list_item = trimmed.startswith("- ")
            is_new_key = (not is_list_item) and indent <= path_list_indent and re.match(
                r"^[A-Za-z0-9_]+:\s*", trimmed
            )
            if is_new_key:
                in_path_list = False
                path_list_indent = 0
                path_list_key = None

        if not in_path_list:
            key_match = re.match(r"^(\s*)(default_inject|fallback_inject|inject):\s*$", line)
            if key_match:
                in_path_list = True
                path_list_indent = len(key_match.group(1))
                key = key_match.group(2)
                if key == "inject" and in_profiles and current_profile:
                    path_list_key = f"profiles.{current_profile}.inject"
                else:
                    path_list_key = key
                continue

        if not in_path_list or not trimmed.startswith("- "):
            continue

        double_quoted = re.match(r'^-\s+"([^"]+)"\s*$', trimmed)
        single_quoted = re.match(r"^-\s+'([^']+)'\s*$", trimmed)
        if double_quoted:
            value = double_quoted.group(1)
        elif single_quoted:
            value = single_quoted.group(1)
        else:
            errors.append(f"Unquoted path in {path_list_key} at line {idx}: {trimmed}")
            continue

        if not value.strip():
            errors.append(f"Empty path value in {path_list_key} at line {idx}")
            continue

        assert path_list_key is not None
        paths_by_list.setdefault(path_list_key, []).append(value)

    default_inject = paths_by_list.get("default_inject", [])
    if not default_inject:
        errors.append("Missing or empty default_inject list in agents-manifest.yaml")
    elif "AGENTS.md" not in default_inject:
        errors.append("default_inject must include AGENTS.md")

    governance_inject = paths_by_list.get("profiles.governance_improvement.inject")
    if governance_inject is None:
        errors.append("Missing profiles.governance_improvement.inject list in agents-manifest.yaml")
    elif "docs/agents/22-ssot-authority-decisions/ssot-authority-decisions.md" not in governance_inject:
        errors.append(
            "profiles.governance_improvement.inject must include "
            "docs/agents/22-ssot-authority-decisions/ssot-authority-decisions.md"
        )

    all_paths = set()
    for list_key, values in paths_by_list.items():
        seen = set()
        for value in values:
            if value in seen:
                errors.append(f"Duplicate path in {list_key}: {value}")
            else:
                seen.add(value)
                all_paths.add(value)

    for rel in sorted(all_paths):
        if not (governance_root / rel).exists():
            errors.append(f"Manifest references missing path: {rel}")

    return errors


def check_docs_ssot(repo_root: Path, governance_root: Path) -> Tuple[List[str], List[str]]:
    errors: List[str] = []
    warnings: List[str] = []

    docs_root = repo_root / "docs"
    if not docs_root.is_dir():
        return [f"Missing required docs/ folder: {docs_root}"], warnings

    policy_doc_rel = "docs/agents/25-docs-ssot-policy/docs-ssot-policy.md"
    policy_path = governance_root / policy_doc_rel
    if not policy_path.is_file():
        return ([f"{policy_doc_rel} missing in governance root: {policy_path}"], warnings)

    policy_lines = policy_path.read_text(encoding="utf-8").splitlines()
    enum_line = None
    in_code_block = False
    for line in policy_lines:
        stripped = line.strip()
        if stripped.startswith("```"):
            in_code_block = not in_code_block
            continue
        if in_code_block and re.match(r"^doc_type:\s*.+\|.+", stripped):
            enum_line = stripped
            break
    if not enum_line:
        return (
            [
                f"Doc header enum template not found in {policy_doc_rel} "
                "(expected 'doc_type: ...|...' inside a fenced code block)."
            ],
            warnings,
        )
    allowed_doc_types = {
        part.strip() for part in re.sub(r"^doc_type:\s*", "", enum_line).split("|") if part.strip()
    }

    payload, registry_errors = load_entrypoint_contracts(governance_root)
    errors.extend(registry_errors)
    errors.extend(validate_registry_paths(payload) if payload else [])
    if errors:
        return errors, warnings

    docs_contract = docs_contract_from_payload(payload)
    doc_dirs = [docs_root]
    doc_dirs.extend(sorted((path for path in docs_root.rglob("*") if path.is_dir()), key=lambda p: p.as_posix()))

    for dir_path in doc_dirs:
        router_name = resolve_docs_router_filename(dir_path.name, docs_contract)
        router_path = dir_path / router_name
        if not router_path.is_file():
            errors.append(f"Missing folder router: {router_path}")
            continue

        router_text = router_path.read_text(encoding="utf-8", errors="replace")
        route_targets, route_errors = extract_route_targets(router_text)
        rel_dir = dir_path.relative_to(docs_root).as_posix()
        for issue in route_errors:
            errors.append(f"{router_path}: {issue}")

        direct_children = [
            child
            for child in sorted(dir_path.iterdir(), key=lambda path: path.name.lower())
            if child.name != router_name and not child.name.startswith(".")
        ]
        public_markdown_children = [
            child
            for child in direct_children
            if child.is_file()
            and child.suffix.lower() == ".md"
            and child.name not in docs_contract.identity_files
        ]
        expected_primary_leaf = resolve_primary_leaf_filename(dir_path.name, docs_contract)
        artifact_first = len(public_markdown_children) == 0
        if not artifact_first:
            if len(public_markdown_children) < docs_contract.minimum_public_leaf_count:
                errors.append(f"{dir_path}: expected at least {docs_contract.minimum_public_leaf_count} public leaf doc(s).")
            public_leaf_names = {child.name for child in public_markdown_children}
            if expected_primary_leaf not in public_leaf_names:
                errors.append(f"{dir_path}: missing canonical public leaf '{expected_primary_leaf}'.")
        for child in direct_children:
            child_router = resolve_docs_router_filename(child.name, docs_contract) if child.is_dir() else ""
            if not targets_child(route_targets, child, child_router_filename=child_router):
                errors.append(f"{router_path}: missing route for direct child '{child.name}'.")
        if artifact_first and any(target.endswith(".md") for target in route_targets):
            leaf_targets = [
                target
                for target in route_targets
                if target.endswith(".md") and "/" not in target and target not in docs_contract.identity_files
            ]
            if leaf_targets:
                errors.append(f"{router_path}: router-only folders must not expose public leaf markdown targets.")
    for md_file in docs_root.rglob("*.md"):
        rel = md_file.relative_to(docs_root).as_posix()
        router_name = resolve_docs_router_filename(md_file.parent.name, docs_contract)
        if md_file.name == router_name:
            continue
        if is_header_exempt_markdown(rel):
            continue
        head = md_file.read_text(encoding="utf-8").splitlines()[:25]
        doc_type_line = next((line for line in head if line.startswith("doc_type:")), None)
        if doc_type_line is None:
            errors.append(f"Missing doc header (doc_type) in: {md_file}")
        else:
            doc_type = re.sub(r"^doc_type:\s*", "", doc_type_line).strip()
            if doc_type not in allowed_doc_types:
                errors.append(f"Invalid doc_type '{doc_type}' in: {md_file}")
        if not any(line.startswith("ssot_owner:") for line in head):
            errors.append(f"Missing doc header (ssot_owner) in: {md_file}")
        if not any(line.startswith("update_trigger:") for line in head):
            errors.append(f"Missing doc header (update_trigger) in: {md_file}")
    for doc_file in docs_root.rglob("*"):
        if not doc_file.is_file():
            continue
        rel = doc_file.relative_to(docs_root).as_posix()
        if "/generated/" in f"/{rel}/":
            continue
        text = doc_file.read_text(encoding="utf-8", errors="replace")
        if re.search(r"defaults?:\s*$|default value", text, flags=re.IGNORECASE | re.MULTILINE):
            warnings.append(
                "Docs mention defaults/default value. Ensure docs reference config keys by identifier, "
                "not copied literal values."
            )
            break
    return errors, warnings
def check_project_docs(repo_root: Path, governance_rel_path: str, governance_root: Path) -> List[str]:
    errors: List[str] = []
    payload, registry_errors = load_entrypoint_contracts(governance_root)
    errors.extend(registry_errors)
    errors.extend(validate_registry_paths(payload) if payload else [])
    if errors:
        return errors
    docs_contract = docs_contract_from_payload(payload)
    required_files = [
        "README.md",
        "docs/project/project_index.md",
        "docs/project/goal/goal_index.md",
        "docs/project/goal/goal.md",
        "docs/project/rules/rules_index.md",
        "docs/project/rules/rules.md",
        "docs/project/architecture/architecture_index.md",
        "docs/project/architecture/architecture.md",
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
            f"{governance_prefix}scripts/check_change_records.ps1",
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
        for child in ("goal", "rules", "architecture", "learning"):
            expected = f"{child}/{resolve_docs_router_filename(child, docs_contract)}"
            if expected not in project_targets:
                errors.append(f"docs/project/project_index.md must reference {expected}")
    for folder_name in ("goal", "rules", "architecture", "learning"):
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
    return errors
