from __future__ import annotations

import copy
from typing import Any


class MockReviewAdapter:
    def __init__(
        self,
        review_runs: list[dict[str, Any]],
        findings_by_sha: dict[str, list[dict[str, Any]]],
        threads_by_sha: dict[str, list[dict[str, Any]]],
    ) -> None:
        self._review_runs = copy.deepcopy(review_runs)
        self._findings_by_sha = copy.deepcopy(findings_by_sha)
        self._threads_by_sha = copy.deepcopy(threads_by_sha)

    @staticmethod
    def _sort_key(run: dict[str, Any]) -> str:
        return str(run.get("completed_at") or run.get("started_at") or "")

    def get_latest_review_run(self, head_sha: str) -> dict[str, Any] | None:
        matches = [run for run in self._review_runs if str(run.get("head_sha")) == head_sha]
        if not matches:
            return None
        latest = sorted(matches, key=self._sort_key, reverse=True)[0]
        return copy.deepcopy(latest)

    def list_findings(self, head_sha: str) -> list[dict[str, Any]]:
        return copy.deepcopy(self._findings_by_sha.get(head_sha, []))

    def request_rerun(
        self,
        head_sha: str,
        existing_comments: list[dict[str, Any]],
        marker: str,
        trigger_text: str,
    ) -> dict[str, Any]:
        trigger = f"sha:{head_sha}"
        already_requested = False
        for comment in existing_comments:
            body = str(comment.get("body", ""))
            if marker in body and trigger in body:
                already_requested = True
                break

        if already_requested:
            return {
                "should_post": False,
                "reason": "already_requested_for_head",
                "comment_body": None,
            }

        comment_body = "\n".join([marker, trigger_text, trigger])
        return {
            "should_post": True,
            "reason": "new_request",
            "comment_body": comment_body,
        }

    def list_threads(self, head_sha: str) -> list[dict[str, Any]]:
        return copy.deepcopy(self._threads_by_sha.get(head_sha, []))

    def resolve_thread(self, thread_id: str) -> bool:
        for threads in self._threads_by_sha.values():
            for thread in threads:
                if str(thread.get("id")) == thread_id:
                    if bool(thread.get("isResolved", False)):
                        return False
                    thread["isResolved"] = True
                    return True
        return False
