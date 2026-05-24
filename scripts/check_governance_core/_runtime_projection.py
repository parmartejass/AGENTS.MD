from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Sequence, Set, Tuple

try:
    from ._shared import load_json, load_toml
except ImportError:  # pragma: no cover - script-path execution
    from _shared import load_json, load_toml

RUNTIME_PROJECTION_REQUIRED_SUPPORT_LEVELS = {
    "official",
    "compatibility",
    "manual",
    "unsupported",
    "reserved",
}
RUNTIME_PROJECTION_ALLOWED_SCOPES = {"project", "user", "system"}
RUNTIME_PROJECTION_ALLOWED_MODES_BY_ASSET_CLASS = {
    "skills": {
        "child_directory_links",
        "generated_cursor_rules_from_skills",
        "generated_claude_commands_from_skills",
        "skip",
    },
    "mcp": {"mcp_file_link", "skip"},
    "settings": {"settings_file_link", "skip"},
    "acp": {"skip"},
}
ENTRY_OPTIONAL_BOOLEAN_FIELDS = {
    "preserve_existing_when_disabled",
    "preserve_existing_non_link",
}


def resolve_runtime_projection_source(path_spec: str, governance_root: Path) -> Path:
    expanded = path_spec.replace("{HOME}", str(Path.home()))
    path = Path(expanded).expanduser()
    if path.is_absolute():
        return path
    return (governance_root / path).resolve()


def _require_top_level_fields(manifest: Dict[str, object], manifest_path: Path) -> List[str]:
    errors: List[str] = []
    for field in (
        "version",
        "ssot_owner",
        "update_trigger",
        "support_levels",
        "path_resolution",
        "asset_classes",
    ):
        if field not in manifest:
            errors.append(
                f"Runtime projection manifest missing top-level field '{field}': {manifest_path}"
            )
    return errors


def _validate_support_levels(manifest: Dict[str, object]) -> List[str]:
    errors: List[str] = []
    support_levels = manifest.get("support_levels")
    if not isinstance(support_levels, list) or not support_levels:
        errors.append("runtime-projections.json support_levels must be a non-empty array.")
        return errors

    normalized = [item for item in support_levels if isinstance(item, str) and item.strip()]
    if len(normalized) != len(support_levels):
        errors.append("runtime-projections.json support_levels must contain only non-empty strings.")
    if len(set(normalized)) != len(normalized):
        errors.append("runtime-projections.json support_levels contains duplicates.")
    missing = RUNTIME_PROJECTION_REQUIRED_SUPPORT_LEVELS.difference(normalized)
    if missing:
        errors.append(
            "runtime-projections.json support_levels is missing required values: "
            + ", ".join(sorted(missing))
        )
    return errors


def _validate_path_resolution(manifest: Dict[str, object]) -> List[str]:
    errors: List[str] = []
    path_resolution = manifest.get("path_resolution")
    if not isinstance(path_resolution, dict):
        errors.append("runtime-projections.json path_resolution must be an object.")
        return errors

    for field in ("source_root", "source_path", "source_preference", "target_root", "target_path"):
        value = path_resolution.get(field)
        if not isinstance(value, str) or not value.strip():
            errors.append(
                f"runtime-projections.json path_resolution.{field} must be a non-empty string."
            )
    return errors


def _validate_source_preference(
    entry_id: str, source_preference: Sequence[object], governance_root: Path
) -> List[str]:
    errors: List[str] = []
    if not isinstance(source_preference, list) or not source_preference:
        return [
            f"runtime-projections.json entry '{entry_id}' requires non-empty source_preference."
        ]

    resolved_candidates = [
        resolve_runtime_projection_source(candidate, governance_root)
        for candidate in source_preference
        if isinstance(candidate, str) and candidate.strip()
    ]
    if len(resolved_candidates) != len(source_preference):
        errors.append(
            f"runtime-projections.json entry '{entry_id}' source_preference must contain only non-empty strings."
        )
    elif not any(candidate.is_file() for candidate in resolved_candidates):
        errors.append(
            f"runtime-projections.json entry '{entry_id}' source_preference does not resolve to an existing file."
        )
    return errors


