from __future__ import annotations

import json
import re
from pathlib import Path, PurePosixPath
from typing import Any, Mapping

from scripts.check_governance_core._documents import DocumentStore, resolve_declared_file
from scripts.check_governance_core._inventory import RepositoryInventory


class ManifestSyntaxError(ValueError):
    pass


_KEY = re.compile(r"^[A-Za-z0-9_]+$")
_TOP_LEVEL_KEYS = {
    "version",
    "ssot_owner",
    "update_trigger",
    "description",
    "routing_mode",
    "fallback_authorities",
    "semantic_queries",
    "profiles",
}
_PROFILE_KEYS = {"detect", "authorities"}
_DETECT_KEYS = {"keywords", "code_patterns", "file_globs", "signals"}


def _strip_comment(value: str) -> str:
    quote: str | None = None
    escaped = False
    for index, char in enumerate(value):
        if escaped:
            escaped = False
            continue
        if quote == '"' and char == "\\":
            escaped = True
            continue
        if char in {'"', "'"}:
            quote = None if quote == char else char if quote is None else quote
            continue
        if char == "#" and quote is None and (index == 0 or value[index - 1].isspace()):
            return value[:index].rstrip()
    if quote is not None:
        raise ManifestSyntaxError("unterminated quoted scalar")
    return value.rstrip()


def _scalar(raw: str, line_no: int) -> Any:
    value = _strip_comment(raw).strip()
    if value == "[]":
        return []
    if value == "{}":
        return {}
    if value.startswith('"'):
        try:
            parsed = json.loads(value)
        except json.JSONDecodeError as exc:
            raise ManifestSyntaxError(f"line {line_no}: invalid double-quoted scalar: {exc.msg}") from exc
        if not isinstance(parsed, str):
            raise ManifestSyntaxError(f"line {line_no}: quoted scalar must be a string")
        return parsed
    if value.startswith("'"):
        if len(value) < 2 or not value.endswith("'"):
            raise ManifestSyntaxError(f"line {line_no}: unterminated single-quoted scalar")
        inner = value[1:-1]
        if "'" in inner.replace("''", ""):
            raise ManifestSyntaxError(f"line {line_no}: invalid single-quoted scalar")
        return inner.replace("''", "'")
    if value.endswith(":") or "\t" in value or re.search(r":\s", value) or value.startswith(("!", "&", "*")) or any(char in value for char in "[]{}\""):
        raise ManifestSyntaxError(f"line {line_no}: unsupported or malformed scalar {value!r}")
    if value in {"true", "false"}:
        return value == "true"
    if re.fullmatch(r"[0-9]+", value):
        return int(value)
    if not value:
        raise ManifestSyntaxError(f"line {line_no}: missing scalar")
    return value


