from __future__ import annotations

from typing import Any


def _is_actionable(finding: dict[str, Any]) -> bool:
    if bool(finding.get("actionable", False)):
        return True
    severity = str(finding.get("severity", "")).lower()
    return severity in {"critical", "high", "medium"}


def _count_attempts(attempts: list[dict[str, Any]], head_sha: str) -> int:
    return sum(1 for entry in attempts if isinstance(entry, dict) and str(entry.get("headSha", "")) == head_sha)


def evaluate_remediation(
    contract: dict[str, Any],
    head_sha: str,
    findings: list[dict[str, Any]],
    attempt_history: list[dict[str, Any]],
) -> dict[str, Any]:
    policy = contract["remediationPolicy"]
    if not bool(policy.get("enabled", False)):
        return {
            "result": "SKIPPED",
            "action": "NO_ACTION",
            "reason": "REMEDIATION_DISABLED_BY_POLICY",
            "headSha": head_sha,
        }

    actionable = [finding for finding in findings if _is_actionable(finding)]
    if not actionable:
        return {
            "result": "SKIPPED",
            "action": "NO_ACTION",
            "reason": "NO_ACTIONABLE_FINDINGS",
            "headSha": head_sha,
            "actionableFindingCount": 0,
        }

    attempts_used = _count_attempts(attempt_history, head_sha=head_sha)
    max_attempts = int(policy.get("maxAttemptsPerSha", 1))
    if attempts_used >= max_attempts:
        return {
            "result": "SKIPPED",
            "action": "NO_ACTION",
            "reason": "MAX_ATTEMPTS_REACHED",
            "headSha": head_sha,
            "attemptsUsed": attempts_used,
            "maxAttemptsPerSha": max_attempts,
            "actionableFindingCount": len(actionable),
        }

    branch_prefix = str(policy.get("branchPrefix", "remediation"))
    return {
        "result": "SUCCESS",
        "action": "REMEDIATION_REQUESTED",
        "reason": "ACTIONABLE_FINDINGS_PRESENT",
        "headSha": head_sha,
        "branchName": f"{branch_prefix}/{head_sha[:12]}",
        "attemptsUsed": attempts_used,
        "maxAttemptsPerSha": max_attempts,
        "actionableFindingCount": len(actionable),
        "neverBypassPolicyGate": bool(policy.get("neverBypassPolicyGate", True)),
    }
