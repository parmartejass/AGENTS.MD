from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "scripts/main.py", *args],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
        timeout=30,
    )


class MainCliTests(unittest.TestCase):
    def test_check_review_state_success_via_parent_contract(self) -> None:
        result = _run_cli(
            "check-review-state",
            "--contract",
            "control-plane.contract.json",
            "--head-sha",
            "abc123",
            "--review-runs-json",
            '[{"name":"Code Review Agent","head_sha":"abc123","status":"completed","conclusion":"success","summary":"clean"}]',
            "--findings-json",
            "tests/fixtures/findings_clean.json",
            "--output-json",
            "-",
        )
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["result"], "SUCCESS")

    def test_risk_policy_gate_requires_head_sha_when_check_runs_are_supplied(self) -> None:
        result = _run_cli(
            "risk-policy-gate",
            "--contract",
            "control-plane.contract.json",
            "--changed-files-json",
            "tests/fixtures/changed_files_high.json",
            "--check-runs-json",
            "tests/fixtures/check_runs_success.json",
            "--output-json",
            "-",
        )
        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["reason"], "INPUTERROR")

    def test_validate_browser_evidence_low_risk_skips_cleanly(self) -> None:
        result = _run_cli(
            "validate-browser-evidence",
            "--contract",
            "control-plane.contract.json",
            "--head-sha",
            "abc123",
            "--changed-files-json",
            "tests/fixtures/changed_files_low.json",
            "--output-json",
            "-",
        )
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["result"], "SUCCESS")
        self.assertFalse(payload["required"])


if __name__ == "__main__":
    unittest.main()