def parse_manifest(text: str) -> dict[str, Any]:
    raw_lines = text.splitlines()
    tokens: list[tuple[int, int, str]] = []
    index = 0
    while index < len(raw_lines):
        line_no = index + 1
        line = raw_lines[index]
        index += 1
        if "\t" in line[: len(line) - len(line.lstrip())]:
            raise ManifestSyntaxError(f"line {line_no}: tabs are not valid indentation")
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        indent = len(line) - len(line.lstrip(" "))
        if indent % 2:
            raise ManifestSyntaxError(f"line {line_no}: indentation must use two-space steps")
        content = line[indent:]
        if content.endswith(('|', '>-', '>')):
            match = re.fullmatch(r"([A-Za-z0-9_]+):\s*(\||>-|>)", content)
            if not match:
                raise ManifestSyntaxError(f"line {line_no}: malformed block scalar")
            parts: list[str] = []
            while index < len(raw_lines):
                child = raw_lines[index]
                child_indent = len(child) - len(child.lstrip(" "))
                if child.strip() and child_indent <= indent:
                    break
                index += 1
                if child.strip():
                    if child_indent != indent + 2:
                        raise ManifestSyntaxError(
                            f"line {index}: block scalar content must use exactly two additional spaces"
                        )
                    parts.append(child[indent + 2 :].strip())
            rendered = "\n".join(parts) if match.group(2) == "|" else " ".join(parts)
            tokens.append((line_no, indent, f"{match.group(1)}: {json.dumps(rendered)}"))
            continue
        tokens.append((line_no, indent, content))

    def parse_node(position: int, indent: int) -> tuple[Any, int]:
        if position >= len(tokens) or tokens[position][1] != indent:
            raise ManifestSyntaxError("unexpected end of nested value")
        is_list = tokens[position][2].startswith("- ")
        node: Any = [] if is_list else {}
        while position < len(tokens):
            line_no, current_indent, content = tokens[position]
            if current_indent < indent:
                break
            if current_indent > indent:
                raise ManifestSyntaxError(f"line {line_no}: unexpected indentation")
            if is_list:
                if not content.startswith("- "):
                    raise ManifestSyntaxError(f"line {line_no}: cannot mix mapping and list entries")
                item = content[2:].strip()
                if not item:
                    raise ManifestSyntaxError(f"line {line_no}: nested list items are unsupported")
                node.append(_scalar(item, line_no))
                position += 1
                continue
            if content.startswith("- ") or ":" not in content:
                raise ManifestSyntaxError(f"line {line_no}: expected mapping entry")
            key, raw = content.split(":", 1)
            key = key.strip()
            if not _KEY.fullmatch(key):
                raise ManifestSyntaxError(f"line {line_no}: invalid mapping key {key!r}")
            if key in node:
                raise ManifestSyntaxError(f"line {line_no}: duplicate mapping key {key!r}")
            raw = raw.strip()
            position += 1
            if raw:
                node[key] = _scalar(raw, line_no)
            else:
                if position >= len(tokens) or tokens[position][1] <= indent:
                    raise ManifestSyntaxError(f"line {line_no}: missing nested value for {key}")
                if tokens[position][1] != indent + 2:
                    raise ManifestSyntaxError(f"line {tokens[position][0]}: invalid nesting depth")
                node[key], position = parse_node(position, indent + 2)
        return node, position

    if not tokens:
        raise ManifestSyntaxError("manifest is empty")
    if tokens[0][1] != 0:
        raise ManifestSyntaxError(f"line {tokens[0][0]}: top-level content must not be indented")
    parsed, consumed = parse_node(0, 0)
    if consumed != len(tokens) or not isinstance(parsed, dict):
        raise ManifestSyntaxError("manifest root must be a mapping")
    return parsed


def _canonical_path(value: str) -> str | None:
    path = PurePosixPath(value)
    if (
        not value
        or "\\" in value
        or ":" in value
        or path.is_absolute()
        or path.as_posix() != value
        or any(part in {"", ".", ".."} or part != part.rstrip(" .") for part in path.parts)
    ):
        return None
    return "/".join(part.casefold() for part in path.parts)


