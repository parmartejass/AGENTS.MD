from __future__ import annotations

import re
from pathlib import Path
from typing import List, Sequence, Tuple
from urllib.parse import unquote


def normalize_link_target(raw_target: str) -> str:
    target = unquote(raw_target.strip())
    if not target:
        return ""
    if re.match(r"^[A-Za-z][A-Za-z0-9+.-]*:", target) or target.startswith("//"):
        return ""
    target = target.split("?", 1)[0]
    target = target.split("#", 1)[0]
    target = target.replace("\\", "/")
    if target.startswith("/"):
        return ""
    while target.startswith("./"):
        target = target[2:]
    parts: List[str] = []
    for part in target.split("/"):
        if part in {"", "."}:
            continue
        if part == "..":
            return ""
        parts.append(part)
    return "/".join(parts)


def extract_route_targets(router_text: str) -> Tuple[List[str], List[str]]:
    errors: List[str] = []
    targets: List[str] = []
    lines = [line.rstrip() for line in router_text.splitlines() if line.strip()]
    if not lines:
        return targets, ["Router file is empty."]
    if not lines[0].startswith("# "):
        return targets, ["Router file must begin with a markdown heading."]

    for line in lines[1:]:
        stripped = line.strip()
        if not stripped.startswith("- "):
            errors.append("Router files must remain routing-only (title plus route bullets only).")
            continue
        if "Required when:" not in stripped:
            errors.append("Router bullet is missing 'Required when:'.")
        match = re.search(r"\[[^\]]+\]\(([^)]+)\)", stripped)
        if match is None:
            errors.append("Router bullet is missing a markdown link target.")
            continue
        normalized = normalize_link_target(match.group(1))
        if not normalized:
            errors.append(f"Router bullet uses an invalid or out-of-bounds link target: {match.group(1)!r}")
            continue
        targets.append(normalized)
    return targets, errors


def targets_child(targets: Sequence[str], child: Path, *, child_router_filename: str) -> bool:
    child_name = child.name
    if child.is_dir():
        allowed = {child_name, f"{child_name}/{child_router_filename}"}
    else:
        allowed = {child_name}
    return any(target in allowed for target in targets)


def is_header_exempt_markdown(rel: str) -> bool:
    return rel.endswith("/SKILL.md")
