from __future__ import annotations
from pathlib import Path
from typing import Any, Dict, List, Tuple
try:
    from ._shared import as_non_empty_list, is_non_empty, load_json
except ImportError:  # pragma: no cover - script-path execution
    from _shared import as_non_empty_list, is_non_empty, load_json
BUGFIX_REQUIRED_FIELDS = (
    "symptom_location",
    "authority_fix_point",
    "root_cause_statement",
    "class_of_errors_prevented",
    "mre",
    "tests",
)
MRE_REQUIRED_FIELDS = ("fixture_path", "pre_fix_failure_signal", "post_fix_pass_signal")
TESTS_REQUIRED_FIELDS = ("regression", "disconfirming", "failure_path")
WITNESS_REQUIRED_FIELDS = ("invariant_id", "signal", "record_location", "pass_criteria")
COUNCIL_FULL_REQUIRED_FIELDS = (
    "council_run_id",
    "phase",
    "intent_coverage",
    "reviewers",
    "findings",
    "conflicts",
    "reconciliation_decision",
    "residual_risks",
    "go_no_go",
    "verification_links",
)
COUNCIL_ABBREVIATED_REQUIRED_FIELDS = (
    "intent_coverage",
    "findings",
    "residual_risks",
    "go_no_go",
)
COUNCIL_FULL_ONLY_FIELDS = tuple(
    field
    for field in COUNCIL_FULL_REQUIRED_FIELDS
    if field not in COUNCIL_ABBREVIATED_REQUIRED_FIELDS
)
COUNCIL_PHASE_ALLOWED = {"pre_change", "post_change"}
COUNCIL_GO_NO_GO_ALLOWED = {"go", "hold"}
COUNCIL_INTENT_REQUIRED = {
    "ssot_duplication",
    "silent_error",
    "edge_case",
    "resource_security_perf",
}
GOVERNANCE_OWNER_PREFIXES = (
    "AGENTS.md",
    "agents-manifest.yaml",
    "docs/agents/",
    "scripts/check_",
)
RETIRED_REF_PREFIX = "retired:"
VENDORED_GOVERNANCE_PREFIX = ".governance/"
RETIRED_REFERENCE_PATTERNS = (
    "docs/agents/acp/",
    "docs/agents/automation/",
    "docs/agents/integrations/",
    "docs/generated/",
    "templates/automation-loop/",
    "templates/pr-control-plane/",
)
def _strip_reference_prefixes(raw_ref: str) -> str:
    normalized = raw_ref.strip().replace("\\", "/")
    if normalized.startswith(RETIRED_REF_PREFIX):
        normalized = normalized[len(RETIRED_REF_PREFIX) :]
    if normalized.startswith(VENDORED_GOVERNANCE_PREFIX):
        normalized = normalized[len(VENDORED_GOVERNANCE_PREFIX) :]
    return normalized
def _iter_string_values(value: Any) -> List[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, dict):
        strings: List[str] = []
        for item in value.values():
            strings.extend(_iter_string_values(item))
        return strings
    if isinstance(value, list):
        strings = []
        for item in value:
            strings.extend(_iter_string_values(item))
        return strings
    return []
def _unprefixed_retired_references(value: str) -> List[str]:
    matches: List[str] = []
    normalized = value.replace("\\", "/")
    for pattern in RETIRED_REFERENCE_PATTERNS:
        start = 0
        while True:
            index = normalized.find(pattern, start)
            if index == -1:
                break
            prefix_start = index - len(RETIRED_REF_PREFIX)
            if prefix_start < 0 or normalized[prefix_start:index] != RETIRED_REF_PREFIX:
                matches.append(pattern)
                break
            start = index + len(pattern)
    return matches
def _reference_target_exists(repo_root: Path, raw_ref: str) -> bool:
    if raw_ref.strip().replace("\\", "/").startswith(RETIRED_REF_PREFIX):
        return True
    normalized = _strip_reference_prefixes(raw_ref)
    if not normalized:
        return True
    if "://" in normalized:
        return True
    target = normalized.split("#", 1)[0].split("?", 1)[0]
    if not target:
        return True
    if target.startswith("/"):
        return False
    if any(part in {"", ".", ".."} for part in target.split("/")):
        return False
    return (repo_root / target).exists()
def _record_is_governance_scoped(record: Dict[str, Any]) -> bool:
    owners = record.get("ssot_owner_paths")
    if not isinstance(owners, list):
        return False
    for owner in owners:
        if not isinstance(owner, str):
            continue
        normalized = _strip_reference_prefixes(owner)
        if normalized.startswith(GOVERNANCE_OWNER_PREFIXES):
            return True
    return False
