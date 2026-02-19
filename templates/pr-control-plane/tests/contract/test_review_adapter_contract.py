from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from adapters.mock.adapter import MockReviewAdapter  # noqa: E402


FIXTURES = ROOT / "tests" / "fixtures"


def _load_fixture(name: str):
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


class ReviewAdapterContractTests(unittest.TestCase):
    def setUp(self) -> None:
        review_runs = [
            _load_fixture("review_run_clean.json"),
            _load_fixture("review_run_stale.json"),
        ]
        findings_by_sha = {
            "abc123": _load_fixture("findings_clean.json"),
            "oldsha": _load_fixture("findings_actionable.json"),
        }
        threads_by_sha = {
            "abc123": _load_fixture("threads.json"),
        }
        self.adapter = MockReviewAdapter(review_runs, findings_by_sha, threads_by_sha)

    def test_latest_review_run_is_head_specific(self) -> None:
        run = self.adapter.get_latest_review_run("abc123")
        self.assertIsNotNone(run)
        self.assertEqual(run["head_sha"], "abc123")
        missing = self.adapter.get_latest_review_run("does-not-exist")
        self.assertIsNone(missing)

    def test_rerun_request_is_deduped_by_marker_and_sha(self) -> None:
        marker = "<!-- review-agent-auto-rerun -->"
        trigger_text = "@review-agent please re-review"

        already = self.adapter.request_rerun(
            head_sha="abc123",
            existing_comments=_load_fixture("comments_with_marker.json"),
            marker=marker,
            trigger_text=trigger_text,
        )
        self.assertFalse(already["should_post"])

        missing = self.adapter.request_rerun(
            head_sha="abc123",
            existing_comments=_load_fixture("comments_without_marker.json"),
            marker=marker,
            trigger_text=trigger_text,
        )
        self.assertTrue(missing["should_post"])
        self.assertIn("sha:abc123", missing["comment_body"])

    def test_resolve_thread_marks_unresolved_thread(self) -> None:
        resolved = self.adapter.resolve_thread("thread-bot-only")
        self.assertTrue(resolved)
        second = self.adapter.resolve_thread("thread-bot-only")
        self.assertFalse(second)


if __name__ == "__main__":
    unittest.main()
