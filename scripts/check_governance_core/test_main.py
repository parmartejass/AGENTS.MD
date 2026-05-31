from __future__ import annotations

import contextlib
import importlib.util
import io
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


SCRIPT_ROOT = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_ROOT.parents[1]


def _load_module(module_name: str, module_path: Path):
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module from {module_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


if str(SCRIPT_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPT_ROOT))

from _test_helpers import write_text

CHANGE_RECORDS = _load_module("check_governance_core_change_records", SCRIPT_ROOT / "_change_records.py")
GOVERNANCE_RESEARCH = _load_module(
    "governance_autoresearch",
    REPO_ROOT / "X-Bookmarks Import/skills/governance-autoresearch/scripts/governance_research.py",
)

ACTIVE_RESEARCH_FILES = (
    "docs/agents/mcp/00-mcp-standards/mcp-standards.md",
    "docs/agents/platforms/00-platform-runtime-standards/platform-runtime-standards.md",
)


class ChangeRecordReferenceTests(unittest.TestCase):
    def test_readme_checks_reference_resolves_through_existing_readme(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = Path(tmp_dir)
            write_text(repo_root / "README.md", "# Checks\n")

            self.assertTrue(CHANGE_RECORDS._reference_target_exists(repo_root, "README.md#checks"))
            self.assertTrue(CHANGE_RECORDS._reference_target_exists(repo_root, ".governance/README.md#checks"))

    def test_readme_checks_reference_does_not_mask_missing_readme(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = Path(tmp_dir)

            self.assertFalse(CHANGE_RECORDS._reference_target_exists(repo_root, "README.md#checks"))

    def test_invalid_reference_targets_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = Path(tmp_dir)
            write_text(repo_root / "README.md", "# Checks\n")

            self.assertFalse(CHANGE_RECORDS._reference_target_exists(repo_root, "../README.md#checks"))
            self.assertFalse(CHANGE_RECORDS._reference_target_exists(repo_root, "/README.md#checks"))


class GovernanceResearchTests(unittest.TestCase):
    def test_governance_files_all_exist(self) -> None:
        missing_files = [
            rel_path
            for rel_path in GOVERNANCE_RESEARCH.GOVERNANCE_FILES
            if not (REPO_ROOT / rel_path).is_file()
        ]

        self.assertEqual([], missing_files)

    def test_active_runtime_authorities_have_curated_topics(self) -> None:
        for rel_path in ACTIVE_RESEARCH_FILES:
            with self.subTest(rel_path=rel_path):
                self.assertIn(rel_path, GOVERNANCE_RESEARCH.GOVERNANCE_FILES)
                self.assertIn(rel_path, GOVERNANCE_RESEARCH.FILE_TOPIC_MAP)
                self.assertEqual(
                    GOVERNANCE_RESEARCH.FILE_TOPIC_MAP[rel_path],
                    GOVERNANCE_RESEARCH.extract_topics(rel_path),
                )

    def test_list_surface_includes_active_runtime_authorities(self) -> None:
        with patch.object(sys, "argv", ["governance_research.py", "--list"]):
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                GOVERNANCE_RESEARCH.main()

        output = stdout.getvalue()
        for rel_path in ACTIVE_RESEARCH_FILES:
            with self.subTest(rel_path=rel_path):
                self.assertIn(f"[OK] {rel_path}", output)

    def test_list_surface_reports_registered_missing_files(self) -> None:
        missing_file = "docs/agents/missing-active-topic.md"
        with (
            patch.object(GOVERNANCE_RESEARCH, "GOVERNANCE_FILES", [missing_file]),
            patch.dict(GOVERNANCE_RESEARCH.FILE_TOPIC_MAP, {missing_file: ["missing topic"]}, clear=True),
            patch.object(sys, "argv", ["governance_research.py", "--list"]),
        ):
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                GOVERNANCE_RESEARCH.main()

        output = stdout.getvalue()
        self.assertIn(f"[MISSING] {missing_file}", output)
        self.assertIn("Topics: missing topic", output)


if __name__ == "__main__":
    unittest.main()
