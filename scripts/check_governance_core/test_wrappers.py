from __future__ import annotations

import json
import os
import shutil
import sys
import tempfile
import time
import unittest
from pathlib import Path

from _test_helpers import copy_vendored_governance_for_wrappers, run_powershell_script, write_text


SCRIPT_ROOT = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_ROOT.parents[1]
POWERSHELL = shutil.which("powershell") or shutil.which("pwsh")
PYTHON_EXE = sys.executable


def _write_fake_python_noop(path: Path) -> None:
    if os.name == "nt":
        write_text(path, "@echo off\r\necho 3.11.0\r\nexit /b 0\r\n")
        return
    write_text(path, "#!/bin/sh\necho 3.11.0\nexit 0\n")
    path.chmod(0o755)


def _write_fake_python_version(path: Path, version: str) -> None:
    if os.name == "nt":
        write_text(path, f"@echo off\r\necho {version}\r\n")
        return
    write_text(path, f"#!/bin/sh\necho {version}\n")
    path.chmod(0o755)


def _write_minimal_runtime_projection_governance(governance_root: Path) -> None:
    write_text(governance_root / "AGENTS.md", "# Test governance\n")
    write_text(governance_root / "agents-manifest.yaml", "default_inject:\n  - AGENTS.md\n")
    (governance_root / "scripts").mkdir(parents=True, exist_ok=True)
    shutil.copy2(REPO_ROOT / "scripts/_python_check_runner.ps1", governance_root / "scripts/_python_check_runner.ps1")
    shutil.copy2(REPO_ROOT / "scripts/setup_repo_platform_assets.ps1", governance_root / "scripts/setup_repo_platform_assets.ps1")
    shutil.copytree(
        REPO_ROOT / "scripts/check_governance_core",
        governance_root / "scripts/check_governance_core",
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
    )
    write_text(governance_root / "docs/agents/settings/codex/config.toml", 'model = "test"\n')
    manifest = {
        "version": 1,
        "ssot_owner": "docs/agents/platforms/runtime-projections.json",
        "update_trigger": "test fixture",
        "support_levels": ["official", "manual", "unsupported", "reserved"],
        "path_resolution": {
            "source_root": "governance root",
            "source_path": "governance root",
            "source_preference": "governance root",
            "target_root": "repo root",
            "target_path": "repo root",
        },
        "asset_classes": {
            "skills": [],
            "mcp": [],
            "settings": [
                {
                    "id": "codex-project-config",
                    "platform": "codex",
                    "support_level": "official",
                    "projection_mode": "settings_file_link",
                    "scope": "project",
                    "source_path": "docs/agents/settings/codex/config.toml",
                    "target_path": ".codex/config.toml",
                    "default_enabled": True,
                }
            ],
            "acp": [],
        },
    }
    write_text(governance_root / "docs/agents/platforms/runtime-projections.json", json.dumps(manifest, indent=2) + "\n")
    shutil.copy2(REPO_ROOT / "docs/agents/link_repo_assets.ps1", governance_root / "docs/agents/link_repo_assets.ps1")


@unittest.skipIf(POWERSHELL is None, "PowerShell is not available in PATH.")
class GovernanceWrapperTests(unittest.TestCase):
    def test_asset_wrappers_pass_python_exe_to_python_backed_linker(self) -> None:
        for wrapper_rel in (
            "docs/agents/mcp/link_mcp.ps1",
            "docs/agents/settings/link_settings.ps1",
            "docs/agents/skills/link_skills.ps1",
        ):
            with self.subTest(wrapper_rel=wrapper_rel):
                text = (REPO_ROOT / wrapper_rel).read_text(encoding="utf-8")
                self.assertIn("[string]$PythonExe", text)
                self.assertIn("-PythonExe $PythonExe", text)
                self.assertNotIn("IncludeCompatibility", text)

    def test_wrappers_reject_noop_python_that_does_not_run_validator(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            fake_python = Path(tmp_dir) / ("python-noop.cmd" if os.name == "nt" else "python-noop")
            _write_fake_python_noop(fake_python)

            for wrapper_name in ("check_docs_ssot.ps1", "check_project_docs.ps1"):
                with self.subTest(wrapper_name=wrapper_name):
                    result = run_powershell_script(
                        POWERSHELL,
                        REPO_ROOT / "scripts" / wrapper_name,
                        "-PythonExe",
                        str(fake_python),
                        cwd=REPO_ROOT,
                    )

                    combined = result.stdout + result.stderr
                    self.assertNotEqual(result.returncode, 0, combined)
                    self.assertIn("expected success marker", combined)

    def test_platform_setup_accepts_python_exe_for_toml_validation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            host_root = Path(tmp_dir) / "host repo"
            governance_root = host_root / ".governance"
            _write_minimal_runtime_projection_governance(governance_root)

            result = run_powershell_script(
                POWERSHELL,
                governance_root / "scripts/setup_repo_platform_assets.ps1",
                "-Force",
                "-PythonExe",
                PYTHON_EXE,
                "-RepoRoot",
                str(host_root),
                cwd=host_root,
            )

            combined = result.stdout + result.stderr
            self.assertEqual(result.returncode, 0, combined)
            self.assertIn("Python selected:", combined)
            projected_config = host_root / ".codex/config.toml"
            self.assertTrue(projected_config.exists(), combined)
            if os.name != "nt":
                self.assertTrue(projected_config.is_symlink(), combined)
                self.assertFalse(os.path.isabs(os.readlink(projected_config)), combined)

    def test_platform_setup_rejects_python_below_minimum_version(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            host_root = Path(tmp_dir) / "host repo"
            governance_root = host_root / ".governance"
            _write_minimal_runtime_projection_governance(governance_root)
            fake_python = Path(tmp_dir) / ("python310.cmd" if os.name == "nt" else "python310")
            _write_fake_python_version(fake_python, "3.10.0")

            result = run_powershell_script(
                POWERSHELL,
                governance_root / "scripts/setup_repo_platform_assets.ps1",
                "-Force",
                "-PythonExe",
                str(fake_python),
                "-RepoRoot",
                str(host_root),
                cwd=host_root,
            )

            combined = result.stdout + result.stderr
            self.assertNotEqual(result.returncode, 0, combined)
            self.assertIn("FAILED_VALIDATION: PythonExe must resolve to Python 3.11+ executable", combined)

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

    def test_vendored_target_repo_wrappers_require_explicit_repo_root(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            host_root = Path(tmp_dir) / "host repo"
            governance_root = host_root / ".governance"
            copy_vendored_governance_for_wrappers(REPO_ROOT, governance_root)

            for wrapper_name in ("check_docs_ssot.ps1", "check_project_docs.ps1"):
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


if __name__ == "__main__":
    unittest.main()
