#!/usr/bin/env python3
"""
Cross-platform governance checks.

This script consolidates cross-platform governance checks:
1) check_agents_manifest.ps1
2) check_docs_ssot.ps1
3) check_project_docs.ps1
4) check_repo_hygiene.ps1
5) docs unresolved citation placeholders
6) governance learnings playbook hard-gate parity
7) check_change_records.ps1 equivalent validation
8) optional strict python safety mode
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Sequence, Set, Tuple

logger = logging.getLogger(__name__)
_GIT_LS_FILES_TIMEOUT_SEC = 30
_PYTHON_SAFETY_TIMEOUT_SEC = 120

_BUGFIX_REQUIRED_FIELDS = (
    "symptom_location",
    "authority_fix_point",
    "root_cause_statement",
    "class_of_errors_prevented",
    "mre",
    "tests",
)
_MRE_REQUIRED_FIELDS = (
    "fixture_path",
    "pre_fix_failure_signal",
    "post_fix_pass_signal",
)
_TESTS_REQUIRED_FIELDS = (
    "regression",
    "disconfirming",
    "failure_path",
)
_WITNESS_REQUIRED_FIELDS = (
    "invariant_id",
    "signal",
    "record_location",
    "pass_criteria",
)
_COUNCIL_FULL_REQUIRED_FIELDS = (
    "council_run_id",
    "phase",
    "reviewers",
    "findings",
    "conflicts",
    "reconciliation_decision",
    "residual_risks",
    "go_no_go",
    "verification_links",
)
_COUNCIL_ABBREVIATED_REQUIRED_FIELDS = (
    "findings",
    "residual_risks",
    "go_no_go",
)
_COUNCIL_FULL_ONLY_FIELDS = tuple(
    field for field in _COUNCIL_FULL_REQUIRED_FIELDS if field not in _COUNCIL_ABBREVIATED_REQUIRED_FIELDS
)
_COUNCIL_PHASE_ALLOWED = {"pre_change", "post_change"}
_COUNCIL_GO_NO_GO_ALLOWED = {"go", "hold"}
_GOVERNANCE_OWNER_PREFIXES = (
    "AGENTS.md",
    "agents-manifest.yaml",
    "docs/agents/",
    "scripts/check_",
)
_UNRESOLVED_CITATION_PATTERNS = (
    "cite",
    "entity",
    "image_group",
)


def _configure_logging() -> None:
    handler = logging.StreamHandler(stream=sys.stdout)
    handler.setFormatter(logging.Formatter("%(message)s"))
    logger.handlers.clear()
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


def _resolve_path(path: str | None, default: Path) -> Path:
    if not path:
        return default.resolve()
    return Path(path).expanduser().resolve()


def _is_non_empty(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, tuple, set, dict)):
        return len(value) > 0
    return True


def _as_non_empty_list(value: Any) -> List[Any]:
    if not isinstance(value, list):
        return []
    return [item for item in value if _is_non_empty(item)]


def _context(
    repo_root_arg: str | None, governance_root_arg: str | None, script_root: Path
) -> Tuple[Path, Path, str]:
    governance_root = _resolve_path(governance_root_arg, script_root.parent)
    repo_root = _resolve_path(repo_root_arg, governance_root)

    if not governance_root.is_dir():
        raise RuntimeError(f"Governance root does not exist or is not a directory: {governance_root}")
    if not repo_root.is_dir():
        raise RuntimeError(f"Repo root does not exist or is not a directory: {repo_root}")

    if repo_root_arg is None and governance_root.name == ".governance":
        raise RuntimeError(
            "RepoRoot is required when running from a vendored governance submodule. "
            "Use --repo-root <target repo root> (for example: --repo-root .)."
        )

    try:
        rel_path = governance_root.relative_to(repo_root)
        rel = "." if str(rel_path) == "." else rel_path.as_posix()
    except ValueError:
        rel = os.path.relpath(governance_root, repo_root).replace("\\", "/")

    governance_rel = "" if rel in {".", ""} else rel
    return repo_root, governance_root, governance_rel


def _check_agents_manifest(governance_root: Path) -> List[str]:
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
                m = re.match(r"^([A-Za-z0-9_]+):\s*$", trimmed)
                if m:
                    if profile_key_indent is None:
                        if indent > profiles_indent:
                            profile_key_indent = indent
                            current_profile = m.group(1)
                    elif indent == profile_key_indent:
                        current_profile = m.group(1)

        if not in_profiles:
            m_profiles = re.match(r"^(\s*)profiles:\s*$", line)
            if m_profiles:
                in_profiles = True
                profiles_indent = len(m_profiles.group(1))
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
            m_key = re.match(r"^(\s*)(default_inject|fallback_inject|inject):\s*$", line)
            if m_key:
                in_path_list = True
                path_list_indent = len(m_key.group(1))
                key = m_key.group(2)
                if key == "inject" and in_profiles and current_profile:
                    path_list_key = f"profiles.{current_profile}.inject"
                else:
                    path_list_key = key
                continue

        if not in_path_list:
            continue

        if not trimmed.startswith("- "):
            continue

        dq = re.match(r'^-\s+"([^"]+)"\s*$', trimmed)
        sq = re.match(r"^-\s+'([^']+)'\s*$", trimmed)
        if dq:
            value = dq.group(1)
        elif sq:
            value = sq.group(1)
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


def _check_docs_ssot(repo_root: Path, governance_root: Path) -> Tuple[List[str], List[str]]:
    errors: List[str] = []
    warnings: List[str] = []

    docs_root = repo_root / "docs"
    if not docs_root.is_dir():
        return errors, ["No docs/ folder found. Skipping docs SSOT checks."]

    policy_path = governance_root / "docs/agents/25-docs-ssot-policy.md"
    if not policy_path.is_file():
        return errors + [
            f"docs/agents/25-docs-ssot-policy.md missing in governance root: {policy_path}"
        ], warnings

    policy_lines = policy_path.read_text(encoding="utf-8").splitlines()
    enum_line = next((ln for ln in policy_lines if re.match(r"^doc_type:\s*.+\|.+", ln)), None)
    if not enum_line:
        return errors + [
            "Doc header enum not found in docs/agents/25-docs-ssot-policy.md "
            "(expected 'doc_type: ...|...')."
        ], warnings

    allowed_doc_types = {p.strip() for p in re.sub(r"^doc_type:\s*", "", enum_line).split("|") if p.strip()}

    for md_file in docs_root.rglob("*.md"):
        rel = md_file.relative_to(docs_root).as_posix()
        if rel == "index.md" or re.match(r"^[^/]+/index\.md$", rel):
            continue

        head = md_file.read_text(encoding="utf-8").splitlines()[:25]
        doc_type_line = next((ln for ln in head if ln.startswith("doc_type:")), None)
        if doc_type_line is None:
            errors.append(f"Missing doc header (doc_type) in: {md_file}")
        else:
            doc_type = re.sub(r"^doc_type:\s*", "", doc_type_line).strip()
            if doc_type not in allowed_doc_types:
                errors.append(f"Invalid doc_type '{doc_type}' in: {md_file}")

        if not any(ln.startswith("ssot_owner:") for ln in head):
            errors.append(f"Missing doc header (ssot_owner) in: {md_file}")
        if not any(ln.startswith("update_trigger:") for ln in head):
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


def _check_project_docs(repo_root: Path, governance_rel_path: str) -> List[str]:
    errors: List[str] = []
    required_files = [
        "README.md",
        "docs/project/index.md",
        "docs/project/goal.md",
        "docs/project/rules.md",
        "docs/project/architecture.md",
        "docs/project/learning.md",
    ]
    for rel in required_files:
        if not (repo_root / rel).is_file():
            errors.append(f"Missing required file: {rel}")

    governance_prefix = f"{governance_rel_path.rstrip('/')}/" if governance_rel_path else ""

    readme = repo_root / "README.md"
    if readme.is_file():
        readme_text = readme.read_text(encoding="utf-8")
        required_refs = [
            "docs/project/index.md",
            "AGENTS.md",
            f"{governance_prefix}scripts/check_docs_ssot.ps1",
            f"{governance_prefix}scripts/check_agents_manifest.ps1",
            f"{governance_prefix}scripts/check_project_docs.ps1",
            f"{governance_prefix}scripts/check_repo_hygiene.ps1",
            f"{governance_prefix}scripts/check_change_records.ps1",
            f"{governance_prefix}scripts/check_python_safety.py",
        ]
        for ref in required_refs:
            if ref not in readme_text:
                errors.append(f"README.md must reference: {ref}")

    proj_index = repo_root / "docs/project/index.md"
    if proj_index.is_file():
        index_text = proj_index.read_text(encoding="utf-8")
        for ref in [
            "docs/project/goal.md",
            "docs/project/rules.md",
            "docs/project/architecture.md",
            "docs/project/learning.md",
        ]:
            if ref not in index_text:
                errors.append(f"docs/project/index.md must reference {ref}")

    return errors


def _check_repo_hygiene(repo_root: Path) -> List[str]:
    errors: List[str] = []
    if not (repo_root / ".git").exists():
        return [f"Repo root does not appear to be a git repository: {repo_root}"]

    try:
        result = subprocess.run(
            ["git", "-C", str(repo_root), "ls-files"],
            check=True,
            capture_output=True,
            text=True,
            cwd=repo_root,
            timeout=_GIT_LS_FILES_TIMEOUT_SEC,
        )
    except FileNotFoundError:
        return ["git is required for hygiene checks."]
    except subprocess.TimeoutExpired:
        return [
            f"git ls-files timed out after {_GIT_LS_FILES_TIMEOUT_SEC}s for repo root: {repo_root}"
        ]
    except subprocess.CalledProcessError:
        return [f"git ls-files failed for repo root: {repo_root}"]

    for raw in result.stdout.splitlines():
        path = raw.strip()
        if not path:
            continue
        norm = path.replace("\\", "/")

        if re.search(r"(^|/)__pycache__(/|$)", norm):
            errors.append(f"Tracked Python cache dir/file: {path}")
            continue
        if norm.endswith(".pyc") or norm.endswith(".pyo"):
            errors.append(f"Tracked Python bytecode: {path}")
            continue
        if re.search(r"(^|/)\.DS_Store$", norm) or re.search(r"(^|/)Thumbs\.db$", norm):
            errors.append(f"Tracked OS noise file: {path}")
            continue
        if norm.startswith("templates/python-dual-entry/tests/output/") and (
            norm != "templates/python-dual-entry/tests/output/.gitkeep"
        ):
            errors.append(
                "Tracked template runtime output file (must be ignored; "
                f"docs/generated/ governance artifacts are allowed): {path}"
            )

    return errors


def _check_docs_for_unresolved_citations(repo_root: Path) -> List[str]:
    errors: List[str] = []
    docs_root = repo_root / "docs"
    if not docs_root.is_dir():
        return errors

    for md_file in docs_root.rglob("*.md"):
        try:
            lines = md_file.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError as exc:
            errors.append(f"Failed to read docs file for citation checks: {md_file} ({exc})")
            continue

        for line_no, line in enumerate(lines, start=1):
            if any(marker in line for marker in _UNRESOLVED_CITATION_PATTERNS):
                rel = md_file.relative_to(repo_root).as_posix()
                errors.append(
                    f"Unresolved citation token in {rel}:{line_no}. "
                    "Replace `cite`/`entity`/`image_group` markers with resolvable references."
                )

    return errors


def _extract_hard_gates_from_playbook_block(lines: List[str], start_idx: int) -> List[str]:
    gates: List[str] = []
    for i in range(start_idx, len(lines)):
        stripped = lines[i].strip()
        if stripped.startswith("## "):
            break
        if stripped.startswith("- "):
            gates.append(stripped[2:].strip())
    return gates


def _extract_hard_gates_from_prompt_pack(lines: List[str], start_idx: int) -> List[str]:
    in_code_block = False
    in_hard_gate_section = False
    gates: List[str] = []

    for i in range(start_idx, len(lines)):
        stripped = lines[i].strip()
        if stripped.startswith("## ") and i > start_idx:
            break

        if stripped.startswith("```"):
            in_code_block = not in_code_block
            continue

        if not in_code_block:
            continue

        if stripped == "Hard gates:":
            in_hard_gate_section = True
            continue

        if not in_hard_gate_section:
            continue

        if stripped.startswith("- "):
            gates.append(stripped[2:].strip())
            continue

        if gates and stripped == "":
            break

        if gates and not stripped.startswith("- "):
            break

    return gates


def _check_governance_playbook_hard_gates(governance_root: Path) -> List[str]:
    errors: List[str] = []
    playbook = governance_root / "docs/agents/playbooks/governance-learnings-template.md"
    if not playbook.is_file():
        return [f"Missing governance learnings playbook: {playbook}"]

    lines = playbook.read_text(encoding="utf-8").splitlines()
    canonical_heading = "## Hard gates (canonical; keep wording in sync)"
    prompt_heading = "## Prompt pack (copy/paste into any chat)"

    canonical_indices = [idx for idx, line in enumerate(lines) if line.strip() == canonical_heading]
    if len(canonical_indices) != 1:
        errors.append(
            "Governance learnings playbook must contain exactly one canonical Hard gates section."
        )
        return errors

    prompt_indices = [idx for idx, line in enumerate(lines) if line.strip() == prompt_heading]
    if len(prompt_indices) != 1:
        errors.append("Governance learnings playbook must contain exactly one Prompt pack section.")
        return errors

    canonical_gates = _extract_hard_gates_from_playbook_block(lines, canonical_indices[0] + 1)
    prompt_gates = _extract_hard_gates_from_prompt_pack(lines, prompt_indices[0] + 1)

    if not canonical_gates:
        errors.append("Canonical Hard gates section is empty in governance learnings playbook.")
        return errors
    if not prompt_gates:
        errors.append("Prompt pack Hard gates block is missing or empty in governance learnings playbook.")
        return errors
    if canonical_gates != prompt_gates:
        errors.append(
            "Prompt pack Hard gates block does not match canonical Hard gates section in "
            "docs/agents/playbooks/governance-learnings-template.md."
        )
    return errors


def _load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise RuntimeError(f"Failed to read JSON file {path}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Failed to parse JSON file {path}: {exc}") from exc


def _record_is_governance_scoped(record: Dict[str, Any]) -> bool:
    owners = record.get("ssot_owner_paths")
    if not isinstance(owners, list):
        return False

    for owner in owners:
        if not isinstance(owner, str):
            continue
        normalized = owner.strip().replace("\\", "/")
        if normalized.startswith(_GOVERNANCE_OWNER_PREFIXES):
            return True
    return False


def _check_governance_specific_record_fields(
    path: Path, record: Dict[str, Any], errors: List[str]
) -> bool:
    record_has_errors = False
    change_type = record.get("change_type")
    if change_type != "docs":
        return record_has_errors
    if not _record_is_governance_scoped(record):
        return record_has_errors

    council = record.get("council_summary")
    if not isinstance(council, dict):
        errors.append(
            f"Governance docs change record missing object field 'council_summary' in {path}."
        )
        return True

    missing_full_fields = [
        field for field in _COUNCIL_FULL_REQUIRED_FIELDS if not _is_non_empty(council.get(field))
    ]
    missing_abbreviated_fields = [
        field
        for field in _COUNCIL_ABBREVIATED_REQUIRED_FIELDS
        if not _is_non_empty(council.get(field))
    ]
    has_full_only_keys = any(field in council for field in _COUNCIL_FULL_ONLY_FIELDS)

    council_mode = "full"
    if missing_full_fields:
        if has_full_only_keys:
            for field in missing_full_fields:
                errors.append(
                    f"Governance docs council_summary missing or empty '{field}' in {path}."
                )
            errors.append(
                "Governance docs council_summary includes full-summary fields and must satisfy "
                f"the full required set {list(_COUNCIL_FULL_REQUIRED_FIELDS)} in {path}."
            )
            record_has_errors = True
        elif missing_abbreviated_fields:
            for field in missing_abbreviated_fields:
                errors.append(
                    f"Governance docs council_summary missing or empty '{field}' in {path}."
                )
            errors.append(
                "Governance docs council_summary must provide either the full summary fields "
                f"{list(_COUNCIL_FULL_REQUIRED_FIELDS)} or the abbreviated fields "
                f"{list(_COUNCIL_ABBREVIATED_REQUIRED_FIELDS)} in {path}."
            )
            record_has_errors = True
        else:
            council_mode = "abbreviated"

    if council_mode == "full":
        reviewers = council.get("reviewers")
        if not isinstance(reviewers, list) or not _as_non_empty_list(reviewers):
            errors.append(
                f"Governance docs council_summary.reviewers must be a non-empty array in {path}."
            )
            record_has_errors = True

    findings = council.get("findings")
    findings_valid = isinstance(findings, list) and bool(_as_non_empty_list(findings))
    if council_mode == "full":
        if not findings_valid:
            errors.append(
                f"Governance docs council_summary.findings must be a non-empty array in {path}."
            )
            record_has_errors = True
    elif council_mode == "abbreviated":
        no_findings_literal = isinstance(findings, str) and findings.strip().lower() == "no findings"
        if not findings_valid and not no_findings_literal:
            errors.append(
                "Governance docs abbreviated council_summary.findings must be a non-empty array "
                f"or the explicit string 'No findings' in {path}."
            )
            record_has_errors = True

    if council_mode == "full":
        verification_links = council.get("verification_links")
        verification_links_valid = (
            isinstance(verification_links, list)
            and verification_links
            and all(isinstance(link, str) and link.strip() for link in verification_links)
        )
        if not verification_links_valid:
            errors.append(
                f"Governance docs council_summary.verification_links must be a non-empty array of strings in {path}."
            )
            record_has_errors = True

    phase = council.get("phase")
    if _is_non_empty(phase) and phase not in _COUNCIL_PHASE_ALLOWED:
        errors.append(
            f"Governance docs council_summary.phase must be one of "
            f"{sorted(_COUNCIL_PHASE_ALLOWED)} in {path}."
        )
        record_has_errors = True

    go_no_go = council.get("go_no_go")
    if _is_non_empty(go_no_go) and go_no_go not in _COUNCIL_GO_NO_GO_ALLOWED:
        errors.append(
            f"Governance docs council_summary.go_no_go must be one of "
            f"{sorted(_COUNCIL_GO_NO_GO_ALLOWED)} in {path}."
        )
        record_has_errors = True

    validation_context = record.get("validation_context")
    if not isinstance(validation_context, dict):
        errors.append(
            f"Governance docs change record missing object field 'validation_context' in {path}."
        )
        return True

    for field in ("intended_environment", "evidence_plan", "release_gate_decision"):
        if not _is_non_empty(validation_context.get(field)):
            errors.append(f"Governance docs validation_context missing or empty '{field}' in {path}.")
            record_has_errors = True

    traceability_refs = validation_context.get("traceability_refs")
    if not isinstance(traceability_refs, list) or not _as_non_empty_list(traceability_refs):
        errors.append(
            f"Governance docs validation_context.traceability_refs must be a non-empty array in {path}."
        )
        record_has_errors = True
    return record_has_errors


def _check_change_records(
    repo_root: Path, governance_root: Path, *, require_records: bool
) -> Tuple[List[str], List[str]]:
    errors: List[str] = []
    notes: List[str] = []

    records_root = repo_root / "docs/project/change-records"
    schema_path = governance_root / "docs/agents/schemas/change-record.schema.json"
    required_marker = records_root / ".required"
    records_required = require_records or required_marker.is_file()

    if not schema_path.is_file():
        return [f"Missing change-record schema: {schema_path}"], notes

    if not records_root.is_dir():
        if records_required:
            return [f"Missing change-record directory: {records_root}"], notes
        notes.append("SKIPPED: No change-record directory found at docs/project/change-records.")
        return errors, notes

    record_files = sorted(records_root.glob("*.json"))
    if not record_files:
        if records_required:
            return [f"No change-record files found under: {records_root}"], notes
        notes.append("SKIPPED: No change-record files (*.json) found under docs/project/change-records.")
        return errors, notes

    try:
        schema = _load_json(schema_path)
    except RuntimeError as exc:
        return [str(exc)], notes

    allowed_change_types = schema.get("properties", {}).get("change_type", {}).get("enum", [])
    if not isinstance(allowed_change_types, list) or not allowed_change_types:
        errors.append(f"Schema missing properties.change_type.enum in: {schema_path}")
        return errors, notes

    base_required = schema.get("required", [])
    if not isinstance(base_required, list) or not base_required:
        errors.append(f"Schema missing required field list in: {schema_path}")
        return errors, notes

    valid_records = 0
    for record_file in record_files:
        try:
            record = _load_json(record_file)
        except RuntimeError as exc:
            errors.append(str(exc))
            continue
        if not isinstance(record, dict):
            errors.append(f"Parsed record is not an object in {record_file}.")
            continue

        record_has_errors = False
        for field in base_required:
            if not _is_non_empty(record.get(field)):
                errors.append(f"Missing or empty required field '{field}' in {record_file}.")
                record_has_errors = True

        change_type = record.get("change_type")
        if _is_non_empty(change_type) and change_type not in allowed_change_types:
            errors.append(
                f"Unknown change_type '{change_type}' in {record_file}. "
                f"Allowed values: {', '.join(allowed_change_types)}."
            )
            record_has_errors = True

        for field_name in ("invariants", "ssot_owner_paths", "verification_commands"):
            field_value = record.get(field_name)
            if not isinstance(field_value, list) or not field_value:
                errors.append(f"'{field_name}' must be a non-empty JSON array in {record_file}.")
                record_has_errors = True
                continue
            for idx, item in enumerate(field_value, start=1):
                if not isinstance(item, str) or not item.strip():
                    errors.append(
                        f"{field_name}[{idx}] must be a non-empty string in {record_file}."
                    )
                    record_has_errors = True

        witnesses = record.get("witnesses")
        if not isinstance(witnesses, list) or not witnesses:
            errors.append(f"'witnesses' must be a non-empty JSON array in {record_file}.")
            record_has_errors = True
        else:
            for idx, witness in enumerate(witnesses, start=1):
                if not isinstance(witness, dict):
                    errors.append(f"witnesses[{idx}] must be an object in {record_file}.")
                    record_has_errors = True
                    continue
                for required_field in _WITNESS_REQUIRED_FIELDS:
                    if not _is_non_empty(witness.get(required_field)):
                        errors.append(
                            f"witnesses[{idx}] missing or empty '{required_field}' in {record_file}."
                        )
                        record_has_errors = True

        if change_type in {"bugfix", "regression"}:
            for field in _BUGFIX_REQUIRED_FIELDS:
                if not _is_non_empty(record.get(field)):
                    errors.append(
                        f"Bugfix/regression record missing or empty '{field}' in {record_file}."
                    )
                    record_has_errors = True

            mre = record.get("mre")
            if not isinstance(mre, dict):
                errors.append(f"mre must be an object in {record_file}.")
                record_has_errors = True
            else:
                for field in _MRE_REQUIRED_FIELDS:
                    if not _is_non_empty(mre.get(field)):
                        errors.append(f"mre missing or empty '{field}' in {record_file}.")
                        record_has_errors = True

            tests = record.get("tests")
            if not isinstance(tests, dict):
                errors.append(f"tests must be an object in {record_file}.")
                record_has_errors = True
            else:
                for field in _TESTS_REQUIRED_FIELDS:
                    if not _is_non_empty(tests.get(field)):
                        errors.append(f"tests missing or empty '{field}' in {record_file}.")
                        record_has_errors = True

        governance_errors = _check_governance_specific_record_fields(record_file, record, errors)
        if governance_errors:
            record_has_errors = True
        if not record_has_errors:
            valid_records += 1

    if not errors:
        notes.append(f"Change record checks passed. Valid records: {valid_records}")
    return errors, notes


def _run_python_safety_check(
    repo_root: Path, governance_root: Path, *, fail_on_warnings: bool
) -> Tuple[List[str], List[str]]:
    errors: List[str] = []
    notes: List[str] = []

    safety_script = governance_root / "scripts/check_python_safety.py"
    if not safety_script.is_file():
        return [f"Missing Python safety script: {safety_script}"], notes

    cmd = [sys.executable, str(safety_script), "--root", str(repo_root)]
    if fail_on_warnings:
        cmd.append("--fail-on-warnings")

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=repo_root,
            timeout=_PYTHON_SAFETY_TIMEOUT_SEC,
        )
    except FileNotFoundError:
        return ["Python interpreter not found while running check_python_safety.py."], notes
    except subprocess.TimeoutExpired:
        return [
            f"check_python_safety.py timed out after {_PYTHON_SAFETY_TIMEOUT_SEC}s."
        ], notes

    output_lines = (result.stdout or "").splitlines()
    notes.extend(output_lines)
    if result.returncode != 0:
        stderr = (result.stderr or "").strip()
        if stderr:
            notes.append(stderr)
        errors.append(
            "Python safety baseline check failed. "
            "Run scripts/check_python_safety.py directly for details."
        )
    return errors, notes


def main(argv: Sequence[str]) -> int:
    _configure_logging()
    parser = argparse.ArgumentParser(
        description=(
            "Run cross-platform governance checks for manifest/docs/project-docs/hygiene, "
            "governance playbook parity, unresolved citation markers, and change-record validation."
        )
    )
    parser.add_argument("--repo-root", help="Target repo root (default: governance root).")
    parser.add_argument(
        "--governance-root",
        help="Governance root that contains AGENTS.md and agents-manifest.yaml "
        "(default: parent of this script).",
    )
    parser.add_argument(
        "--require-records",
        action="store_true",
        help=(
            "Require docs/project/change-records/*.json (same behavior as "
            "docs/project/change-records/.required marker)."
        ),
    )
    parser.add_argument(
        "--fail-on-safety-warnings",
        action="store_true",
        help="Run scripts/check_python_safety.py with --fail-on-warnings.",
    )
    args = parser.parse_args(argv)

    script_root = Path(__file__).resolve().parent
    try:
        repo_root, governance_root, governance_rel = _context(
            args.repo_root, args.governance_root, script_root
        )
    except RuntimeError as err:
        logger.error("ERROR: %s", err)
        return 1

    total_errors = 0

    manifest_errors = _check_agents_manifest(governance_root)
    if manifest_errors:
        for issue in manifest_errors:
            logger.error("ERROR: %s", issue)
        total_errors += len(manifest_errors)
    else:
        logger.info("Agents manifest checks passed.")

    docs_errors, docs_warnings = _check_docs_ssot(repo_root, governance_root)
    if docs_errors:
        for issue in docs_errors:
            logger.error("ERROR: %s", issue)
        total_errors += len(docs_errors)
    else:
        logger.info("Docs SSOT checks passed.")
    for warn in docs_warnings:
        logger.warning("WARNING: %s", warn)

    project_errors = _check_project_docs(repo_root, governance_rel)
    if project_errors:
        for issue in project_errors:
            logger.error("ERROR: %s", issue)
        total_errors += len(project_errors)
    else:
        logger.info("Project docs checks passed.")

    hygiene_errors = _check_repo_hygiene(repo_root)
    if hygiene_errors:
        for issue in hygiene_errors:
            logger.error("ERROR: %s", issue)
        total_errors += len(hygiene_errors)
    else:
        logger.info("Repo hygiene checks passed.")

    unresolved_citation_errors = _check_docs_for_unresolved_citations(repo_root)
    if unresolved_citation_errors:
        for issue in unresolved_citation_errors:
            logger.error("ERROR: %s", issue)
        total_errors += len(unresolved_citation_errors)
    else:
        logger.info("Docs unresolved-citation checks passed.")

    playbook_errors = _check_governance_playbook_hard_gates(governance_root)
    if playbook_errors:
        for issue in playbook_errors:
            logger.error("ERROR: %s", issue)
        total_errors += len(playbook_errors)
    else:
        logger.info("Governance playbook hard-gate parity checks passed.")

    change_record_errors, change_record_notes = _check_change_records(
        repo_root, governance_root, require_records=args.require_records
    )
    if change_record_errors:
        for issue in change_record_errors:
            logger.error("ERROR: %s", issue)
        total_errors += len(change_record_errors)
    else:
        if change_record_notes:
            for note in change_record_notes:
                logger.info(note)
        else:
            logger.info("Change record checks passed.")

    if args.fail_on_safety_warnings:
        safety_errors, safety_notes = _run_python_safety_check(
            repo_root, governance_root, fail_on_warnings=True
        )
        for note in safety_notes:
            logger.info(note)
        if safety_errors:
            for issue in safety_errors:
                logger.error("ERROR: %s", issue)
            total_errors += len(safety_errors)
        else:
            logger.info("Python safety strict-mode checks passed.")

    if total_errors > 0:
        logger.error("Governance core checks failed: %s issue(s).", total_errors)
        return 1

    logger.info("Governance core checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
