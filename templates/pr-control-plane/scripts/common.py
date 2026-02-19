from __future__ import annotations

import datetime as dt
import json
import os
import sys
import tempfile
from fnmatch import fnmatch
from pathlib import Path
from typing import Any, Iterable


UTC = dt.timezone.utc


def parse_iso8601(value: str) -> dt.datetime:
    normalized = value.replace("Z", "+00:00")
    parsed = dt.datetime.fromisoformat(normalized)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)


def utc_now() -> dt.datetime:
    return dt.datetime.now(tz=UTC)


def read_json(path_or_json: str) -> Any:
    try:
        return json.loads(path_or_json)
    except json.JSONDecodeError:
        candidate = Path(path_or_json)
        if not candidate.exists():
            raise
        return json.loads(candidate.read_text(encoding="utf-8"))


def write_json(path: str, payload: dict[str, Any]) -> None:
    if path == "-":
        sys.stdout.write(json.dumps(payload, indent=2, sort_keys=True) + "\n")
        sys.stdout.flush()
        return

    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    _atomic_write_text(target, json.dumps(payload, indent=2, sort_keys=True))


def _atomic_write_text(target: Path, content: str) -> None:
    with tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        dir=str(target.parent),
        delete=False,
        prefix=f".{target.name}.",
        suffix=".tmp",
    ) as handle:
        handle.write(content)
        handle.flush()
        os.fsync(handle.fileno())
        temp_path = Path(handle.name)
    temp_path.replace(target)


def load_contract(path: str) -> dict[str, Any]:
    contract = read_json(path)
    required_keys = (
        "riskTierRules",
        "mergePolicy",
        "docsDriftRules",
        "reviewPolicy",
        "rerunPolicy",
        "remediationPolicy",
        "threadPolicy",
        "browserEvidencePolicy",
        "harnessGapPolicy",
    )
    missing = [key for key in required_keys if key not in contract]
    if missing:
        raise ValueError(f"Contract missing required keys: {', '.join(missing)}")
    return contract


def matches_any(path: str, patterns: Iterable[str]) -> bool:
    for pattern in patterns:
        if fnmatch(path, pattern):
            return True
    return False


def compute_risk_tier(changed_files: list[str], risk_tier_rules: dict[str, list[str]]) -> str:
    matched_tiers: set[str] = set()
    for tier, patterns in risk_tier_rules.items():
        if any(matches_any(changed, patterns) for changed in changed_files):
            matched_tiers.add(tier)

    precedence = ["high", "medium", "low"]
    for tier in precedence:
        if tier in matched_tiers:
            return tier

    if matched_tiers:
        return sorted(matched_tiers)[0]

    if "low" in risk_tier_rules:
        return "low"

    return sorted(risk_tier_rules.keys())[0]


def normalize_check_runs(value: Any) -> list[dict[str, Any]]:
    if value is None:
        return []
    if isinstance(value, list):
        return [entry for entry in value if isinstance(entry, dict)]
    if isinstance(value, dict) and isinstance(value.get("check_runs"), list):
        return [entry for entry in value["check_runs"] if isinstance(entry, dict)]
    raise ValueError("check runs must be a list or an object with check_runs")


def check_run_is_success(run: dict[str, Any]) -> bool:
    return run.get("status") == "completed" and run.get("conclusion") == "success"


def run_sort_key(run: dict[str, Any]) -> dt.datetime:
    completed_at = run.get("completed_at")
    if isinstance(completed_at, str) and completed_at:
        try:
            return parse_iso8601(completed_at)
        except ValueError:
            pass

    started_at = run.get("started_at")
    if isinstance(started_at, str) and started_at:
        try:
            return parse_iso8601(started_at)
        except ValueError:
            pass

    return dt.datetime(1970, 1, 1, tzinfo=UTC)
