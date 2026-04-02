from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path


SCRIPT_ROOT = Path(__file__).resolve().parent
MODULE_PATH = SCRIPT_ROOT / "main.py"
SPEC = importlib.util.spec_from_file_location("check_folder_architecture_main", MODULE_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"Unable to load checker module from {MODULE_PATH}")

MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)

check_governance_owned_contracts = MODULE._check_governance_owned_contracts


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(textwrap.dedent(content).lstrip("\n"), encoding="utf-8")


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
                        "owner": "scripts/check_folder_architecture/main.py",
                    },
                    {
                        "path": "templates/python-dual-entry/myapp",
                        "enforcement_mode": "enforce",
                        "owner": "scripts/check_folder_architecture/main.py",
                    },
                    {
                        "path": "templates/pr-control-plane/scripts",
                        "enforcement_mode": "enforce",
                        "owner": "scripts/check_folder_architecture/main.py",
                    },
                ],
            },
            indent=2,
        )
        + "\n",
    )
    for rel_path in (
        "scripts/check_docs_router_contract/main.py",
        "scripts/check_folder_architecture/main.py",
        "scripts/check_governance_core/main.py",
        "scripts/check_python_safety/main.py",
        "templates/python-dual-entry/myapp/cli/main.py",
        "templates/python-dual-entry/myapp/core/main.py",
        "templates/python-dual-entry/myapp/gui/main.py",
        "templates/python-dual-entry/myapp/runner/validation.py",
        "templates/python-dual-entry/myapp/runner/workflows.py",
        "templates/python-dual-entry/myapp/runner/text_transform.py",
        "templates/pr-control-plane/scripts/check_review_state/main.py",
        "templates/pr-control-plane/scripts/harness_gap/main.py",
        "templates/pr-control-plane/scripts/remediation_loop/main.py",
        "templates/pr-control-plane/scripts/request_rerun/main.py",
        "templates/pr-control-plane/scripts/resolve_bot_threads/main.py",
        "templates/pr-control-plane/scripts/risk_policy_gate/main.py",
        "templates/pr-control-plane/scripts/validate_browser_evidence/main.py",
    ):
        _write(governance_root / rel_path, "from __future__ import annotations\n")

    _write(
        governance_root / "templates/python-dual-entry/myapp/main.py",
        """
        from myapp.cli.main import build_cli_request, has_cli_intent
        from myapp.gui.main import start_gui
        """,
    )
    _write(
        governance_root / "templates/python-dual-entry/myapp/runner/main.py",
        """
        from .validation import validate_job_config
        from .workflows import get_workflow
        """,
    )
    _write(
        governance_root / "templates/pr-control-plane/scripts/main.py",
        """
        def _load_child_module(child_name: str):
            return child_name

        _load_child_module("check_review_state")
        _load_child_module("risk_policy_gate")
        subparsers = type("Subparsers", (), {"add_parser": lambda self, *_args, **_kwargs: None})()
        subparsers.add_parser("risk-policy-gate")
        """,
    )


class FolderArchitectureBoundaryTests(unittest.TestCase):
    def test_vendored_mode_ignores_host_python_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_root = Path(tmp_dir)
            repo_root = tmp_root / "host"
            governance_root = tmp_root / "host/.governance"
            _write_minimal_governance_tree(governance_root)
            _write(repo_root / "app.py", "print('host file')\n")

            issues = []
            check_governance_owned_contracts(repo_root, governance_root, issues)

            self.assertEqual([], issues)

    def test_vendored_mode_still_flags_governance_python_outside_scope(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_root = Path(tmp_dir)
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

    def test_source_repo_mode_keeps_scope_manifest_reference_check(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = Path(tmp_dir)
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
