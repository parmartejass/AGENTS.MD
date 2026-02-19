from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from common import load_contract  # noqa: E402
from risk_policy_gate import evaluate_policy  # noqa: E402


FIXTURES = ROOT / "tests" / "fixtures"


def _load_fixture(name: str):
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


class RiskPolicyGateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.contract = load_contract(str(ROOT / "control-plane.contract.json"))

    def test_high_risk_with_all_required_checks_passes(self) -> None:
        result = evaluate_policy(
            contract=self.contract,
            changed_files=_load_fixture("changed_files_high.json"),
            check_runs=_load_fixture("check_runs_success.json"),
            head_sha="abc123",
        )
        self.assertEqual(result["riskTier"], "high")
        self.assertEqual(result["result"], "SUCCESS")

    def test_missing_required_check_fails(self) -> None:
        result = evaluate_policy(
            contract=self.contract,
            changed_files=_load_fixture("changed_files_high.json"),
            check_runs=_load_fixture("check_runs_missing_browser.json"),
            head_sha="abc123",
        )
        self.assertEqual(result["result"], "FAILURE")
        self.assertTrue(any(item["code"] == "MISSING_REQUIRED_CHECK" for item in result["failures"]))

    def test_docs_drift_rule_fails_when_required_docs_missing(self) -> None:
        changed_files = [
            ".github/workflows/risk-policy-gate.yml",
            "automation/pr-control-plane/scripts/risk_policy_gate.py",
        ]
        result = evaluate_policy(
            contract=self.contract,
            changed_files=changed_files,
            check_runs=None,
            head_sha=None,
        )
        self.assertEqual(result["result"], "FAILURE")
        self.assertTrue(any(item["code"] == "DOCS_DRIFT_REQUIRED_DOCS_MISSING" for item in result["failures"]))


if __name__ == "__main__":
    unittest.main()
