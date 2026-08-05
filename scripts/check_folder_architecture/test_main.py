from __future__ import annotations

import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import textwrap
import unittest
from contextlib import contextmanager
from pathlib import Path
from uuid import uuid4


SCRIPT_ROOT = Path(__file__).resolve().parent
MODULE_PATH = SCRIPT_ROOT / "check_folder_architecture_main.py"
if str(SCRIPT_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPT_ROOT))

SPEC = importlib.util.spec_from_file_location("check_folder_architecture_main", MODULE_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"Unable to load checker module from {MODULE_PATH}")

MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)

check_governance_owned_contracts = MODULE._check_governance_owned_contracts
iter_repo_python_files = MODULE._iter_repo_python_files
load_scope_manifest = MODULE._load_scope_manifest
python_entrypoint_filename = MODULE.python_entrypoint_filename
TMP_ROOT = Path(tempfile.gettempdir()) / "agents-md-check-folder-architecture-tests"


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    rendered = textwrap.dedent(content).lstrip("\n")
    with path.open("w", encoding="utf-8", newline="") as handle:
        handle.write(rendered)


@contextmanager
def _temporary_workspace():
    TMP_ROOT.mkdir(parents=True, exist_ok=True)
    tmp_root = TMP_ROOT / uuid4().hex
    tmp_root.mkdir(parents=True, exist_ok=False)
    try:
        yield tmp_root
    finally:
        shutil.rmtree(tmp_root, ignore_errors=True)


def _write_minimal_governance_tree(governance_root: Path) -> None:
    _write(
        governance_root / "scripts/check_folder_architecture/scope.json",
        json.dumps(
            {
                "version": 1,
                "python_roots": [
                    {
                        "path": "scripts",
                        "enforcement_mode": "enforce",
                        "owner": "scripts/check_folder_architecture/check_folder_architecture_main.py",
                    },
                ],
            },
            indent=2,
        )
        + "\n",
    )
    for rel_path in (
        "scripts/check_docs_router_contract/check_docs_router_contract_main.py",
        "scripts/check_folder_architecture/check_folder_architecture_main.py",
        "scripts/check_governance_core/check_governance_core_main.py",
        "scripts/check_python_safety/check_python_safety_main.py",
    ):
        _write(governance_root / rel_path, "from __future__ import annotations\n")

