from __future__ import annotations

import argparse
from typing import Any

from common import load_contract, normalize_check_runs, read_json, run_sort_key, write_json


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


def _select_latest_review_run(
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
    return sorted(candidates, key=run_sort_key, reverse=True)[0]


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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate review-agent state for current PR head.")
    parser.add_argument("--contract", required=True, help="Path to control-plane contract JSON.")
    parser.add_argument("--head-sha", required=True, help="Current PR head SHA.")
    parser.add_argument(
        "--review-runs-json",
        required=True,
        help="JSON list/object of check runs used to locate the review-agent run.",
    )
    parser.add_argument(
        "--findings-json",
        required=False,
        default="[]",
        help="JSON list/path for normalized findings tied to head SHA.",
    )
    parser.add_argument("--timed-out", action="store_true", help="Force timeout failure mode.")
    parser.add_argument("--output-json", default="-", help="Output JSON path or '-' for stdout.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    contract = load_contract(args.contract)
    review_policy = contract["reviewPolicy"]
    review_runs = normalize_check_runs(read_json(args.review_runs_json))
    review_run = _select_latest_review_run(
        review_runs=review_runs,
        required_check_name=str(review_policy.get("requiredReviewCheck")),
        head_sha=args.head_sha,
    )

    findings = read_json(args.findings_json)
    if not isinstance(findings, list):
        raise ValueError("findings-json must resolve to a JSON list")

    result = evaluate_review_state(
        contract=contract,
        head_sha=args.head_sha,
        review_run=review_run,
        findings=[entry for entry in findings if isinstance(entry, dict)],
        timed_out=args.timed_out,
    )
    write_json(args.output_json, result)
    return 0 if result["result"] == "SUCCESS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
