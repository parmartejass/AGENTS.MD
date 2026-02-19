from __future__ import annotations

import argparse
from typing import Any

from common import load_contract, read_json, write_json


def evaluate_rerun_request(
    contract: dict[str, Any],
    head_sha: str,
    comments: list[dict[str, Any]],
) -> dict[str, Any]:
    policy = contract["rerunPolicy"]
    if not policy.get("enabled", True):
        return {
            "result": "SKIPPED",
            "reason": "RERUN_DISABLED_BY_POLICY",
            "shouldPost": False,
            "headSha": head_sha,
        }

    marker = str(policy["commentMarker"])
    trigger_token = f"sha:{head_sha}"
    trigger_text = str(policy["triggerText"])

    already_requested = False
    for comment in comments:
        body = str(comment.get("body", ""))
        if marker in body and trigger_token in body:
            already_requested = True
            break

    if already_requested:
        return {
            "result": "SKIPPED",
            "reason": "RERUN_ALREADY_REQUESTED_FOR_HEAD",
            "shouldPost": False,
            "headSha": head_sha,
            "dedupeKey": f"{marker}|{trigger_token}",
        }

    return {
        "result": "SUCCESS",
        "reason": "RERUN_REQUEST_CREATED",
        "shouldPost": True,
        "headSha": head_sha,
        "dedupeKey": f"{marker}|{trigger_token}",
        "commentBody": "\n".join([marker, trigger_text, trigger_token]),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Canonical rerun-comment dedupe evaluator.")
    parser.add_argument("--contract", required=True, help="Path to control-plane contract JSON.")
    parser.add_argument("--head-sha", required=True, help="Current PR head SHA.")
    parser.add_argument(
        "--comments-json",
        required=True,
        help="JSON list/path of issue comments with at least `body` fields.",
    )
    parser.add_argument("--output-json", default="-", help="Output JSON path or '-' for stdout.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    contract = load_contract(args.contract)
    comments = read_json(args.comments_json)
    if not isinstance(comments, list):
        raise ValueError("comments-json must resolve to a JSON list")

    result = evaluate_rerun_request(
        contract=contract,
        head_sha=args.head_sha,
        comments=[entry for entry in comments if isinstance(entry, dict)],
    )
    write_json(args.output_json, result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
