from __future__ import annotations

import datetime as dt
from fnmatch import fnmatch
from typing import Any, Iterable


UTC = dt.timezone.utc


def _parse_iso8601(value: str) -> dt.datetime:
    normalized = value.replace("Z", "+00:00")
    parsed = dt.datetime.fromisoformat(normalized)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)


def _matches_any(path: str, patterns: Iterable[str]) -> bool:
    return any(fnmatch(path, pattern) for pattern in patterns)


def compute_risk_tier(changed_files: list[str], risk_tier_rules: dict[str, list[str]]) -> str:
    if not risk_tier_rules:
        raise ValueError("riskTierRules must not be empty")

    matched_tiers: set[str] = set()
    for tier, patterns in risk_tier_rules.items():
        if any(_matches_any(changed, patterns) for changed in changed_files):
            matched_tiers.add(tier)

    for tier in ("high", "medium", "low"):
        if tier in matched_tiers:
            return tier

    if matched_tiers:
        return sorted(matched_tiers)[0]
    if "low" in risk_tier_rules:
        return "low"
    return sorted(risk_tier_rules.keys())[0]


def _normalize_check_runs(value: Any) -> list[dict[str, Any]]:
    if value is None:
        return []
    if isinstance(value, list):
        return [entry for entry in value if isinstance(entry, dict)]
    if isinstance(value, dict) and isinstance(value.get("check_runs"), list):
        return [entry for entry in value["check_runs"] if isinstance(entry, dict)]
    raise ValueError("check runs must be a list or an object with check_runs")


def _check_run_is_success(run: dict[str, Any]) -> bool:
    return run.get("status") == "completed" and run.get("conclusion") == "success"


def _run_sort_key(run: dict[str, Any]) -> dt.datetime:
    completed_at = run.get("completed_at")
    if isinstance(completed_at, str) and completed_at:
        try:
            return _parse_iso8601(completed_at)
        except ValueError:
            pass

    started_at = run.get("started_at")
    if isinstance(started_at, str) and started_at:
        try:
            return _parse_iso8601(started_at)
        except ValueError:
            pass

    return dt.datetime(1970, 1, 1, tzinfo=UTC)


def evaluate_policy(
    contract: dict[str, Any],
    changed_files: list[str],
    check_runs: list[dict[str, Any]] | dict[str, Any] | None = None,
    head_sha: str | None = None,
) -> dict[str, Any]:
    failures: list[dict[str, Any]] = []
    risk_tier = compute_risk_tier(changed_files, contract["riskTierRules"])
    required_checks = contract["mergePolicy"].get(risk_tier, {}).get("requiredChecks", [])

    docs_drift = contract["docsDriftRules"]
    control_plane_paths = docs_drift.get("controlPlanePaths", [])
    required_docs = docs_drift.get("requiredDocs", [])
    control_plane_changed = [path for path in changed_files if _matches_any(path, control_plane_paths)]
    if control_plane_changed:
        missing_docs = [doc for doc in required_docs if doc not in changed_files]
        if missing_docs:
            failures.append(
                {
                    "code": "DOCS_DRIFT_REQUIRED_DOCS_MISSING",
                    "message": "Control-plane changes require corresponding docs updates.",
                    "detail": {
                        "controlPlaneChanged": control_plane_changed,
                        "missingDocs": missing_docs,
                    },
                }
            )

    checks_validated = False
    if check_runs is not None:
        if not head_sha:
            failures.append(
                {
                    "code": "HEAD_SHA_REQUIRED",
                    "message": "Current head SHA is required when validating check runs.",
                    "detail": {"requiredChecks": required_checks},
                }
            )
            return {
                "result": "FAILURE",
                "riskTier": risk_tier,
                "requiredChecks": required_checks,
                "checksValidated": False,
                "failures": failures,
            }
        checks_validated = True
        normalized_runs = _normalize_check_runs(check_runs)
        for required_name in required_checks:
            matches = [run for run in normalized_runs if run.get("name") == required_name]
            if head_sha:
                matches = [run for run in matches if run.get("head_sha") == head_sha]

            if not matches:
                failures.append(
                    {
                        "code": "MISSING_REQUIRED_CHECK",
                        "message": f"Required check '{required_name}' was not found for the current head.",
                        "detail": {"requiredCheck": required_name, "headSha": head_sha},
                    }
                )
                continue

            latest = sorted(matches, key=_run_sort_key, reverse=True)[0]
            if not _check_run_is_success(latest):
                failures.append(
                    {
                        "code": "REQUIRED_CHECK_NOT_SUCCESS",
                        "message": f"Required check '{required_name}' is not successful.",
                        "detail": {
                            "requiredCheck": required_name,
                            "status": latest.get("status"),
                            "conclusion": latest.get("conclusion"),
                            "headSha": latest.get("head_sha"),
                        },
                    }
                )

    return {
        "result": "FAILURE" if failures else "SUCCESS",
        "riskTier": risk_tier,
        "requiredChecks": required_checks,
        "checksValidated": checks_validated,
        "failures": failures,
    }
