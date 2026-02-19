from __future__ import annotations

import argparse
from typing import Any

from common import load_contract, read_json, write_json


def _is_actionable(finding: dict[str, Any]) -> bool:
    if bool(finding.get("actionable", False)):
        return True
    severity = str(finding.get("severity", "")).lower()
    if severity in {"critical", "high", "medium"}:
        return True
    return False


def _count_attempts(attempts: list[dict[str, Any]], head_sha: str) -> int:
    count = 0
    for entry in attempts:
        if not isinstance(entry, dict):
            continue
        if str(entry.get("headSha", "")) == head_sha:
            count += 1
    return count


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
    branch_name = f"{branch_prefix}/{head_sha[:12]}"
    return {
        "result": "SUCCESS",
        "action": "REMEDIATION_REQUESTED",
        "reason": "ACTIONABLE_FINDINGS_PRESENT",
        "headSha": head_sha,
        "branchName": branch_name,
        "attemptsUsed": attempts_used,
        "maxAttemptsPerSha": max_attempts,
        "actionableFindingCount": len(actionable),
        "neverBypassPolicyGate": bool(policy.get("neverBypassPolicyGate", True)),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evaluate deterministic remediation action for findings.")
    parser.add_argument("--contract", required=True, help="Path to control-plane contract JSON.")
    parser.add_argument("--head-sha", required=True, help="Current PR head SHA.")
    parser.add_argument(
        "--findings-json",
        required=True,
        help="JSON list/path for normalized findings.",
    )
    parser.add_argument(
        "--attempt-history-json",
        required=False,
        default="[]",
        help="JSON list/path of prior remediation attempts.",
    )
    parser.add_argument("--output-json", default="-", help="Output JSON path or '-' for stdout.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    contract = load_contract(args.contract)
    findings = read_json(args.findings_json)
    if not isinstance(findings, list):
        raise ValueError("findings-json must resolve to a JSON list")
    attempt_history = read_json(args.attempt_history_json)
    if not isinstance(attempt_history, list):
        raise ValueError("attempt-history-json must resolve to a JSON list")

    result = evaluate_remediation(
        contract=contract,
        head_sha=args.head_sha,
        findings=[entry for entry in findings if isinstance(entry, dict)],
        attempt_history=[entry for entry in attempt_history if isinstance(entry, dict)],
    )
    write_json(args.output_json, result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
