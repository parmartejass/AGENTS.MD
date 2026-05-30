from __future__ import annotations
import re
from pathlib import Path
from typing import Dict, List, Tuple
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
def _record_blocks(text: str, prefix: str) -> List[str]:
    heading_pattern = re.compile(rf"^###\s+({re.escape(prefix)}-[0-9]{{8}}-[0-9]{{3}})\b.*$", re.MULTILINE)
    matches = list(heading_pattern.finditer(text))
    blocks: List[str] = []
    for index, match in enumerate(matches):
        start = match.start()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        blocks.append(text[start:end])
    return blocks
def _malformed_record_headings(text: str, prefix: str) -> List[str]:
    valid_heading = re.compile(rf"^###\s+{re.escape(prefix)}-[0-9]{{8}}-[0-9]{{3}}\b.*$", re.MULTILINE)
    malformed: List[str] = []
    record_like_heading = re.compile(
        rf"^###\s+{re.escape(prefix)}(?:[-_][^\n]*|\b[^\n]*)$",
        flags=re.IGNORECASE | re.MULTILINE,
    )
    for match in record_like_heading.finditer(text):
        line = match.group(0).strip()
        if not valid_heading.match(line):
            malformed.append(line)
    return malformed
def _validate_contains_fields(errors: List[str], rel_path: str, text: str, fields: List[str]) -> None:
    for field in fields:
        if field not in text:
            errors.append(f"{rel_path} must contain required field/section: {field}")
def _field_value(block: str, field: str) -> str | None:
    match = re.search(rf"^- {re.escape(field)}:[^\S\r\n]*(.*)[^\S\r\n]*$", block, flags=re.MULTILINE)
    if match is None:
        return None
    return match.group(1).strip().strip("`").strip()
def _field_values(block: str, field: str) -> List[str]:
    return [
        match.group(1).strip().strip("`").strip()
        for match in re.finditer(rf"^- {re.escape(field)}:[^\S\r\n]*(.*)[^\S\r\n]*$", block, flags=re.MULTILINE)
    ]
def _is_placeholder_value(value: str) -> bool:
    normalized = value.strip().lower()
    return (
        not normalized
        or normalized in {"todo", "tbd", "fixme", "pending", "..."}
        or (normalized.startswith("<") and normalized.endswith(">"))
    )
def _normalized_record_key(block: str, fields: List[str]) -> Tuple[str, ...]:
    values: List[str] = []
    for field in fields:
        value = _field_value(block, field) or ""
        values.append(re.sub(r"\s+", " ", value).strip().lower())
    return tuple(values)
def _validate_record_shape(
    errors: List[str],
    rel_path: str,
    text: str,
    *,
    prefix: str,
    required_fields: List[str],
    allowed_statuses: set[str],
    allow_empty: bool = False,
    empty_marker: str | None = None,
    duplicate_key_fields: List[str] | None = None,
    allowed_field_values: Dict[str, set[str]] | None = None,
) -> None:
    for heading in _malformed_record_headings(text, prefix):
        errors.append(f"{rel_path} contains malformed {prefix} record heading: {heading}")
    blocks = _record_blocks(text, prefix)
    if not blocks:
        if allow_empty and (empty_marker is None or empty_marker in text):
            return
        errors.append(f"{rel_path} must contain at least one {prefix}-YYYYMMDD-NNN record.")
        return
    seen_ids = set()
    seen_structural_keys: Dict[Tuple[str, ...], str] = {}
    for block in blocks:
        id_match = re.match(rf"^###\s+({re.escape(prefix)}-[0-9]{{8}}-[0-9]{{3}})\b", block)
        if not id_match:
            errors.append(f"{rel_path} contains malformed {prefix} record heading.")
            continue
        record_id = id_match.group(1)
        if record_id in seen_ids:
            errors.append(f"{rel_path} contains duplicate record id: {record_id}")
        seen_ids.add(record_id)
        for field in required_fields:
            values = _field_values(block, field)
            if not values:
                errors.append(f"{rel_path} record {record_id} missing required field: {field}")
                continue
            if len(values) > 1:
                errors.append(f"{rel_path} record {record_id} contains duplicate field: {field}")
            for value in values:
                if _is_placeholder_value(value) and value.upper() != "N/A":
                    errors.append(f"{rel_path} record {record_id} has blank or placeholder value for field: {field}")
        status_values = _field_values(block, "Status")
        if not status_values:
            if "Status" not in required_fields:
                errors.append(f"{rel_path} record {record_id} missing required field: Status")
        else:
            for status in status_values:
                if status not in allowed_statuses:
                    errors.append(f"{rel_path} record {record_id} has invalid status: {status}")
        if duplicate_key_fields:
            key = _normalized_record_key(block, duplicate_key_fields)
            if all(key):
                previous_id = seen_structural_keys.get(key)
                if previous_id is not None:
                    errors.append(
                        f"{rel_path} records {previous_id} and {record_id} duplicate structural authority key: "
                        f"{', '.join(duplicate_key_fields)}"
                    )
                else:
                    seen_structural_keys[key] = record_id
        if allowed_field_values:
            for field, allowed_values in allowed_field_values.items():
                for value in _field_values(block, field):
                    if value not in allowed_values:
                        errors.append(f"{rel_path} record {record_id} has invalid {field}: {value}")
