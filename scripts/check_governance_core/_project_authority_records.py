from __future__ import annotations

import re
from typing import Dict, List, Tuple


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


def _section_text(text: str, heading: str) -> str:
    match = re.search(rf"^##\s+{re.escape(heading)}\s*$([\s\S]*?)(?=^##\s+|\Z)", text, flags=re.MULTILINE)
    if match is None:
        return ""
    return match.group(1).strip()


def _section_payload(section: str) -> str:
    fence_match = re.search(r"```(?:text|md|markdown)?\s*\n([\s\S]*?)\n```", section, flags=re.IGNORECASE)
    value = fence_match.group(1) if fence_match else section
    lines = []
    for line in value.splitlines():
        stripped = line.strip()
        if stripped:
            lines.append(re.sub(r"^[-*]\s+", "", stripped))
    return "\n".join(lines).strip().strip("`").strip()


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


def _is_missing_active_payload(section: str) -> bool:
    normalized = _section_payload(section).lower()
    return (
        not normalized
        or normalized in {"todo", "tbd", "fixme", "..."}
        or "n/a - no active work" in normalized
        or (normalized.startswith("<") and normalized.endswith(">"))
    )


def _is_missing_active_field_value(value: str | None) -> bool:
    if value is None:
        return True
    normalized = value.strip().lower()
    return (
        not normalized
        or normalized in {"todo", "tbd", "fixme", "..."}
        or "n/a - no active work" in normalized
        or (normalized.startswith("<") and normalized.endswith(">"))
    )


def _is_generic_ready_evidence(value: str) -> bool:
    normalized = re.sub(r"[\s.]+", " ", value.strip().lower()).strip()
    return normalized in {"complete", "completed", "verified", "passed", "done", "ok", "yes", "fulfilled"}


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
        if not status_values and "Status" not in required_fields:
            errors.append(f"{rel_path} record {record_id} missing required field: Status")
        for status in status_values:
            if status not in allowed_statuses:
                errors.append(f"{rel_path} record {record_id} has invalid status: {status}")
        if duplicate_key_fields:
            key = _normalized_record_key(block, duplicate_key_fields)
            previous_id = seen_structural_keys.get(key)
            if all(key) and previous_id is not None:
                errors.append(
                    f"{rel_path} records {previous_id} and {record_id} duplicate structural authority key: "
                    f"{', '.join(duplicate_key_fields)}"
                )
            elif all(key):
                seen_structural_keys[key] = record_id
        if allowed_field_values:
            for field, allowed_values in allowed_field_values.items():
                for value in _field_values(block, field):
                    if value not in allowed_values:
                        errors.append(f"{rel_path} record {record_id} has invalid {field}: {value}")
