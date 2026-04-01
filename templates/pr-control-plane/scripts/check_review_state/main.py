from __future__ import annotations

import datetime as dt
from typing import Any


UTC = dt.timezone.utc


def _parse_iso8601(value: str) -> dt.datetime:
    normalized = value.replace("Z", "+00:00")
    parsed = dt.datetime.fromisoformat(normalized)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)


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


def _text_blob(item: dict[str, Any]) -> str:
    parts = [
        str(item.get("title", "")),
        str(item.get("summary", "")),
        str(item.get("body", "")),
        str(item.get("message", "")),
    ]
    return " ".join(parts).lower()


def _find_actionable_findings(
    findings: list[dict[str, Any]],
    actionable_tokens: list[str],
    weak_confidence_tokens: list[str],
) -> list[dict[str, Any]]:
    actionable: list[dict[str, Any]] = []
    token_set = [token.lower() for token in actionable_tokens + weak_confidence_tokens]
    severe_levels = {"critical", "high", "medium"}

    for finding in findings:
        severity = str(finding.get("severity", "")).lower()
        confidence = str(finding.get("confidence", "")).lower()
        text = _text_blob(finding)
        token_hit = any(token in text for token in token_set)
        severe = severity in severe_levels
        explicit = bool(finding.get("actionable", False))
        weak_confidence = confidence in {"low", "unknown"}

        if explicit or severe or weak_confidence or token_hit:
            actionable.append(
                {
                    "id": finding.get("id"),
                    "severity": severity,
                    "confidence": confidence,
                    "summary": finding.get("summary") or finding.get("title") or finding.get("message"),
                }
            )
    return actionable


def select_latest_review_run(
    review_runs: list[dict[str, Any]],
    required_check_name: str,
    head_sha: str | None,
) -> dict[str, Any] | None:
    candidates = [run for run in review_runs if run.get("name") == required_check_name]
    if head_sha:
        head_matches = [run for run in candidates if run.get("head_sha") == head_sha]
        if head_matches:
            candidates = head_matches
    if not candidates:
        return None
    return sorted(candidates, key=_run_sort_key, reverse=True)[0]


def evaluate_review_state(
    contract: dict[str, Any],
    head_sha: str,
    review_run: dict[str, Any] | None,
    findings: list[dict[str, Any]],
    timed_out: bool = False,
) -> dict[str, Any]:
    failures: list[dict[str, Any]] = []
    review_policy = contract["reviewPolicy"]

    if not review_policy.get("enabled", True):
        return {
            "result": "SUCCESS",
            "headSha": head_sha,
            "reviewRun": None,
            "actionableFindingCount": 0,
            "failures": [],
        }

    required_current_head = bool(review_policy.get("requireCurrentHeadSha", True))

    if timed_out:
        failures.append(
            {
                "code": "REVIEW_TIMEOUT",
                "message": "Review-agent state did not complete before timeout.",
                "detail": {"headSha": head_sha, "timeoutMinutes": review_policy.get("timeoutMinutes")},
            }
        )
    elif review_run is None:
        failures.append(
            {
                "code": "MISSING_REVIEW_RUN",
                "message": "No review-agent check run found for policy evaluation.",
                "detail": {"requiredReviewCheck": review_policy.get("requiredReviewCheck")},
            }
        )
    else:
        if required_current_head and review_run.get("head_sha") != head_sha:
            failures.append(
                {
                    "code": "STALE_REVIEW_RUN",
                    "message": "Latest review run does not match the current PR head SHA.",
                    "detail": {
                        "expectedHeadSha": head_sha,
                        "reviewHeadSha": review_run.get("head_sha"),
                    },
                }
            )

        if review_run.get("status") != "completed" or review_run.get("conclusion") != "success":
            failures.append(
                {
                    "code": "REVIEW_NOT_SUCCESS",
                    "message": "Review check run is not successful.",
                    "detail": {
                        "status": review_run.get("status"),
                        "conclusion": review_run.get("conclusion"),
                    },
                }
            )

        summary = str(review_run.get("summary", "")).lower()
        weak_tokens = [token.lower() for token in review_policy.get("weakConfidenceTokens", [])]
        action_tokens = [token.lower() for token in review_policy.get("actionableTokens", [])]
        summary_token_hit = any(token in summary for token in (weak_tokens + action_tokens))
        if summary_token_hit:
            failures.append(
                {
                    "code": "ACTIONABLE_REVIEW_SUMMARY",
                    "message": "Review summary contains actionable or weak-confidence language.",
                    "detail": {"summary": review_run.get("summary", "")},
                }
            )

    actionable_findings = _find_actionable_findings(
        findings=findings,
        actionable_tokens=review_policy.get("actionableTokens", []),
        weak_confidence_tokens=review_policy.get("weakConfidenceTokens", []),
    )
    if actionable_findings:
        failures.append(
            {
                "code": "ACTIONABLE_FINDINGS_PRESENT",
                "message": "Actionable findings exist for the current head.",
                "detail": {"count": len(actionable_findings), "findings": actionable_findings},
            }
        )

    result = "FAILURE" if failures else "SUCCESS"
    return {
        "result": result,
        "headSha": head_sha,
        "reviewRun": review_run,
        "actionableFindingCount": len(actionable_findings),
        "failures": failures,
    }