def _validate_project_authority_memory_docs(repo_root: Path) -> List[str]:
    errors: List[str] = []
    current_work = repo_root / "docs/project/goal/current-work.md"
    if current_work.is_file():
        rel = current_work.relative_to(repo_root).as_posix()
        text = current_work.read_text(encoding="utf-8")
        _validate_contains_fields(
            errors,
            rel,
            text,
            ["Status:", "Work item ID:", "Last updated:", "## Next safe action", "## Clear Rule"],
        )
        id_match = re.search(r"Work item ID:\s*`?(CW-[0-9]{8}-[0-9]{3})`?", text)
        if not id_match:
            errors.append(f"{rel} must contain a CW-YYYYMMDD-NNN Work item ID.")
        status_values = re.findall(r"^Status:\s*`?([^`\n]+)`?\s*$", text, flags=re.MULTILINE)
        if status_values:
            if len(status_values) > 1:
                errors.append(f"{rel} contains duplicate Status fields.")
            for status_value in status_values:
                status = status_value.strip()
                if status not in {"active", "paused", "blocked", "ready-to-clear"}:
                    errors.append(f"{rel} has invalid Status: {status}")
        else:
            errors.append(f"{rel} must contain a Status value.")
    data_truth = repo_root / "docs/project/data-truth/data-truth.md"
    if data_truth.is_file():
        rel = data_truth.relative_to(repo_root).as_posix()
        text = data_truth.read_text(encoding="utf-8")
        _validate_contains_fields(errors, rel, text, ["## Record Schema", "## Records"])
        _validate_record_shape(
            errors,
            rel,
            text,
            prefix="DT",
            required_fields=[
                "Status",
                "Truth type",
                "Owner SSOT",
                "Doc role",
                "Scope",
                "Statement",
                "Provenance",
                "Consumers",
                "Validation",
                "Change rule",
                "Related protected behavior",
                "Related rules",
                "Supersedes",
                "Evidence/version",
                "Re-verification trigger",
                "Superseded by",
            ],
            allowed_statuses={"active", "proposed", "deprecated", "superseded"},
            allow_empty=True,
            empty_marker="Reviewed-empty date:",
            duplicate_key_fields=["Truth type", "Owner SSOT", "Scope"],
            allowed_field_values={
                "Truth type": {
                    "input-artifact",
                    "source-artifact",
                    "workbook",
                    "schema",
                    "config",
                    "constant",
                    "default",
                    "external-system",
                    "mapping",
                    "threshold",
                    "path",
                    "sample-data",
                    "document-owned",
                },
                "Doc role": {"owner", "router", "provenance", "interpretation", "validation"},
            },
        )
    protected_behavior = repo_root / "docs/project/architecture/protected-behavior.md"
    if protected_behavior.is_file():
        rel = protected_behavior.relative_to(repo_root).as_posix()
        text = protected_behavior.read_text(encoding="utf-8")
        _validate_record_shape(
            errors,
            rel,
            text,
            prefix="PB",
            required_fields=[
                "Status",
                "Behavior",
                "Scope",
                "Protected because",
                "Current mechanism",
                "Required equivalence",
                "Verification",
                "Evidence/version",
                "Re-verification trigger",
                "Weakening rule",
                "Related data truths",
                "Superseded by",
            ],
            allowed_statuses={"active", "proposed", "deprecated", "superseded"},
            duplicate_key_fields=["Behavior", "Scope"],
        )
    changelog = repo_root / "docs/project/learning/changelog.md"
    if changelog.is_file():
        rel = changelog.relative_to(repo_root).as_posix()
        text = changelog.read_text(encoding="utf-8")
        _validate_record_shape(
            errors,
            rel,
            text,
            prefix="CH",
            required_fields=[
                "Date",
                "Status",
                "Change type",
                "Changed owners/files",
                "Context",
                "Decision/change",
                "Validation",
                "Evidence/version",
                "Superseded by",
                "Follow-up required",
            ],
            allowed_statuses={"proposed", "accepted", "corrected", "deprecated", "superseded", "rolled-back"},
            duplicate_key_fields=["Change type", "Changed owners/files", "Decision/change"],
        )
    return errors
