"""Sanitization/redaction helpers for structured logs."""

from __future__ import annotations

import hashlib
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any


_SENSITIVE_KEY_TOKENS = ("token", "password", "secret", "key", "credential")
_REDACTED = "[REDACTED]"


def sanitize_for_logging(value: Any, *, key_name: str | None = None) -> Any:
    if key_name is not None and _looks_sensitive_key(key_name):
        return _REDACTED

    if isinstance(value, Mapping):
        return {str(k): sanitize_for_logging(v, key_name=str(k)) for k, v in value.items()}

    if isinstance(value, Path):
        return describe_path(value)

    if isinstance(value, str):
        if len(value) <= 256:
            return value
        return _summarize_large_string(value)

    if isinstance(value, bytes):
        return {
            "type": "bytes",
            "size_bytes": len(value),
            "sha256": hashlib.sha256(value).hexdigest(),
        }

    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        items_raw = list(value)
        items = [sanitize_for_logging(item) for item in items_raw[:20]]
        if len(items_raw) > 20:
            items.append({"truncated_items": len(items_raw) - 20})
        return items

    if isinstance(value, (int, float, bool)) or value is None:
        return value

    return str(value)


def describe_path(path: Path) -> dict[str, Any]:
    path = Path(path)
    info: dict[str, Any] = {
        "path": str(path),
        "exists": path.exists(),
    }
    if path.exists():
        info["is_file"] = path.is_file()
        info["is_dir"] = path.is_dir()
        if path.is_file():
            info["size_bytes"] = path.stat().st_size
    return info


def _looks_sensitive_key(key_name: str) -> bool:
    key = key_name.lower()
    return any(token in key for token in _SENSITIVE_KEY_TOKENS)


def _summarize_large_string(value: str) -> dict[str, Any]:
    raw = value.encode("utf-8")
    preview = value[:128]
    return {
        "type": "large_string",
        "preview": preview,
        "length": len(value),
        "sha256": hashlib.sha256(raw).hexdigest(),
    }
