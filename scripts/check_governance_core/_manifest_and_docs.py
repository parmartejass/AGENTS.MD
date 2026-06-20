from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, List, Tuple

SOURCES_OF_TRUTH_MAP_DOC = "docs/agents/20-sources-of-truth-map/sources-of-truth-map.md"

try:
    from ._docs_routes import extract_route_targets, is_header_exempt_markdown, targets_child
    from ._entrypoint_contracts import (
        docs_contract_from_payload,
        load_entrypoint_contracts,
        resolve_docs_router_filename,
        resolve_primary_leaf_filename,
        ssot_owner_path_from_payload,
        validate_registry_paths,
    )
except ImportError:  # pragma: no cover - script-path execution
    from _docs_routes import extract_route_targets, is_header_exempt_markdown, targets_child
    from _entrypoint_contracts import (
        docs_contract_from_payload,
        load_entrypoint_contracts,
        resolve_docs_router_filename,
        resolve_primary_leaf_filename,
        ssot_owner_path_from_payload,
        validate_registry_paths,
    )


def _profile_block(manifest_text: str, profile_name: str) -> str:
    match = re.search(
        rf"(?ms)^  {re.escape(profile_name)}:\n(?P<body>.*?)(?=^  [A-Za-z0-9_]+:\n|^\S|\Z)",
        manifest_text,
    )
    return match.group("body") if match else ""


def _detect_values_from_profile(profile_block: str, list_name: str) -> List[str]:
    match = re.search(r"(?ms)^    detect:\n(?P<body>.*?)(?=^    inject:|^  [A-Za-z0-9_]+:|^\S|\Z)", profile_block)
    if not match:
        return []
    values_match = re.search(
        rf"(?ms)^      {re.escape(list_name)}:\n(?P<body>.*?)(?=^      [A-Za-z0-9_]+:|^    inject:|^  [A-Za-z0-9_]+:|^\S|\Z)",
        match.group("body"),
    )
    if not values_match:
        return []
    return re.findall(r'^\s+-\s+"([^"]+)"\s*$', values_match.group("body"), flags=re.MULTILINE)


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

    registry_payload, registry_errors = load_entrypoint_contracts(governance_root)
    errors.extend(registry_errors)
    coding_principles_doc = ssot_owner_path_from_payload(registry_payload, "runtime_code")
    if not coding_principles_doc:
        errors.append("scripts/entrypoint_contracts.json must define ssot_owner.runtime_code")

    coding_principles_inject = paths_by_list.get("profiles.coding_principles.inject")
    if coding_principles_inject is None:
        errors.append("Missing profiles.coding_principles.inject list in agents-manifest.yaml")
    else:
        if coding_principles_doc and coding_principles_doc not in coding_principles_inject:
            errors.append(f"profiles.coding_principles.inject must include {coding_principles_doc}")
        if SOURCES_OF_TRUTH_MAP_DOC not in coding_principles_inject:
            errors.append(f"profiles.coding_principles.inject must include {SOURCES_OF_TRUTH_MAP_DOC}")

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

    manifest_text = "\n".join(lines)
    errors.extend(_validate_project_docs_profile(manifest_text, paths_by_list))

    return errors


def _validate_project_docs_profile(manifest_text: str, paths_by_list: Dict[str, List[str]]) -> List[str]:
    errors: List[str] = []
    profile = _profile_block(manifest_text, "project_docs")
    if not profile:
        errors.append("Missing profiles.project_docs in agents-manifest.yaml")
        return errors

    project_docs_inject = paths_by_list.get("profiles.project_docs.inject", [])
    required_inject = {
        "docs/project/project_index.md",
        "docs/agents/25-docs-ssot-policy/docs-ssot-policy.md",
        "docs/agents/20-sources-of-truth-map/sources-of-truth-map.md",
        "docs/agents/playbooks/project-docs-template/project-docs-template.md",
    }
    for rel in sorted(required_inject - set(project_docs_inject)):
        errors.append(f"profiles.project_docs.inject must include {rel}")

    broad_keywords = {
        "docs",
        "documentation",
        "readme",
        "architecture",
        "goal",
        "rules",
        "runbook",
        "playbook",
        "adr",
        "protected behavior",
        "protected-behavior",
        "data truth",
        "data-truth",
        "authority supersession",
    }
    for keyword in _detect_values_from_profile(profile, "keywords"):
        if keyword.lower() in broad_keywords:
            errors.append(f"profiles.project_docs.detect keyword is too broad: {keyword}")

    required_file_globs = {"README.md", "docs/project/**/*.md"}
    project_docs_file_globs = set(_detect_values_from_profile(profile, "file_globs"))
    for file_glob in sorted(required_file_globs - project_docs_file_globs):
        errors.append(f"profiles.project_docs.detect.file_globs must include {file_glob}")

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


try:
    from ._project_authority_docs import (
        _validate_project_optional_leaf_routes,
        check_project_docs,
    )
except ImportError:  # pragma: no cover - script-path execution
    from _project_authority_docs import (
        _validate_project_optional_leaf_routes,
        check_project_docs,
    )
