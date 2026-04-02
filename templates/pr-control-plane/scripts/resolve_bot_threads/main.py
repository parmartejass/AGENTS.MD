from __future__ import annotations

from typing import Any


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
