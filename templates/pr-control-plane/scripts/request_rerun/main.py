from __future__ import annotations

from typing import Any


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

    for comment in comments:
        body = str(comment.get("body", ""))
        if marker in body and trigger_token in body:
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
