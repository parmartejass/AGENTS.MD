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
            self.assertIn("runtime projection manifest validator failed", combined)
            self.assertIn("Runtime projection manifest missing top-level field 'version'", combined)
            self.assertFalse((host_root / ".codex/config.toml").exists(), combined)

    def test_platform_setup_rejects_retired_compatibility_support_level(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            host_root = Path(tmp_dir) / "host repo"
            governance_root = host_root / ".governance"
            _write_minimal_runtime_projection_governance(governance_root)
            manifest_path = governance_root / "docs/agents/platforms/runtime-projections.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["support_levels"].append("compatibility")
            write_text(manifest_path, json.dumps(manifest, indent=2) + "\n")

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
            self.assertIn("support_levels contains unsupported values", combined)
            self.assertIn("compatibility", combined)
            self.assertFalse((host_root / ".codex/config.toml").exists(), combined)

    def test_platform_setup_rejects_retired_include_compatibility_flag(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            host_root = Path(tmp_dir) / "host repo"
            governance_root = host_root / ".governance"
            _write_minimal_runtime_projection_governance(governance_root)

            result = run_powershell_script(
                POWERSHELL,
                governance_root / "scripts/setup_repo_platform_assets.ps1",
                "-Force",
                "-IncludeCompatibility",
                "-PythonExe",
                PYTHON_EXE,
                "-RepoRoot",
                str(host_root),
                cwd=host_root,
            )

            combined = result.stdout + result.stderr
            self.assertNotEqual(result.returncode, 0, combined)
            self.assertIn("IncludeCompatibility", combined)
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

    def test_mcp_link_helper_ignores_unselected_settings_content_errors(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            host_root = Path(tmp_dir) / "host repo"
            governance_root = host_root / ".governance"
            _write_minimal_runtime_projection_governance(governance_root)
            (governance_root / "docs/agents/mcp").mkdir(parents=True, exist_ok=True)
            shutil.copy2(
                REPO_ROOT / "docs/agents/mcp/link_mcp.ps1",
                governance_root / "docs/agents/mcp/link_mcp.ps1",
            )
            write_text(governance_root / "docs/agents/mcp/shared/mcp.json", '{"mcpServers": {}}\n')
            write_text(governance_root / "docs/agents/settings/codex/config.toml", "invalid = [\n")

            manifest_path = governance_root / "docs/agents/platforms/runtime-projections.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["asset_classes"]["mcp"] = [
                {
                    "id": "claude-project-mcp",
                    "platform": "claude-code",
                    "support_level": "official",
                    "projection_mode": "mcp_file_link",
                    "scope": "project",
                    "source_preference": ["docs/agents/mcp/shared/mcp.json"],
                    "target_path": ".mcp.json",
                    "default_enabled": True,
                }
            ]
            write_text(manifest_path, json.dumps(manifest, indent=2) + "\n")

            result = run_powershell_script(
                POWERSHELL,
                governance_root / "docs/agents/mcp/link_mcp.ps1",
                "-Force",
                "-PythonExe",
                PYTHON_EXE,
                "-RepoRoot",
                str(host_root),
                cwd=host_root,
            )

            combined = result.stdout + result.stderr
            self.assertEqual(result.returncode, 0, combined)
            self.assertNotIn("Invalid TOML", combined)
            self.assertTrue((host_root / ".mcp.json").exists(), combined)

    def test_settings_link_helper_rejects_selected_settings_content_errors(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            host_root = Path(tmp_dir) / "host repo"
            governance_root = host_root / ".governance"
            _write_minimal_runtime_projection_governance(governance_root)
            shutil.copy2(
                REPO_ROOT / "docs/agents/settings/link_settings.ps1",
                governance_root / "docs/agents/settings/link_settings.ps1",
            )
            write_text(governance_root / "docs/agents/settings/codex/config.toml", "invalid = [\n")

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
            self.assertNotEqual(result.returncode, 0, combined)
            self.assertIn("Failed to parse TOML file", combined)
            self.assertFalse((host_root / ".codex/config.toml").exists(), combined)


if __name__ == "__main__":
    unittest.main()