def _validate_settings_source(
    entry_id: str, source_path: object, governance_root: Path
) -> Tuple[List[str], List[str]]:
    errors: List[str] = []
    notes: List[str] = []
    if not isinstance(source_path, str) or not source_path.strip():
        return [f"runtime-projections.json entry '{entry_id}' requires non-empty source_path."], notes

    resolved_source_path = resolve_runtime_projection_source(source_path, governance_root)
    if not resolved_source_path.is_file():
        return [
            f"runtime-projections.json entry '{entry_id}' source_path does not exist: {resolved_source_path}"
        ], notes

    suffix = resolved_source_path.suffix.lower()
    try:
        if suffix == ".json":
            load_json(resolved_source_path)
        elif suffix == ".toml":
            load_toml(resolved_source_path)
        else:
            errors.append(
                f"runtime-projections.json entry '{entry_id}' uses unsupported settings file extension '{suffix}'."
            )
    except RuntimeError as exc:
        errors.append(str(exc))
    return errors, notes


def _validate_optional_boolean_fields(entry_id: str, entry: Dict[str, object]) -> List[str]:
    errors: List[str] = []
    for field in ENTRY_OPTIONAL_BOOLEAN_FIELDS:
        if field in entry and not isinstance(entry[field], bool):
            errors.append(f"runtime-projections.json entry '{entry_id}' {field} must be a boolean.")
    return errors


def _validate_entry(
    asset_class: str,
    idx: int,
    entry: object,
    allowed_modes: Set[str],
    governance_root: Path,
    seen_ids: Set[str],
) -> Tuple[List[str], List[str]]:
    errors: List[str] = []
    notes: List[str] = []
    if not isinstance(entry, dict):
        return [
            f"runtime-projections.json asset_classes.{asset_class}[{idx}] must be an object."
        ], notes

    missing_fields = [
        field
        for field in ("id", "platform", "support_level", "projection_mode", "scope", "default_enabled")
        if field not in entry
    ]
    if missing_fields:
        for field in missing_fields:
            errors.append(
                f"runtime-projections.json asset_classes.{asset_class}[{idx}] missing field '{field}'."
            )
        return errors, notes

    entry_id = entry.get("id")
    if not isinstance(entry_id, str) or not entry_id.strip():
        return [
            f"runtime-projections.json asset_classes.{asset_class}[{idx}].id must be a non-empty string."
        ], notes
    if entry_id in seen_ids:
        errors.append(f"runtime-projections.json contains duplicate projection id '{entry_id}'.")
    else:
        seen_ids.add(entry_id)

    errors.extend(_validate_optional_boolean_fields(entry_id, entry))

    support_level = entry.get("support_level")
    if support_level not in RUNTIME_PROJECTION_REQUIRED_SUPPORT_LEVELS:
        errors.append(
            f"runtime-projections.json entry '{entry_id}' uses unsupported support_level '{support_level}'."
        )

    scope = entry.get("scope")
    if scope not in RUNTIME_PROJECTION_ALLOWED_SCOPES:
        errors.append(
            f"runtime-projections.json entry '{entry_id}' uses unsupported scope '{scope}'."
        )

    default_enabled = entry.get("default_enabled")
    if not isinstance(default_enabled, bool):
        errors.append(
            f"runtime-projections.json entry '{entry_id}' default_enabled must be a boolean."
        )

    projection_mode = entry.get("projection_mode")
    if projection_mode not in allowed_modes:
        errors.append(
            f"runtime-projections.json entry '{entry_id}' uses unsupported projection_mode "
            f"'{projection_mode}' for asset class '{asset_class}'."
        )
        return errors, notes

    if projection_mode in {
        "child_directory_links",
        "generated_cursor_rules_from_skills",
        "generated_claude_commands_from_skills",
    }:
        source_root = entry.get("source_root")
        target_root = entry.get("target_root")
        if not isinstance(source_root, str) or not source_root.strip():
            errors.append(f"runtime-projections.json entry '{entry_id}' requires non-empty source_root.")
        else:
            resolved_source_root = resolve_runtime_projection_source(source_root, governance_root)
            if not resolved_source_root.is_dir():
                errors.append(
                    f"runtime-projections.json entry '{entry_id}' source_root does not exist: {resolved_source_root}"
                )
        if not isinstance(target_root, str) or not target_root.strip():
            errors.append(f"runtime-projections.json entry '{entry_id}' requires non-empty target_root.")

    if projection_mode == "mcp_file_link":
        errors.extend(_validate_source_preference(entry_id, entry.get("source_preference"), governance_root))
        target_path = entry.get("target_path")
        if not isinstance(target_path, str) or not target_path.strip():
            errors.append(f"runtime-projections.json entry '{entry_id}' requires non-empty target_path.")

    if projection_mode == "settings_file_link":
        settings_errors, settings_notes = _validate_settings_source(
            entry_id, entry.get("source_path"), governance_root
        )
        errors.extend(settings_errors)
        notes.extend(settings_notes)
        target_path = entry.get("target_path")
        if not isinstance(target_path, str) or not target_path.strip():
            errors.append(f"runtime-projections.json entry '{entry_id}' requires non-empty target_path.")

    if projection_mode == "skip":
        reason = entry.get("reason")
        if not isinstance(reason, str) or not reason.strip():
            errors.append(
                f"runtime-projections.json entry '{entry_id}' with projection_mode 'skip' requires a non-empty reason."
            )

    if support_level in {"compatibility", "manual", "unsupported", "reserved"} and default_enabled:
        errors.append(
            f"runtime-projections.json entry '{entry_id}' must not enable non-official projections by default."
        )

    return errors, notes


