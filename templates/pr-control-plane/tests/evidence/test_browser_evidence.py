from __future__ import annotations

import datetime as dt
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from common import load_contract  # noqa: E402
from validate_browser_evidence import evaluate_browser_evidence  # noqa: E402


FIXTURES = ROOT / "tests" / "fixtures"


def _load_fixture(name: str):
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


class BrowserEvidenceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.contract = load_contract(str(ROOT / "control-plane.contract.json"))
        self.now = dt.datetime(2026, 1, 1, 1, 0, 0, tzinfo=dt.timezone.utc)

    def test_required_high_risk_valid_manifest_passes(self) -> None:
        result = evaluate_browser_evidence(
            contract=self.contract,
            head_sha="abc123",
            changed_files=_load_fixture("changed_files_high.json"),
            manifest=_load_fixture("browser_evidence_valid.json"),
            now=self.now,
        )
        self.assertEqual(result["result"], "SUCCESS")
        self.assertTrue(result["required"])

    def test_stale_manifest_fails_when_required(self) -> None:
        result = evaluate_browser_evidence(
            contract=self.contract,
            head_sha="abc123",
            changed_files=_load_fixture("changed_files_high.json"),
            manifest=_load_fixture("browser_evidence_stale.json"),
            now=self.now,
        )
        self.assertEqual(result["result"], "FAILURE")
        self.assertTrue(any(item["code"] == "EVIDENCE_STALE" for item in result["failures"]))

    def test_low_risk_change_skips_evidence_requirement(self) -> None:
        result = evaluate_browser_evidence(
            contract=self.contract,
            head_sha="abc123",
            changed_files=_load_fixture("changed_files_low.json"),
            manifest=None,
            now=self.now,
        )
        self.assertEqual(result["result"], "SUCCESS")
        self.assertFalse(result["required"])


if __name__ == "__main__":
    unittest.main()