def _validate_project_optional_leaf_routes(repo_root: Path) -> List[str]:
    errors: List[str] = []
    optional_routes = {
        "docs/project/goal/current-work.md": "docs/project/goal/goal_index.md",
        "docs/project/architecture/protected-behavior.md": "docs/project/architecture/architecture_index.md",
        "docs/project/learning/changelog.md": "docs/project/learning/learning_index.md",
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
def check_project_docs(repo_root: Path, governance_rel_path: str, governance_root: Path) -> List[str]:
    errors: List[str] = []
    payload, registry_errors = load_entrypoint_contracts(governance_root)
    errors.extend(registry_errors)
    errors.extend(validate_registry_paths(payload) if payload else [])
    if errors:
        return errors
    docs_contract = docs_contract_from_payload(payload)
    policy_path = governance_root / "docs/agents/25-docs-ssot-policy/docs-ssot-policy.md"
    if policy_path.is_file():
        policy_text = policy_path.read_text(encoding="utf-8")
        if "do not create parallel project memory, session history, transcript, or authority-memory doc trees" not in policy_text:
            errors.append("Docs SSOT policy must state the no-parallel-memory-doc-tree rule.")
    else:
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
        "docs/project/learning/learning_index.md",
        "docs/project/learning/learning.md",
    ]
    for rel in required_files:
        if not (repo_root / rel).is_file():
            errors.append(f"Missing required file: {rel}")
    allowed_memory_paths = {
        Path("docs/project/goal/current-work.md"),
        Path("docs/project/architecture/protected-behavior.md"),
        Path("docs/project/learning/changelog.md"),
    }
    forbidden_memory_segments = {
        "memory",
        "memories",
        "authority-memory",
        "bounded-memory",
        "session-memory",
        "transcript-memory",
        "session-logs",
        "transcripts",
    }
    for candidate in (repo_root / "docs").rglob("*"):
        if not candidate.exists():
            continue
        rel_candidate = candidate.relative_to(repo_root)
        if rel_candidate in allowed_memory_paths:
            continue
        normalized_parts = [re.sub(r"[^a-z0-9]+", "-", part.lower()).strip("-") for part in rel_candidate.parts]
        if any(part in forbidden_memory_segments or "memory" in part or "memories" in part or "transcript" in part for part in normalized_parts):
            errors.append(f"Forbidden parallel memory docs path exists: {rel_candidate.as_posix()}")
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
        for child in ("goal", "rules", "architecture", "data-truth", "learning"):
            expected = f"{child}/{resolve_docs_router_filename(child, docs_contract)}"
            if expected not in project_targets:
                errors.append(f"docs/project/project_index.md must reference {expected}")
    for folder_name in ("goal", "rules", "architecture", "data-truth", "learning"):
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
    errors.extend(_validate_project_authority_memory_docs(repo_root))
    errors.extend(_validate_project_optional_leaf_routes(repo_root))
    return errors