def _check_governance_specific_record_fields(
    path: Path, record: Dict[str, Any], repo_root: Path, errors: List[str]
) -> bool:
    record_has_errors = False
    change_type = record.get("change_type")
    if not isinstance(change_type, str) or change_type.strip().lower() != "docs":
        return record_has_errors
    if not _record_is_governance_scoped(record):
        return record_has_errors
    for value in _iter_string_values(record):
        for pattern in _unprefixed_retired_references(value):
            errors.append(
                f"Governance docs change record contains unprefixed retired reference "
                f"'{pattern}' in {path}. Prefix historical references with '{RETIRED_REF_PREFIX}'."
            )
            record_has_errors = True
    council = record.get("council_summary")
    if not isinstance(council, dict):
        errors.append(f"Governance docs change record missing object field 'council_summary' in {path}.")
        return True
    missing_full_fields = [
        field for field in COUNCIL_FULL_REQUIRED_FIELDS if not is_non_empty(council.get(field))
    ]
    missing_abbreviated_fields = [
        field
        for field in COUNCIL_ABBREVIATED_REQUIRED_FIELDS
        if not is_non_empty(council.get(field))
    ]
    has_full_only_keys = any(field in council for field in COUNCIL_FULL_ONLY_FIELDS)
    council_mode = "full"
    if missing_full_fields:
        if has_full_only_keys:
            for field in missing_full_fields:
                errors.append(f"Governance docs council_summary missing or empty '{field}' in {path}.")
            errors.append(
                "Governance docs council_summary includes full-summary fields and must satisfy "
                f"the full required set {list(COUNCIL_FULL_REQUIRED_FIELDS)} in {path}."
            )
            record_has_errors = True
        elif missing_abbreviated_fields:
            for field in missing_abbreviated_fields:
                errors.append(f"Governance docs council_summary missing or empty '{field}' in {path}.")
            errors.append(
                "Governance docs council_summary must provide either the full summary fields "
                f"{list(COUNCIL_FULL_REQUIRED_FIELDS)} or the abbreviated fields "
                f"{list(COUNCIL_ABBREVIATED_REQUIRED_FIELDS)} in {path}."
            )
            record_has_errors = True
        else:
            council_mode = "abbreviated"
    if council_mode == "full":
        reviewers = council.get("reviewers")
        if not isinstance(reviewers, list) or not as_non_empty_list(reviewers):
            errors.append(f"Governance docs council_summary.reviewers must be a non-empty array in {path}.")
            record_has_errors = True
    findings = council.get("findings")
    findings_valid = isinstance(findings, list) and bool(as_non_empty_list(findings))
    if council_mode == "full":
        if not findings_valid:
            errors.append(f"Governance docs council_summary.findings must be a non-empty array in {path}.")
            record_has_errors = True
    else:
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
    intent_coverage = council.get("intent_coverage")
    intent_values = intent_coverage if isinstance(intent_coverage, list) else None
    if not intent_values or not as_non_empty_list(intent_values):
        errors.append(f"Governance docs council_summary.intent_coverage must be a non-empty array in {path}.")
        record_has_errors = True
    else:
        normalized_intents: List[str] = []
        for item in intent_values:
            if not isinstance(item, str) or not item.strip():
                errors.append(
                    f"Governance docs council_summary.intent_coverage must contain only non-empty strings in {path}."
                )
                record_has_errors = True
                continue
            normalized_intents.append(item.strip())
        if normalized_intents:
            for required_intent in sorted(COUNCIL_INTENT_REQUIRED):
                if required_intent not in normalized_intents:
                    errors.append(
                        f"Governance docs council_summary.intent_coverage missing '{required_intent}' in {path}."
                    )
                    record_has_errors = True
    phase = council.get("phase")
    phase_normalized = phase.strip().lower() if isinstance(phase, str) else phase
    if is_non_empty(phase) and phase_normalized not in COUNCIL_PHASE_ALLOWED:
        errors.append(
            f"Governance docs council_summary.phase must be one of {sorted(COUNCIL_PHASE_ALLOWED)} in {path}."
        )
        record_has_errors = True
    go_no_go = council.get("go_no_go")
    go_no_go_normalized = go_no_go.strip().lower() if isinstance(go_no_go, str) else go_no_go
    if is_non_empty(go_no_go) and go_no_go_normalized not in COUNCIL_GO_NO_GO_ALLOWED:
        errors.append(
            f"Governance docs council_summary.go_no_go must be one of {sorted(COUNCIL_GO_NO_GO_ALLOWED)} in {path}."
        )
        record_has_errors = True
    validation_context = record.get("validation_context")
    if not isinstance(validation_context, dict):
        errors.append(f"Governance docs change record missing object field 'validation_context' in {path}.")
        return True
    for field in ("intended_environment", "evidence_plan", "release_gate_decision"):
        if not is_non_empty(validation_context.get(field)):
            errors.append(f"Governance docs validation_context missing or empty '{field}' in {path}.")
            record_has_errors = True
    traceability_refs = validation_context.get("traceability_refs")
    if not isinstance(traceability_refs, list) or not as_non_empty_list(traceability_refs):
        errors.append(
            f"Governance docs validation_context.traceability_refs must be a non-empty array in {path}."
        )
        record_has_errors = True
    else:
        valid_traceability_refs = 0
        for item in traceability_refs:
            if not isinstance(item, str) or not item.strip():
                errors.append(
                    f"Governance docs validation_context.traceability_refs must contain only non-empty strings in {path}."
                )
                record_has_errors = True
                continue
            if not _reference_target_exists(repo_root, item):
                errors.append(
                    f"Governance docs validation_context.traceability_refs contains missing active reference "
                    f"'{item}' in {path}. Prefix retired historical references with '{RETIRED_REF_PREFIX}'."
                )
                record_has_errors = True
                continue
            valid_traceability_refs += 1
        if valid_traceability_refs == 0:
            errors.append(
                f"Governance docs validation_context.traceability_refs must be a non-empty array in {path}."
            )
            record_has_errors = True
    return record_has_errors
