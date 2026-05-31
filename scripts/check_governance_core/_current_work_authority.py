from __future__ import annotations

import re
import subprocess
from pathlib import Path
from typing import List

try:
    from ._project_authority_records import _record_blocks
    from ._project_authority_records import (
        _field_value,
        _is_generic_ready_evidence,
        _is_missing_active_field_value,
        _is_missing_active_payload,
        _is_placeholder_value,
        _section_text,
        _validate_contains_fields,
    )
    from ._shared import GIT_LS_FILES_TIMEOUT_SEC
except ImportError:  # pragma: no cover - script-path execution
    from _project_authority_records import _record_blocks
    from _project_authority_records import (
        _field_value,
        _is_generic_ready_evidence,
        _is_missing_active_field_value,
        _is_missing_active_payload,
        _is_placeholder_value,
        _section_text,
        _validate_contains_fields,
    )
    from _shared import GIT_LS_FILES_TIMEOUT_SEC


PROMPT_SECTION_MAX_CHARS = 4000
PROMPT_SAFETY_DECISIONS = {"reviewed-safe", "redacted-substitute"}
PLAN_OPEN_STATUSES = {"planned", "in_progress"}
PLAN_ALLOWED_STATUSES = PLAN_OPEN_STATUSES | {"completed", "skipped", "deferred", "rejected"}
SENSITIVE_PROMPT_PATTERNS = (
    re.compile(r"(?i)\b(api[_-]?key|secret|token|password|credential)\b\s*[:=]"),
    re.compile(r"(?i)\b(bearer|basic)\s+[a-z0-9._~+/=-]{16,}"),
    re.compile(r"(?i)-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    re.compile(r"\b(ghp|github_pat|sk|xox[baprs]|AKIA)[A-Za-z0-9_/-]{12,}\b"),
)
COMMIT_STATE_PATTERN = re.compile(
    r"^(uncommitted|committed:[0-9a-f]{7,40}|pushed:[^\s].+|PR:https?://\S+|not-required \+ reason:.+)$"
)
ACTIVE_STATUSES = {"active", "paused", "blocked", "ready-to-clear"}
ALLOWED_STATUSES = ACTIVE_STATUSES | {"no-active-work"}


def validate_current_work_doc(repo_root: Path) -> List[str]:
    current_work = repo_root / "docs/project/goal/current-work.md"
    if not current_work.is_file():
        return []
    rel = current_work.relative_to(repo_root).as_posix()
    text = current_work.read_text(encoding="utf-8")
    errors: List[str] = []

    _validate_current_work_shape(errors, rel, text)
    work_item_id = _work_item_id(text)
    status = _validate_status(errors, rel, text)
    sections = _current_work_sections(text)

    prompt_text = sections["User Prompt"]
    if len(prompt_text) > PROMPT_SECTION_MAX_CHARS:
        errors.append(f"{rel} User Prompt section must stay under {PROMPT_SECTION_MAX_CHARS} characters.")
    if any(pattern.search(prompt_text) for pattern in SENSITIVE_PROMPT_PATTERNS):
        errors.append(f"{rel} User Prompt section contains an unsafe secret-like pattern; use a redacted substitute.")

    if status == "no-active-work":
        _validate_no_active_work(errors, rel, sections)
    elif status in ACTIVE_STATUSES:
        _validate_active_work(errors, repo_root, rel, status, work_item_id, sections)
    return errors


def _work_item_id(text: str) -> str:
    match = re.search(r"Work item ID:\s*`?(CW-[0-9]{8}-[0-9]{3})`?", text)
    return match.group(1) if match else ""


def _validate_current_work_shape(errors: List[str], rel: str, text: str) -> None:
    _validate_contains_fields(
        errors,
        rel,
        text,
        [
            "Status:",
            "Work item ID:",
            "Last updated:",
            "## User Prompt",
            "## Prompt Safety",
            "## Goal Statement",
            "## Status",
            "## Goal Alignment",
            "## Blockers",
            "## Boundaries",
            "## Derived Plan",
            "## Implementation Records",
            "## Reconciliation",
            "## Supersession",
            "## SSOT Layers",
            "## Review Confirmation",
            "## Closure Handoff",
            "## Next safe action",
            "## Clear Rule",
        ],
    )
    if not re.search(r"Work item ID:\s*`?(CW-[0-9]{8}-[0-9]{3})`?", text):
        errors.append(f"{rel} must contain a CW-YYYYMMDD-NNN Work item ID.")
    if not re.search(r"Last updated:\s*`?[0-9]{4}-[0-9]{2}-[0-9]{2}`?", text):
        errors.append(f"{rel} must contain a Last updated value in YYYY-MM-DD format.")


def _validate_status(errors: List[str], rel: str, text: str) -> str:
    status_values = re.findall(r"^Status:\s*`?([^`\n]+)`?\s*$", text, flags=re.MULTILINE)
    status = ""
    if status_values:
        if len(status_values) > 1:
            errors.append(f"{rel} contains duplicate Status fields.")
        for status_value in status_values:
            status = status_value.strip()
            if status not in ALLOWED_STATUSES:
                errors.append(f"{rel} has invalid Status: {status}")
    else:
        errors.append(f"{rel} must contain a Status value.")
    return status


def _current_work_sections(text: str) -> dict[str, str]:
    headings = (
        "User Prompt",
        "Prompt Safety",
        "Goal Statement",
        "Derived Plan",
        "Implementation Records",
        "Reconciliation",
        "SSOT Layers",
        "Review Confirmation",
        "Closure Handoff",
    )
    return {heading: _section_text(text, heading) for heading in headings}


def _validate_no_active_work(errors: List[str], rel: str, sections: dict[str, str]) -> None:
    for heading, section in sections.items():
        if "N/A - no active work" not in section:
            errors.append(f"{rel} {heading} section must reset to 'N/A - no active work' when Status is no-active-work.")
    no_active_residue = "\n".join(sections.values())
    if re.search(r"\b(DP-[0-9]{8}-[0-9]{3}|reviewed-safe|uncommitted|committed:|pushed:|PR:https?://)", no_active_residue):
        errors.append(f"{rel} no-active-work sections must not retain active prompt, plan, review, or closure residue.")


def _validate_active_work(
    errors: List[str], repo_root: Path, rel: str, status: str, work_item_id: str, sections: dict[str, str]
) -> None:
    for heading in ("User Prompt", "Goal Statement"):
        if _is_missing_active_payload(sections[heading]):
            errors.append(f"{rel} {heading} section must contain active work content when Status is {status}.")

    _validate_prompt_safety(errors, rel, status, sections["Prompt Safety"])
    plan_statuses = _validate_derived_plan(errors, rel, sections["Derived Plan"])
    _validate_named_fields(errors, rel, "Implementation Records", sections["Implementation Records"], ("Owner docs updated", "Changelog witness", "Change records"))
    _validate_named_fields(errors, rel, "Reconciliation", sections["Reconciliation"], ("Stale/rejected prompts", "Stale/rejected plans", "Unused artifacts"))
    _validate_truth_layers(errors, rel, status, sections["SSOT Layers"])
    _validate_review_confirmation(errors, rel, status, sections["Review Confirmation"])
    commit_state = _validate_closure_handoff(errors, rel, sections["Closure Handoff"])
    if status == "ready-to-clear":
        _validate_ready_to_clear(errors, repo_root, rel, work_item_id, plan_statuses, commit_state, sections)


def _validate_prompt_safety(errors: List[str], rel: str, status: str, section: str) -> None:
    storage_decision = _field_value(section, "Storage decision") or ""
    if storage_decision not in PROMPT_SAFETY_DECISIONS:
        errors.append(f"{rel} Prompt Safety Storage decision must be one of: {', '.join(sorted(PROMPT_SAFETY_DECISIONS))}.")
    if _is_missing_active_field_value(_field_value(section, "Evidence")):
        errors.append(f"{rel} Prompt Safety section must contain a non-placeholder Evidence value when Status is {status}.")
    if _is_missing_active_field_value(_field_value(section, "Prompt equality witness")):
        errors.append(f"{rel} Prompt Safety section must contain a non-placeholder Prompt equality witness when Status is {status}.")


def _validate_derived_plan(errors: List[str], rel: str, section: str) -> list[str]:
    plan_statuses = re.findall(r"\[([a-z_]+)\]", section)
    if not plan_statuses or "DP-" not in section:
        errors.append(f"{rel} Derived Plan section must contain at least one DP-* plan item with a status.")
    for plan_status in plan_statuses:
        if plan_status not in PLAN_ALLOWED_STATUSES:
            errors.append(f"{rel} Derived Plan contains invalid plan item status: {plan_status}")
    for required_term in ("prompt", "goal", "SSOT", "witness"):
        if required_term not in section:
            errors.append(f"{rel} Derived Plan section must reference {required_term}.")
    return plan_statuses


def _validate_named_fields(errors: List[str], rel: str, section_name: str, section: str, fields: tuple[str, ...]) -> None:
    for field in fields:
        if field not in section:
            errors.append(f"{rel} {section_name} section must include {field}.")


def _validate_truth_layers(errors: List[str], rel: str, status: str, section: str) -> None:
    for truth_layer in ("Runtime truth", "Semantic truth", "Recorded truth"):
        if truth_layer not in section:
            errors.append(f"{rel} SSOT Layers section must include {truth_layer}.")
        elif _is_missing_active_field_value(_field_value(section, truth_layer)):
            errors.append(f"{rel} SSOT Layers section must contain a non-placeholder value for {truth_layer} when Status is {status}.")


def _validate_review_confirmation(errors: List[str], rel: str, status: str, section: str) -> None:
    for review_field in ("Pre-change review:", "Post-change review:", "Fulfillment:"):
        if review_field not in section:
            errors.append(f"{rel} Review Confirmation section must include {review_field}")
        elif _is_missing_active_field_value(_field_value(section, review_field.rstrip(":"))):
            errors.append(f"{rel} Review Confirmation section must contain a non-placeholder value for {review_field.rstrip(':')} when Status is {status}.")


def _validate_closure_handoff(errors: List[str], rel: str, section: str) -> str:
    _validate_named_fields(errors, rel, "Closure Handoff", section, ("Changelog witness", "Commit/push state", "Tracked artifact witness"))
    commit_state = _field_value(section, "Commit/push state") or ""
    if commit_state and not COMMIT_STATE_PATTERN.match(commit_state):
        errors.append(
            f"{rel} Closure Handoff Commit/push state must be one of "
            "uncommitted, committed:<sha>, pushed:<remote/ref>, PR:<url>, or not-required + reason:<reason>."
        )
    return commit_state


def _validate_ready_to_clear(
    errors: List[str],
    repo_root: Path,
    rel: str,
    work_item_id: str,
    plan_statuses: list[str],
    commit_state: str,
    sections: dict[str, str],
) -> None:
    combined = "\n".join(sections[name] for name in ("Derived Plan", "Implementation Records", "Reconciliation", "SSOT Layers", "Review Confirmation", "Closure Handoff"))
    if re.search(r"\bpending\b", combined, flags=re.IGNORECASE):
        errors.append(f"{rel} ready-to-clear status cannot contain pending SSOT layer or review confirmation values.")
    if any(plan_status in PLAN_OPEN_STATUSES for plan_status in plan_statuses):
        errors.append(f"{rel} ready-to-clear Derived Plan cannot contain planned or in_progress items.")
    if commit_state == "uncommitted":
        errors.append(f"{rel} ready-to-clear Closure Handoff cannot remain uncommitted.")
    for field, section_name in {
        "Runtime truth": "SSOT Layers",
        "Semantic truth": "SSOT Layers",
        "Recorded truth": "SSOT Layers",
        "Pre-change review": "Review Confirmation",
        "Post-change review": "Review Confirmation",
        "Fulfillment": "Review Confirmation",
        "Owner docs updated": "Implementation Records",
        "Changelog witness": "Closure Handoff",
        "Change records": "Implementation Records",
        "Stale/rejected prompts": "Reconciliation",
        "Stale/rejected plans": "Reconciliation",
        "Unused artifacts": "Reconciliation",
        "Tracked artifact witness": "Closure Handoff",
    }.items():
        value = _field_value(sections[section_name], field) or ""
        if not value or _is_placeholder_value(value) or value == "N/A" or _is_generic_ready_evidence(value):
            errors.append(f"{rel} ready-to-clear status requires concrete evidence for {field}.")
    fulfillment = _field_value(sections["Review Confirmation"], "Fulfillment") or ""
    if not re.search(r"\bprompt\b", fulfillment, flags=re.IGNORECASE) or not re.search(r"\b(goal|work-item)\b", fulfillment, flags=re.IGNORECASE):
        errors.append(f"{rel} ready-to-clear Fulfillment must reference the recorded prompt and work-item goal.")
    _validate_changelog_witness(errors, repo_root, rel, work_item_id, sections["Closure Handoff"])
    _validate_git_status_witness(errors, repo_root, rel, sections["Closure Handoff"])


def _validate_changelog_witness(errors: List[str], repo_root: Path, rel: str, work_item_id: str, section: str) -> None:
    witness = _field_value(section, "Changelog witness") or ""
    if witness.startswith("not-required + reason:"):
        return
    match = re.search(r"\b(CH-[0-9]{8}-[0-9]{3})\b", witness)
    if not match:
        errors.append(f"{rel} ready-to-clear Changelog witness must reference CH-YYYYMMDD-NNN or not-required + reason:<reason>.")
        return
    changelog = repo_root / "docs/project/learning/changelog.md"
    if not changelog.is_file():
        errors.append(f"{rel} ready-to-clear Changelog witness references {match.group(1)} but changelog.md is missing.")
        return
    for block in _record_blocks(changelog.read_text(encoding="utf-8"), "CH"):
        if re.match(rf"^###\s+{re.escape(match.group(1))}\b", block):
            current_work = _field_value(block, "Current work") or ""
            if work_item_id and work_item_id not in current_work:
                errors.append(f"{rel} Changelog witness {match.group(1)} must reference current work {work_item_id}.")
            return
    errors.append(f"{rel} ready-to-clear Changelog witness references missing entry: {match.group(1)}.")


def _validate_git_status_witness(errors: List[str], repo_root: Path, rel: str, section: str) -> None:
    if not (repo_root / ".git").exists():
        return
    witness = _field_value(section, "Tracked artifact witness") or ""
    try:
        result = subprocess.run(
            ["git", "-C", str(repo_root), "status", "--short"],
            check=True,
            capture_output=True,
            text=True,
            timeout=GIT_LS_FILES_TIMEOUT_SEC,
        )
    except (FileNotFoundError, subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
        errors.append(f"{rel} could not verify git status for Tracked artifact witness: {exc}")
        return
    actual = (result.stdout or "").strip()
    if actual:
        errors.append(f"{rel} ready-to-clear requires clean git status; current git status is not clean.")
    elif "git status --short: clean" not in witness:
        errors.append(f"{rel} Tracked artifact witness must record `git status --short: clean`.")
