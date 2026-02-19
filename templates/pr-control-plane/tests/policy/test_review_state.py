from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from check_review_state import evaluate_review_state  # noqa: E402
from common import load_contract  # noqa: E402


FIXTURES = ROOT / "tests" / "fixtures"


def _load_fixture(name: str):
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


class ReviewStateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.contract = load_contract(str(ROOT / "control-plane.contract.json"))

    def test_clean_review_and_no_findings_passes(self) -> None:
        result = evaluate_review_state(
            contract=self.contract,
            head_sha="abc123",
            review_run=_load_fixture("review_run_clean.json"),
            findings=_load_fixture("findings_clean.json"),
            timed_out=False,
        )
        self.assertEqual(result["result"], "SUCCESS")

    def test_stale_review_run_fails(self) -> None:
        result = evaluate_review_state(
            contract=self.contract,
            head_sha="abc123",
            review_run=_load_fixture("review_run_stale.json"),
            findings=_load_fixture("findings_clean.json"),
            timed_out=False,
        )
        self.assertEqual(result["result"], "FAILURE")
        self.assertTrue(any(item["code"] == "STALE_REVIEW_RUN" for item in result["failures"]))

    def test_actionable_findings_fail(self) -> None:
        result = evaluate_review_state(
            contract=self.contract,
            head_sha="abc123",
            review_run=_load_fixture("review_run_clean.json"),
            findings=_load_fixture("findings_actionable.json"),
            timed_out=False,
        )
        self.assertEqual(result["result"], "FAILURE")
        self.assertTrue(any(item["code"] == "ACTIONABLE_FINDINGS_PRESENT" for item in result["failures"]))

    def test_timeout_is_a_failure(self) -> None:
        result = evaluate_review_state(
            contract=self.contract,
            head_sha="abc123",
            review_run=_load_fixture("review_run_clean.json"),
            findings=_load_fixture("findings_clean.json"),
            timed_out=True,
        )
        self.assertEqual(result["result"], "FAILURE")
        self.assertTrue(any(item["code"] == "REVIEW_TIMEOUT" for item in result["failures"]))


if __name__ == "__main__":
    unittest.main()
