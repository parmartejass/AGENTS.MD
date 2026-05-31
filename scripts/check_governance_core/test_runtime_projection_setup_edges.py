from __future__ import annotations

import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path

from _test_helpers import run_powershell_script, write_text
from test_wrappers import POWERSHELL, PYTHON_EXE, REPO_ROOT, _write_minimal_runtime_projection_governance


def _add_skill_runtime_projection(governance_root: Path) -> None:
    write_text(governance_root / "docs/agents/skills/x-api-data-access/SKILL.md", "# Test skill\n")
    manifest_path = governance_root / "docs/agents/platforms/runtime-projections.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["asset_classes"]["skills"] = [
        {
            "id": "claude-project-skills",
            "platform": "claude-code",
            "support_level": "official",
            "projection_mode": "child_directory_links",
            "scope": "project",
            "source_root": "docs/agents/skills",
            "target_root": ".claude/skills",
            "default_enabled": True,
        }
    ]
    write_text(manifest_path, json.dumps(manifest, indent=2) + "\n")


@unittest.skipIf(POWERSHELL is None, "PowerShell is not available in PATH.")
class RuntimeProjectionSetupEdgeTests(unittest.TestCase):
    def test_platform_setup_rejects_invalid_runtime_projection_manifest_before_writes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            host_root = Path(tmp_dir) / "host repo"
            governance_root = host_root / ".governance"
            _write_minimal_runtime_projection_governance(governance_root)
            write_text(
                governance_root / "docs/agents/platforms/runtime-projections.json",
                json.dumps({"asset_classes": {"skills": [], "mcp": [], "settings": [], "acp": []}}, indent=2) + "\n",
            )

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
            self.assertNotEqual(result.returncode, 0, combined)
            self.assertIn("FAILED_VALIDATION: runtime projection manifest contract invalid", combined)
            self.assertIn("Runtime projection manifest missing top-level field 'version'", combined)
            self.assertFalse((host_root / ".codex/config.toml").exists(), combined)

    def test_platform_setup_repairs_plain_directory_stubs_through_wrapper(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            host_root = Path(tmp_dir) / "host repo"
            governance_root = host_root / ".governance"
            _write_minimal_runtime_projection_governance(governance_root)
            _add_skill_runtime_projection(governance_root)
            stub_path = host_root / ".claude/skills/x-api-data-access"
            write_text(stub_path, "../../.governance/docs/agents/skills/x-api-data-access\n")

            result = run_powershell_script(
                POWERSHELL,
                governance_root / "scripts/setup_repo_platform_assets.ps1",
                "-Force",
                "-RepairPlainDirectoryStubs",
                "-PythonExe",
                PYTHON_EXE,
                "-RepoRoot",
                str(host_root),
                cwd=host_root,
            )

            combined = result.stdout + result.stderr
            self.assertEqual(result.returncode, 0, combined)
            self.assertTrue(stub_path.exists(), combined)
            self.assertTrue(stub_path.is_dir(), combined)

    def test_settings_link_helper_accepts_python_exe_for_toml_validation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            host_root = Path(tmp_dir) / "host repo"
            governance_root = host_root / ".governance"
            _write_minimal_runtime_projection_governance(governance_root)
            shutil.copy2(
                REPO_ROOT / "docs/agents/settings/link_settings.ps1",
                governance_root / "docs/agents/settings/link_settings.ps1",
            )

            result = run_powershell_script(
                POWERSHELL,
                governance_root / "docs/agents/settings/link_settings.ps1",
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
            self.assertTrue((host_root / ".codex/config.toml").exists(), combined)


if __name__ == "__main__":
    unittest.main()
