from __future__ import annotations

import os
import shutil
import tempfile
import time
import unittest
from pathlib import Path

from _test_helpers import (
    copy_vendored_governance_for_wrappers,
    run_powershell_script,
    write_minimal_change_record,
    write_text,
)


SCRIPT_ROOT = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_ROOT.parents[1]
POWERSHELL = shutil.which("powershell")


def _write_fake_python_noop(path: Path) -> None:
    write_text(path, "@echo off\r\necho 3.11.0\r\nexit /b 0\r\n")


@unittest.skipIf(POWERSHELL is None, "PowerShell is not available in PATH.")
class ChangeRecordWrapperTests(unittest.TestCase):
    def test_wrapper_runs_only_change_record_checks(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = Path(tmp_dir)
            write_minimal_change_record(repo_root)

            result = run_powershell_script(
                POWERSHELL,
                REPO_ROOT / "scripts/check_change_records.ps1",
                "-RepoRoot",
                str(repo_root),
                "-RequireRecords",
                cwd=REPO_ROOT,
            )

            combined = result.stdout + result.stderr
            self.assertEqual(result.returncode, 0, combined)
            self.assertIn("Python selected:", combined)
            self.assertIn("Change record checks passed", combined)
            self.assertNotIn("Agents manifest checks passed", combined)
            self.assertNotIn("Docs SSOT checks passed", combined)

    def test_wrapper_accepts_trailing_backslash_repo_root(self) -> None:
        result = run_powershell_script(
            POWERSHELL,
            REPO_ROOT / "scripts/check_change_records.ps1",
            "-RepoRoot",
            ".\\",
            "-RequireRecords",
            cwd=REPO_ROOT,
        )

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_wrapper_rejects_missing_repo_root_with_explicit_validation(self) -> None:
        result = run_powershell_script(
            POWERSHELL,
            REPO_ROOT / "scripts/check_change_records.ps1",
            "-RepoRoot",
            str(REPO_ROOT / ".missing-change-record-wrapper-root"),
            cwd=REPO_ROOT,
        )

        combined = result.stdout + result.stderr
        self.assertNotEqual(result.returncode, 0, combined)
        self.assertIn("FAILED_VALIDATION: RepoRoot does not exist", combined)

    def test_wrapper_rejects_missing_python_exe_with_explicit_validation(self) -> None:
        result = run_powershell_script(
            POWERSHELL,
            REPO_ROOT / "scripts/check_change_records.ps1",
            "-PythonExe",
            str(REPO_ROOT / ".missing-python.exe"),
            cwd=REPO_ROOT,
        )

        combined = result.stdout + result.stderr
        self.assertNotEqual(result.returncode, 0, combined)
        self.assertIn("FAILED_VALIDATION: PythonExe must resolve to Python 3.11+ executable", combined)

    def test_wrapper_rejects_python_below_minimum_version(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            fake_python = Path(tmp_dir) / "python310.cmd"
            write_text(fake_python, "@echo off\r\necho 3.10.0\r\n")

            result = run_powershell_script(
                POWERSHELL,
                REPO_ROOT / "scripts/check_change_records.ps1",
                "-PythonExe",
                str(fake_python),
                cwd=REPO_ROOT,
            )

            combined = result.stdout + result.stderr
            self.assertNotEqual(result.returncode, 0, combined)
            self.assertIn("FAILED_VALIDATION: PythonExe must resolve to Python 3.11+ executable", combined)

    def test_wrappers_reject_noop_python_that_does_not_run_validator(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            fake_python = Path(tmp_dir) / "python-noop.cmd"
            _write_fake_python_noop(fake_python)

            wrappers = (
                ("check_change_records.ps1", ("-RequireRecords",)),
                ("check_docs_ssot.ps1", ()),
                ("check_project_docs.ps1", ()),
            )
            for wrapper_name, extra_args in wrappers:
                with self.subTest(wrapper_name=wrapper_name):
                    result = run_powershell_script(
                        POWERSHELL,
                        REPO_ROOT / "scripts" / wrapper_name,
                        "-PythonExe",
                        str(fake_python),
                        *extra_args,
                        cwd=REPO_ROOT,
                    )

                    combined = result.stdout + result.stderr
                    self.assertNotEqual(result.returncode, 0, combined)
                    self.assertIn("did not emit expected success marker", combined)

    def test_wrapper_bounds_hanging_python_version_probe(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            fake_python = Path(tmp_dir) / "python-hangs.cmd"
            write_text(fake_python, "@echo off\r\nping -n 15 127.0.0.1 >nul\r\n")

            result = run_powershell_script(
                POWERSHELL,
                REPO_ROOT / "scripts/check_change_records.ps1",
                "-PythonExe",
                str(fake_python),
                cwd=REPO_ROOT,
            )

            combined = result.stdout + result.stderr
            self.assertNotEqual(result.returncode, 0, combined)
            self.assertIn("FAILED_VALIDATION: Python version probe timed out", combined)

    @unittest.skipUnless(os.name == "nt" and POWERSHELL is not None, "Windows PowerShell process-tree cleanup test.")
    def test_python_check_timeout_terminates_child_process_tree(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            child_marker = tmp_path / "child-survived.txt"
            child_script = tmp_path / "child.cmd"
            fake_python = tmp_path / "python-spawns-child.cmd"
            probe_script = tmp_path / "invoke-runner-timeout.ps1"
            write_text(
                child_script,
                f'@echo off\r\nping -n 8 127.0.0.1 >nul\r\necho survived>"{child_marker}"\r\n',
            )
            write_text(
                fake_python,
                f'@echo off\r\nif "%~1"=="-c" (\r\n  echo 3.11.0\r\n  exit /b 0\r\n)\r\nstart "" /B "{child_script}"\r\nping -n 30 127.0.0.1 >nul\r\nexit /b 0\r\n',
            )
            write_text(
                probe_script,
                f"""
$ErrorActionPreference = "Stop"
. '{REPO_ROOT / "scripts/_python_check_runner.ps1"}'
$pythonPath = Resolve-CheckPythonExecutable -RequestedPython '{fake_python}'
try {{
  Invoke-PythonCheck -PythonPath $pythonPath -Arguments @('validator.py') -WorkingDirectory '{tmp_path}' -TimeoutMilliseconds 1000 -DisplayName 'process-tree timeout test'
  Write-Host 'unexpected success'
  exit 3
}} catch {{
  $message = $_.ToString()
  Write-Host $message
  if ($message -like '*FAILED_VALIDATION: process-tree timeout test timed out*') {{
    exit 0
  }}
  exit 4
}}
""".lstrip(),
            )

            result = run_powershell_script(POWERSHELL, probe_script, cwd=REPO_ROOT, timeout=20)

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            time.sleep(10)
            self.assertFalse(child_marker.exists(), result.stdout + result.stderr)

    def test_vendored_wrapper_accepts_space_path_and_trailing_slash(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            host_root = Path(tmp_dir) / "host repo"
            governance_root = host_root / ".governance"
            write_minimal_change_record(host_root)
            copy_vendored_governance_for_wrappers(REPO_ROOT, governance_root)

            result = run_powershell_script(
                POWERSHELL,
                governance_root / "scripts/check_change_records.ps1",
                "-RepoRoot",
                ".\\",
                "-RequireRecords",
                cwd=host_root,
            )

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_vendored_target_repo_wrappers_require_explicit_repo_root(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            host_root = Path(tmp_dir) / "host repo"
            governance_root = host_root / ".governance"
            copy_vendored_governance_for_wrappers(REPO_ROOT, governance_root)

            for wrapper_name in ("check_change_records.ps1", "check_docs_ssot.ps1", "check_project_docs.ps1"):
                with self.subTest(wrapper_name=wrapper_name):
                    result = run_powershell_script(
                        POWERSHELL,
                        governance_root / "scripts" / wrapper_name,
                        cwd=host_root,
                    )

                    combined = result.stdout + result.stderr
                    self.assertNotEqual(result.returncode, 0, combined)
                    self.assertIn("FAILED_VALIDATION: RepoRoot is required", combined)

    def test_vendored_agents_manifest_wrapper_does_not_require_repo_root(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            host_root = Path(tmp_dir) / "host repo"
            governance_root = host_root / ".governance"
            copy_vendored_governance_for_wrappers(REPO_ROOT, governance_root)
            write_text(governance_root / "AGENTS.md", "# Test governance\n")
            write_text(governance_root / "docs/agents/22-ssot-authority-decisions/ssot-authority-decisions.md", "# Decisions\n")
            write_text(
                governance_root / "agents-manifest.yaml",
                'default_inject:\n  - "AGENTS.md"\nprofiles:\n  governance_improvement:\n    inject:\n      - "docs/agents/22-ssot-authority-decisions/ssot-authority-decisions.md"\n',
            )

            result = run_powershell_script(
                POWERSHELL,
                governance_root / "scripts/check_agents_manifest.ps1",
                cwd=host_root,
            )

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_wrapper_accepts_space_containing_repo_root_variants(self) -> None:
        for repo_root in (str(REPO_ROOT), f"{REPO_ROOT}\\"):
            with self.subTest(repo_root=repo_root):
                result = run_powershell_script(
                    POWERSHELL,
                    REPO_ROOT / "scripts/check_change_records.ps1",
                    "-RepoRoot",
                    repo_root,
                    "-RequireRecords",
                    cwd=REPO_ROOT,
                )

                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