def validate_manifest(
    governance_root: Path,
    store: DocumentStore,
    inventory: RepositoryInventory,
    root_authorities: tuple[str, ...],
) -> tuple[dict[str, Any] | None, list[str]]:
    path, validation_error = inventory.validate_file(governance_root / "agents-manifest.yaml")
    if validation_error:
        return None, [validation_error]
    assert path is not None
    text, read_error = store.read_text(path)
    if read_error:
        return None, [read_error]
    assert text is not None
    try:
        data = parse_manifest(text)
    except ManifestSyntaxError as exc:
        return None, [f"agents-manifest.yaml: {exc}"]

    errors: list[str] = []
    missing_top = sorted(_TOP_LEVEL_KEYS - set(data))
    unknown_top = sorted(set(data) - _TOP_LEVEL_KEYS)
    for key in missing_top:
        errors.append(f"agents-manifest.yaml: missing required top-level key: {key}")
    for key in unknown_top:
        errors.append(f"agents-manifest.yaml: unsupported top-level key: {key}")
    if data.get("version") != 2:
        errors.append("agents-manifest.yaml: version must be 2")
    if data.get("ssot_owner") != "agents-manifest.yaml":
        errors.append("agents-manifest.yaml: ssot_owner must be agents-manifest.yaml")
    for field in ("update_trigger", "description"):
        value = data.get(field)
        if not isinstance(value, str) or not value.strip():
            errors.append(f"agents-manifest.yaml: {field} must be a non-empty string")
    if data.get("routing_mode") not in {"union", "first_match"}:
        errors.append("agents-manifest.yaml: routing_mode must be union or first_match")
    profiles = data.get("profiles")
    fallback = data.get("fallback_authorities")
    if not isinstance(profiles, dict) or not profiles:
        errors.append("agents-manifest.yaml: profiles must be a non-empty mapping")
        profiles = {}
    if not isinstance(fallback, list) or not fallback:
        errors.append("agents-manifest.yaml: fallback_authorities must be a non-empty list")
        fallback = []
    semantic = data.get("semantic_queries", {})
    if not isinstance(semantic, dict):
        errors.append("agents-manifest.yaml: semantic_queries must be a mapping")
        semantic = {}

    authority_lists: list[tuple[str, object]] = [("fallback_authorities", fallback)]
    for name, profile in profiles.items():
        if not isinstance(profile, dict):
            errors.append(f"agents-manifest.yaml: profiles.{name} must be a mapping")
            continue
        for key in sorted(_PROFILE_KEYS - set(profile)):
            errors.append(f"agents-manifest.yaml: profiles.{name} missing required key: {key}")
        for key in sorted(set(profile) - _PROFILE_KEYS):
            errors.append(f"agents-manifest.yaml: profiles.{name} has unsupported key: {key}")
        detect = profile.get("detect")
        authorities = profile.get("authorities")
        if not isinstance(detect, dict) or not detect:
            errors.append(f"agents-manifest.yaml: profiles.{name}.detect must be a non-empty mapping")
        else:
            for signal_name in sorted(set(detect) - _DETECT_KEYS):
                errors.append(
                    f"agents-manifest.yaml: profiles.{name}.detect has unsupported key: {signal_name}"
                )
            for signal_name, signals in detect.items():
                if not isinstance(signals, list):
                    errors.append(f"agents-manifest.yaml: profiles.{name}.detect.{signal_name} must be a list")
                elif any(not isinstance(signal, str) or not signal for signal in signals):
                    errors.append(f"agents-manifest.yaml: profiles.{name}.detect.{signal_name} contains an invalid signal")
        authority_lists.append((f"profiles.{name}.authorities", authorities))
    for name, queries in semantic.items():
        if name not in profiles:
            errors.append(f"agents-manifest.yaml: semantic_queries.{name} has no profile")
        if not isinstance(queries, list) or not queries or any(
            not isinstance(item, str) or not item.strip() for item in queries
        ):
            errors.append(f"agents-manifest.yaml: semantic_queries.{name} must be a non-empty string list")

    root_keys = {_canonical_path(value) for value in root_authorities}
    root_targets = [resolve_declared_file(governance_root, value)[0] for value in root_authorities]
    for label, values in authority_lists:
        if not isinstance(values, list) or not values:
            errors.append(f"agents-manifest.yaml: {label} must be a non-empty list")
            continue
        seen: set[str] = set()
        seen_targets: list[Path] = []
        for value in values:
            if not isinstance(value, str):
                errors.append(f"agents-manifest.yaml: {label} contains a non-string authority")
                continue
            key = _canonical_path(value)
            if key is None:
                errors.append(f"agents-manifest.yaml: {label} contains an invalid authority path: {value!r}")
                continue
            if key in seen:
                errors.append(f"agents-manifest.yaml: {label} contains a duplicate authority path: {value}")
            seen.add(key)
            if key in root_keys:
                errors.append(f"agents-manifest.yaml: {label} contains root-owned authority: {value}")
            _candidate, path_error = resolve_declared_file(governance_root, value)
            if path_error:
                errors.append(f"agents-manifest.yaml: {label} authority {path_error}")
                continue
            assert _candidate is not None
            if any(_candidate.samefile(target) for target in root_targets if target is not None):
                if key not in root_keys:
                    errors.append(f"agents-manifest.yaml: {label} aliases a root-owned authority: {value}")
            if any(_candidate.samefile(target) for target in seen_targets):
                errors.append(f"agents-manifest.yaml: {label} aliases an earlier authority: {value}")
            seen_targets.append(_candidate)
    return data, errors