def check_change_records(
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
        schema = load_json(schema_path)
    except RuntimeError as exc:
        return [str(exc)], notes
    allowed_change_types = schema.get("properties", {}).get("change_type", {}).get("enum", [])
    if not isinstance(allowed_change_types, list) or not allowed_change_types:
        return [f"Schema missing properties.change_type.enum in: {schema_path}"], notes
    base_required = schema.get("required", [])
    if not isinstance(base_required, list) or not base_required:
        return [f"Schema missing required field list in: {schema_path}"], notes
    valid_records = 0
    for record_file in record_files:
        try:
            record = load_json(record_file)
        except RuntimeError as exc:
            errors.append(str(exc))
            continue
        if not isinstance(record, dict):
            errors.append(f"Parsed record is not an object in {record_file}.")
            continue
        record_has_errors = False
        for field in base_required:
            if not is_non_empty(record.get(field)):
                errors.append(f"Missing or empty required field '{field}' in {record_file}.")
                record_has_errors = True
        change_type = record.get("change_type")
        normalized_change_type = change_type.strip().lower() if isinstance(change_type, str) else change_type
        if is_non_empty(change_type) and normalized_change_type not in allowed_change_types:
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
                    errors.append(f"{field_name}[{idx}] must be a non-empty string in {record_file}.")
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
                for required_field in WITNESS_REQUIRED_FIELDS:
                    if not is_non_empty(witness.get(required_field)):
                        errors.append(
                            f"witnesses[{idx}] missing or empty '{required_field}' in {record_file}."
                        )
                        record_has_errors = True
        if normalized_change_type in {"bugfix", "regression"}:
            for field in BUGFIX_REQUIRED_FIELDS:
                if not is_non_empty(record.get(field)):
                    errors.append(f"Bugfix/regression record missing or empty '{field}' in {record_file}.")
                    record_has_errors = True
            mre = record.get("mre")
            if not isinstance(mre, dict):
                errors.append(f"mre must be an object in {record_file}.")
                record_has_errors = True
            else:
                for field in MRE_REQUIRED_FIELDS:
                    if not is_non_empty(mre.get(field)):
                        errors.append(f"mre missing or empty '{field}' in {record_file}.")
                        record_has_errors = True
            tests = record.get("tests")
            if not isinstance(tests, dict):
                errors.append(f"tests must be an object in {record_file}.")
                record_has_errors = True
            else:
                for field in TESTS_REQUIRED_FIELDS:
                    if not is_non_empty(tests.get(field)):
                        errors.append(f"tests missing or empty '{field}' in {record_file}.")
                        record_has_errors = True
        if _check_governance_specific_record_fields(record_file, record, repo_root, errors):
            record_has_errors = True
        if not record_has_errors:
            valid_records += 1
    if not errors:
        notes.append(f"Change record checks passed. Valid records: {valid_records}")
    return errors, notes
