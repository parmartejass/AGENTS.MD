from __future__ import annotations

import io
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import scripts.check_governance_core as GOVERNANCE_CORE
from scripts.check_governance_core._test_support import REPOSITORY_ROOT, write


PACKAGE = GOVERNANCE_CORE.__name__
LAUNCH_TIMEOUT_SECONDS = 120
README_BASE = "# Fixture\n\nAGENTS.md docs/project/project_index.md\n\n## Checks\n"


def launch(*arguments: str) -> subprocess.CompletedProcess[str]:
    """Run the package launcher in a fresh interpreter from the governance root."""

    return subprocess.run(
        [sys.executable, "-B", "-m", PACKAGE, *arguments],
        cwd=REPOSITORY_ROOT,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
        capture_output=True,
        text=True,
        timeout=LAUNCH_TIMEOUT_SECONDS,
    )


def project_docs_result(readme: str) -> dict:
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        shutil.copytree(REPOSITORY_ROOT / "docs", root / "docs")
        write(root / "README.md", readme)
        return GOVERNANCE_CORE.run_checks(
            {"repo_root": str(root), "governance_root": str(root), "mode": "project_docs"}
        )


class GovernanceCoreCliContractTests(unittest.TestCase):
    def _assert_retired_option_rejected(self, option: str) -> None:
        stderr = io.StringIO()
        with patch.object(sys, "stderr", stderr):
            with self.assertRaises(SystemExit) as raised:
                GOVERNANCE_CORE.main([option])

        self.assertEqual(2, raised.exception.code)
        self.assertIn(f"unrecognized arguments: {option}", stderr.getvalue())

    def test_retired_runtime_projection_option_is_rejected(self) -> None:
        self._assert_retired_option_rejected("--only-runtime-projection")

    def test_retired_success_marker_option_is_rejected(self) -> None:
        self._assert_retired_option_rejected("--success-marker")

    def test_public_members_are_exactly_the_declared_api(self) -> None:
        self.assertEqual(["main", "resolve_documents", "run_checks"], sorted(GOVERNANCE_CORE.__all__))
        self.assertTrue(all(callable(getattr(GOVERNANCE_CORE, name)) for name in GOVERNANCE_CORE.__all__))


class ModuleLauncherTests(unittest.TestCase):
    def test_module_launcher_runs_the_public_entrypoint(self) -> None:
        result = launch("--only-docs-ssot", "--repo-root", ".", "--governance-root", ".")
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("Governance core: PASSED", result.stdout)

    def test_module_launcher_rejects_a_retired_option(self) -> None:
        result = launch("--only-runtime-projection")
        self.assertEqual(2, result.returncode, result.stdout + result.stderr)
        self.assertIn("unrecognized arguments: --only-runtime-projection", result.stderr)


class ReadmeLauncherReferenceTests(unittest.TestCase):
    def test_module_launcher_reference_satisfies_project_docs(self) -> None:
        result = project_docs_result(README_BASE + f"From `.governance/`: `python3 -B -m {PACKAGE} --repo-root ..`\n")
        self.assertEqual("PASSED", result["status"], result)

    def test_retired_and_lookalike_references_fail(self) -> None:
        for line in (
            "python3 -B .governance/scripts/check_governance_core/check_governance_core_main.py --repo-root .\n",
            "`scripts.check_governance_core.check_governance_core_main` is the API.\n",
            f"python3 -B -m {PACKAGE}_extra\n",
            f"python3 -B -m {PACKAGE}.private_module\n",
        ):
            with self.subTest(line=line):
                result = project_docs_result(README_BASE + line)
                self.assertEqual("FAILED", result["status"], result)
                self.assertTrue(any("governance-core launcher" in error for error in result["errors"]), result)


if __name__ == "__main__":
    unittest.main()