def check_runtime_projection_manifest(
    repo_root: Path, governance_root: Path
) -> Tuple[List[str], List[str]]:
    del repo_root
    errors: List[str] = []
    notes: List[str] = []

    manifest_path = governance_root / "docs/agents/platforms/runtime-projections.json"
    if not manifest_path.is_file():
        return [f"Missing runtime projection manifest: {manifest_path}"], notes

    try:
        manifest = load_json(manifest_path)
    except RuntimeError as exc:
        return [str(exc)], notes

    if not isinstance(manifest, dict):
        return [f"Runtime projection manifest must be a JSON object: {manifest_path}"], notes

    errors.extend(_require_top_level_fields(manifest, manifest_path))
    if errors:
        return errors, notes

    if manifest.get("ssot_owner") != "docs/agents/platforms/runtime-projections.json":
        errors.append(
            "Runtime projection manifest ssot_owner must be "
            "'docs/agents/platforms/runtime-projections.json'."
        )

    errors.extend(_validate_support_levels(manifest))
    errors.extend(_validate_path_resolution(manifest))

    asset_classes = manifest.get("asset_classes")
    if not isinstance(asset_classes, dict):
        errors.append("runtime-projections.json asset_classes must be an object.")
        return errors, notes

    seen_ids: Set[str] = set()
    for asset_class, allowed_modes in RUNTIME_PROJECTION_ALLOWED_MODES_BY_ASSET_CLASS.items():
        entries = asset_classes.get(asset_class)
        if not isinstance(entries, list):
            errors.append(f"runtime-projections.json asset_classes.{asset_class} must be an array.")
            continue
        for idx, entry in enumerate(entries, start=1):
            entry_errors, entry_notes = _validate_entry(
                asset_class, idx, entry, allowed_modes, governance_root, seen_ids
            )
            errors.extend(entry_errors)
            notes.extend(entry_notes)

    if not errors:
        notes.append(f"Runtime projection manifest checks passed: {manifest_path}")
    return errors, notes