class FolderArchitectureBoundaryTests(unittest.TestCase):
    @unittest.skipIf(shutil.which("git") is None, "git is not available in PATH.")
    def test_git_enumeration_skips_deleted_tracked_python_files(self) -> None:
        with _temporary_workspace() as repo_root:
            subprocess.run(["git", "init"], cwd=repo_root, check=True, capture_output=True, text=True, timeout=10)
            tracked_file = repo_root / "scripts/deleted/deleted_main.py"
            _write(tracked_file, "from __future__ import annotations\n")
            subprocess.run(["git", "add", str(tracked_file)], cwd=repo_root, check=True, capture_output=True, text=True, timeout=10)
            tracked_file.unlink()

            issues = []
            python_files = iter_repo_python_files(repo_root, issues)

            self.assertEqual([], issues)
            self.assertNotIn(tracked_file, python_files)

    @unittest.skipIf(shutil.which("git") is None, "git is not available in PATH.")
    def test_git_enumeration_skips_deleted_tracked_python_file_replaced_by_directory(self) -> None:
        with _temporary_workspace() as repo_root:
            subprocess.run(["git", "init"], cwd=repo_root, check=True, capture_output=True, text=True, timeout=10)
            tracked_path = repo_root / "scripts/replaced/replaced_main.py"
            _write(tracked_path, "from __future__ import annotations\n")
            subprocess.run(["git", "add", str(tracked_path)], cwd=repo_root, check=True, capture_output=True, text=True, timeout=10)
            tracked_path.unlink()
            tracked_path.mkdir()

            issues = []
            python_files = iter_repo_python_files(repo_root, issues)

            self.assertEqual([], issues)
            self.assertNotIn(tracked_path, python_files)

    def test_scope_manifest_rejects_drive_qualified_paths(self) -> None:
        with _temporary_workspace() as governance_root:
            _write(
                governance_root / "scripts/check_folder_architecture/scope.json",
                """
                {
                  "version": 1,
                  "python_roots": [
                    {
                      "path": "C:/repo/scripts",
                      "enforcement_mode": "enforce",
                      "owner": "scripts/check_folder_architecture/check_folder_architecture_main.py"
                    }
                  ]
                }
                """,
            )

            issues = []
            roots = load_scope_manifest(governance_root, issues)

            self.assertEqual([], roots)
            self.assertTrue(
                any("drive-qualified" in issue.message for issue in issues),
                issues,
            )

    def test_scope_manifest_rejects_rooted_paths(self) -> None:
        with _temporary_workspace() as governance_root:
            _write(
                governance_root / "scripts/check_folder_architecture/scope.json",
                """
                {
                  "version": 1,
                  "python_roots": [
                    {
                      "path": "/scripts",
                      "enforcement_mode": "enforce",
                      "owner": "scripts/check_folder_architecture/check_folder_architecture_main.py"
                    }
                  ]
                }
                """,
            )

            issues = []
            roots = load_scope_manifest(governance_root, issues)

            self.assertEqual([], roots)
            self.assertTrue(
                any("repo-relative, not rooted" in issue.message for issue in issues),
                issues,
            )

    def test_python_entrypoint_filename_uses_direct_contract(self) -> None:
        self.assertEqual("billing_main.py", python_entrypoint_filename("billing"))

    def test_discovered_script_feature_requires_main_entrypoint(self) -> None:
        with _temporary_workspace() as repo_root:
            _write_minimal_governance_tree(repo_root)
            _write(repo_root / "scripts/reporting/helper.py", "from __future__ import annotations\n")
            _write(
                repo_root / "docs/project/architecture/architecture.md",
                f"# Architecture\n\n- {MODULE.SCOPE_MANIFEST_PATH}\n",
            )

            issues = []
            check_governance_owned_contracts(repo_root, repo_root, issues)

            self.assertTrue(
                any(issue.path == "scripts/reporting/reporting_main.py" for issue in issues),
                issues,
            )

    def test_discovered_script_feature_passes_with_main_entrypoint(self) -> None:
        with _temporary_workspace() as repo_root:
            _write_minimal_governance_tree(repo_root)
            _write(repo_root / "scripts/reporting/reporting_main.py", "from __future__ import annotations\n")
            _write(
                repo_root / "docs/project/architecture/architecture.md",
                f"# Architecture\n\n- {MODULE.SCOPE_MANIFEST_PATH}\n",
            )

            issues = []
            check_governance_owned_contracts(repo_root, repo_root, issues)

            self.assertEqual([], issues)

    def test_script_feature_discovery_is_direct_child_only(self) -> None:
        with _temporary_workspace() as repo_root:
            _write_minimal_governance_tree(repo_root)
            _write(repo_root / "scripts/reporting/reporting_main.py", "from __future__ import annotations\n")
            _write(repo_root / "scripts/reporting/nested/helper.py", "from __future__ import annotations\n")
            _write(
                repo_root / "docs/project/architecture/architecture.md",
                f"# Architecture\n\n- {MODULE.SCOPE_MANIFEST_PATH}\n",
            )

            issues = []
            check_governance_owned_contracts(repo_root, repo_root, issues)

            self.assertFalse(
                any(issue.path == "scripts/reporting/nested/nested_main.py" for issue in issues),
                issues,
            )

    def test_vendored_mode_ignores_host_python_files(self) -> None:
        with _temporary_workspace() as tmp_root:
            repo_root = tmp_root / "host"
            governance_root = tmp_root / "host/.governance"
            _write_minimal_governance_tree(governance_root)
            _write(repo_root / "app.py", "print('host file')\n")

            issues = []
            check_governance_owned_contracts(repo_root, governance_root, issues)

            self.assertEqual([], issues)

    def test_vendored_mode_still_flags_governance_python_outside_scope(self) -> None:
        with _temporary_workspace() as tmp_root:
            repo_root = tmp_root / "host"
            governance_root = tmp_root / "host/.governance"
            _write_minimal_governance_tree(governance_root)
            _write(repo_root / "app.py", "print('host file')\n")
            _write(governance_root / "rogue.py", "print('rogue')\n")

            issues = []
            check_governance_owned_contracts(repo_root, governance_root, issues)
            paths = {issue.path for issue in issues}

            self.assertIn("rogue.py", paths)
            self.assertNotIn("app.py", paths)

    def test_non_git_enumeration_ignores_generated_and_environment_paths(self) -> None:
        with _temporary_workspace() as repo_root:
            _write_minimal_governance_tree(repo_root)
            _write(
                repo_root / "docs/project/architecture/architecture.md",
                f"# Architecture\n\n- {MODULE.SCOPE_MANIFEST_PATH}\n",
            )
            _write(repo_root / ".tmp-test-workspaces/generated.py", "print('generated')\n")
            _write(repo_root / "venv/generated.py", "print('venv')\n")
            _write(repo_root / ".venv/generated.py", "print('dot venv')\n")
            _write(repo_root / "__pycache__/generated.py", "print('cache')\n")

            issues = []
            check_governance_owned_contracts(repo_root, repo_root, issues)

            self.assertEqual([], issues)

    def test_source_repo_mode_keeps_scope_manifest_reference_check(self) -> None:
        with _temporary_workspace() as repo_root:
            _write_minimal_governance_tree(repo_root)
            _write(
                repo_root / "docs/project/architecture/architecture.md",
                """
                # Architecture

                - Entrypoints live here.
                """,
            )

            issues = []
            check_governance_owned_contracts(repo_root, repo_root, issues)

            self.assertTrue(
                any(issue.path == "docs/project/architecture/architecture.md" for issue in issues),
                issues,
            )


if __name__ == "__main__":
    unittest.main()
