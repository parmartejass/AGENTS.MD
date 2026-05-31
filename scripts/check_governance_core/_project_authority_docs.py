from __future__ import annotations
import re
from pathlib import Path
from typing import List
try:
    from ._current_work_authority import validate_current_work_doc
    from ._docs_routes import extract_route_targets
    from ._entrypoint_contracts import (
        docs_contract_from_payload,
        load_entrypoint_contracts,
        resolve_docs_router_filename,
        resolve_primary_leaf_filename,
        validate_registry_paths,
    )
    from ._project_authority_records import (
        _validate_contains_fields,
        _validate_record_shape,
    )
except ImportError:  # pragma: no cover - script-path execution
    from _current_work_authority import validate_current_work_doc
    from _docs_routes import extract_route_targets
    from _entrypoint_contracts import (
        docs_contract_from_payload,
        load_entrypoint_contracts,
        resolve_docs_router_filename,
        resolve_primary_leaf_filename,
        validate_registry_paths,
    )
    from _project_authority_records import (
        _validate_contains_fields,
        _validate_record_shape,
    )
def _validate_project_authority_memory_docs(repo_root: Path) -> List[str]:
    errors: List[str] = []
    errors.extend(validate_current_work_doc(repo_root))
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
                "Current work",
                "Context",
                "Decision/change",
                "Validation",
                "Evidence/version",
                "Commit/push state",
                "Superseded by",
                "Follow-up required",
            ],
            allowed_statuses={"proposed", "accepted", "corrected", "deprecated", "superseded", "rolled-back"},
            duplicate_key_fields=["Change type", "Changed owners/files", "Decision/change"],
        )
    return errors
def _validate_project_optional_leaf_routes(repo_root: Path) -> List[str]:
    errors: List[str] = []
    required_routes = {
        "docs/project/goal/current-work.md": "docs/project/goal/goal_index.md",
    }
    optional_routes = {
        "docs/project/architecture/protected-behavior.md": "docs/project/architecture/architecture_index.md",
        "docs/project/learning/changelog.md": "docs/project/learning/learning_index.md",
    }
    for leaf_rel, router_rel in required_routes.items():
        leaf = repo_root / leaf_rel
        router = repo_root / router_rel
        if not router.is_file():
            errors.append(f"Missing required file: {router_rel}")
            continue
        route_targets, route_errors = extract_route_targets(router.read_text(encoding="utf-8"))
        for issue in route_errors:
            errors.append(f"{router_rel}: {issue}")
        if Path(leaf_rel).name not in route_targets:
            errors.append(f"{router_rel} must reference required {Path(leaf_rel).name}")
        for target in route_targets:
            if target.lower().endswith(".md") and not (router.parent / target).is_file():
                errors.append(f"{router_rel} references missing local route target: {target}")
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
        "docs/project/goal/current-work.md",
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
