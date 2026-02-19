from __future__ import annotations

import argparse
from typing import Any

from common import load_contract, read_json, write_json


def evaluate_thread_resolution(
    contract: dict[str, Any],
    threads: list[dict[str, Any]],
    clean_rerun: bool,
) -> dict[str, Any]:
    policy = contract["threadPolicy"]
    enabled = bool(policy.get("autoResolveBotOnlyAfterCleanRerun", False))
    if not enabled:
        return {
            "result": "SKIPPED",
            "reason": "AUTO_RESOLVE_DISABLED",
            "toResolve": [],
            "skipped": [],
        }

    if not clean_rerun:
        return {
            "result": "SKIPPED",
            "reason": "CLEAN_RERUN_REQUIRED",
            "toResolve": [],
            "skipped": [],
        }

    allowlist = set(policy.get("botAuthorAllowlist", []))
    to_resolve: list[str] = []
    skipped: list[dict[str, Any]] = []

    for thread in threads:
        thread_id = str(thread.get("id", ""))
        if not thread_id:
            skipped.append({"threadId": None, "reason": "MISSING_THREAD_ID"})
            continue

        if bool(thread.get("isResolved", False)):
            skipped.append({"threadId": thread_id, "reason": "ALREADY_RESOLVED"})
            continue

        comments = thread.get("comments", [])
        if not comments:
            skipped.append({"threadId": thread_id, "reason": "NO_COMMENTS"})
            continue

        authors = {
            str(comment.get("author_login", "")).strip()
            for comment in comments
            if isinstance(comment, dict)
        }
        if not authors:
            skipped.append({"threadId": thread_id, "reason": "UNKNOWN_AUTHORS"})
            continue

        if authors.issubset(allowlist):
            to_resolve.append(thread_id)
        else:
            skipped.append(
                {
                    "threadId": thread_id,
                    "reason": "HUMAN_PARTICIPATION_DETECTED",
                    "authors": sorted(authors),
                }
            )

    return {
        "result": "SUCCESS",
        "reason": "THREAD_SCAN_COMPLETE",
        "toResolve": to_resolve,
        "skipped": skipped,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Resolve bot-only review threads after clean rerun.")
    parser.add_argument("--contract", required=True, help="Path to control-plane contract JSON.")
    parser.add_argument(
        "--threads-json",
        required=True,
        help="JSON list/path of review threads with comments and author_login fields.",
    )
    parser.add_argument(
        "--clean-rerun",
        action="store_true",
        help="Indicates current-head rerun is clean and eligible for auto-resolve.",
    )
    parser.add_argument("--output-json", default="-", help="Output JSON path or '-' for stdout.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    contract = load_contract(args.contract)
    threads = read_json(args.threads_json)
    if not isinstance(threads, list):
        raise ValueError("threads-json must resolve to a JSON list")

    result = evaluate_thread_resolution(
        contract=contract,
        threads=[entry for entry in threads if isinstance(entry, dict)],
        clean_rerun=args.clean_rerun,
    )
    write_json(args.output_json, result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
