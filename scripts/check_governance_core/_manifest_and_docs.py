from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple


def _load_migrated_router_leaves(governance_root: Path) -> Tuple[Dict[str, str], List[str]]:
    errors: List[str] = []
    mapping_path = governance_root / "scripts/migrated_router_leaves.json"
    if not mapping_path.is_file():
        return {}, [f"Missing migrated router-leaf map: {mapping_path}"]

    try:
        payload = json.loads(mapping_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return {}, [f"Invalid JSON in {mapping_path}: {exc}"]

    raw_map = payload.get("migrated_router_leaves")
    if not isinstance(raw_map, dict):
        return {}, [f"Expected object key 'migrated_router_leaves' in {mapping_path}"]

    normalized: Dict[str, str] = {}
    for raw_key, raw_value in sorted(raw_map.items()):
        if not isinstance(raw_key, str) or not raw_key.strip():
            errors.append(f"Invalid migrated router key in {mapping_path}: {raw_key!r}")
            continue
        if not isinstance(raw_value, str) or not raw_value.strip():
            errors.append(f"Invalid migrated router leaf value for {raw_key!r} in {mapping_path}")
            continue
        key = raw_key.strip().strip("/")
        leaf = raw_value.strip()
        if "/" in leaf or leaf.endswith("/"):
            errors.append(
                f"Invalid migrated router leaf '{leaf}' for {key}; expected direct-child markdown filename."
            )
            continue
        normalized[key] = leaf

    return normalized, errors


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
    elif (
        "docs/agents/22-ssot-authority-decisions/ssot-authority-decisions.md"
        not in governance_inject
    ):
        errors.append(
            "profiles.governance_improvement.inject must include "
            "docs/agents/22-ssot-authority-decisions/ssot-authority-decisions.md"
        )

    all_paths: Set[str] = set()
    for list_key, values in paths_by_list.items():
        seen: Set[str] = set()
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


def _normalize_link_target(raw_target: str) -> str:
    target = raw_target.strip()
    if not target:
        return ""
    if re.match(r"^[A-Za-z][A-Za-z0-9+.-]*:", target) or target.startswith("//"):
        return ""
    target = target.split("?", 1)[0]
    target = target.split("#", 1)[0]
    target = target.replace("\\", "/")
    while target.startswith("./"):
        target = target[2:]
    if target.startswith("/"):
        target = target[1:]
    parts: List[str] = []
    for part in target.split("/"):
        if part in {"", "."}:
            continue
        if part == "..":
            return ""
        parts.append(part)
    return "/".join(parts)


def _extract_markdown_link_targets(text: str) -> List[str]:
    normalized_targets: List[str] = []
    for match in re.findall(r"\[[^\]]+\]\(([^)]+)\)", text):
        normalized = _normalize_link_target(match)
        if normalized:
            normalized_targets.append(normalized)
    return normalized_targets


def _index_targets_child(link_targets: List[str], child: Path) -> bool:
    child_name = child.name
    if child.is_dir():
        allowed_targets = {child_name, f"{child_name}/index.md"}
    else:
        allowed_targets = {child_name}
    return any(target in allowed_targets for target in link_targets)


def _is_docs_router_exempt(docs_root: Path, dir_path: Path) -> bool:
    rel = dir_path.relative_to(docs_root).as_posix()
    if rel.startswith("agents/subagents/shared"):
        return True
    skill_match = re.match(r"^agents/skills/([^/]+)$", rel)
    if skill_match and (dir_path / "SKILL.md").is_file():
        return True
    return False


def _router_looks_routing_only(index_text: str) -> bool:
    lines = [line.strip() for line in index_text.splitlines() if line.strip()]
    if not lines:
        return False
    if not lines[0].startswith("# "):
        return False
    return all(line.startswith("- ") for line in lines[1:])


def check_docs_ssot(repo_root: Path, governance_root: Path) -> Tuple[List[str], List[str]]:
    errors: List[str] = []
    warnings: List[str] = []

    docs_root = repo_root / "docs"
    if not docs_root.is_dir():
        return errors, ["No docs/ folder found. Skipping docs SSOT checks."]

    policy_doc_rel = "docs/agents/25-docs-ssot-policy/docs-ssot-policy.md"
    policy_path = governance_root / policy_doc_rel
    if not policy_path.is_file():
        return ([f"{policy_doc_rel} missing in governance root: {policy_path}"], warnings)

    policy_lines = policy_path.read_text(encoding="utf-8").splitlines()
    enum_line = next((line for line in policy_lines if re.match(r"^doc_type:\s*.+\|.+", line)), None)
    if not enum_line:
        return (
            [f"Doc header enum not found in {policy_doc_rel} (expected 'doc_type: ...|...')."],
            warnings,
        )

    allowed_doc_types = {
        part.strip() for part in re.sub(r"^doc_type:\s*", "", enum_line).split("|") if part.strip()
    }
    migrated_router_leaves, map_errors = _load_migrated_router_leaves(governance_root)
    errors.extend(map_errors)

    doc_dirs = [docs_root]
    doc_dirs.extend(sorted((path for path in docs_root.rglob("*") if path.is_dir()), key=lambda p: p.as_posix()))

    for dir_path in doc_dirs:
        index_path = dir_path / "index.md"
        if not index_path.is_file():
            errors.append(f"Missing folder index: {index_path}")
            continue

        index_text = index_path.read_text(encoding="utf-8", errors="replace")
        direct_children = [
            child
            for child in sorted(dir_path.iterdir(), key=lambda path: path.name.lower())
            if child.name != "index.md" and not child.name.startswith(".")
        ]
        rel_dir = dir_path.relative_to(docs_root).as_posix()
        is_router_exempt = _is_docs_router_exempt(docs_root, dir_path)
        direct_markdown_children = [
            child for child in direct_children if child.is_file() and child.suffix.lower() == ".md"
        ]

        if not is_router_exempt and not _router_looks_routing_only(index_text):
            errors.append(
                "Docs folder index must remain routing-only (title plus bullet links only): "
                f"{index_path}"
            )

        if not is_router_exempt and len(direct_markdown_children) > 1:
            errors.append(
                "Docs narrative folders must contain at most one canonical non-index markdown doc: "
                f"{dir_path}"
            )

        expected_leaf = migrated_router_leaves.get(rel_dir)
        if expected_leaf is not None:
            if len(direct_markdown_children) != 1 or direct_markdown_children[0].name != expected_leaf:
                errors.append(
                    f"Migrated narrative folder must contain canonical leaf '{expected_leaf}': {dir_path}"
                )

        if not direct_children:
            continue

        link_targets = _extract_markdown_link_targets(index_text)
        if index_text.count("Required when:") < len(direct_children):
            errors.append(
                "Folder index must include a 'Required when:' route for each direct child: "
                f"{index_path}"
            )

        for child in direct_children:
            if not _index_targets_child(link_targets, child):
                errors.append(
                    f"Folder index is missing a markdown link to direct child '{child.name}': {index_path}"
                )

    for md_file in docs_root.rglob("*.md"):
        rel = md_file.relative_to(docs_root).as_posix()
        skill_match = re.match(r"^agents/skills/([^/]+)/", rel)
        if skill_match:
            skill_root = docs_root / "agents" / "skills" / skill_match.group(1)
            if (skill_root / "SKILL.md").is_file():
                continue
        if re.match(r"^agents/subagents/[^/]+/", rel):
            continue
        if rel == "index.md" or rel.endswith("/index.md"):
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
    required_files = [
        "README.md",
        "docs/project/index.md",
        "docs/project/goal/index.md",
        "docs/project/goal/goal.md",
        "docs/project/rules/index.md",
        "docs/project/rules/rules.md",
        "docs/project/architecture/index.md",
        "docs/project/architecture/architecture.md",
        "docs/project/learning/index.md",
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
            "docs/project/index.md",
            "AGENTS.md",
            f"{governance_prefix}docs/agents/platforms/00-platform-runtime-standards/platform-runtime-standards.md",
            f"{governance_prefix}docs/agents/platforms/index.md",
            f"{governance_prefix}docs/agents/platforms/runtime-projections.json",
            f"{governance_prefix}docs/agents/integrations/index.md",
            f"{governance_prefix}scripts/setup_repo_platform_assets.ps1",
            f"{governance_prefix}scripts/check_docs_ssot.ps1",
            f"{governance_prefix}scripts/check_docs_router_contract/main.py",
            f"{governance_prefix}scripts/check_agents_manifest.ps1",
            f"{governance_prefix}scripts/check_project_docs.ps1",
            f"{governance_prefix}scripts/check_repo_hygiene.ps1",
            f"{governance_prefix}scripts/check_change_records.ps1",
            f"{governance_prefix}scripts/check_folder_architecture/main.py",
            f"{governance_prefix}scripts/check_python_safety/main.py",
        ]
        for ref in required_refs:
            if ref.lower() not in readme_text_lower:
                errors.append(f"README.md must reference: {ref}")

    proj_index = repo_root / "docs/project/index.md"
    if proj_index.is_file():
        index_text_lower = proj_index.read_text(encoding="utf-8").lower()
        for ref in [
            "docs/project/goal/index.md",
            "docs/project/rules/index.md",
            "docs/project/architecture/index.md",
            "docs/project/learning/index.md",
        ]:
            if ref.lower() not in index_text_lower:
                errors.append(f"docs/project/index.md must reference {ref}")

    migrated_router_leaves, map_errors = _load_migrated_router_leaves(governance_root)
    errors.extend(map_errors)
    required_router_leaf_refs = {
        f"docs/{router_rel}/index.md": leaf
        for router_rel, leaf in migrated_router_leaves.items()
        if router_rel.startswith("project/")
    }
    for router_rel, leaf_ref in required_router_leaf_refs.items():
        router_path = repo_root / router_rel
        if not router_path.is_file():
            continue
        router_text = router_path.read_text(encoding="utf-8")
        link_targets = _extract_markdown_link_targets(router_text)
        if leaf_ref not in link_targets:
            errors.append(f"{router_rel} must reference {leaf_ref}")

    return errors
