from __future__ import annotations

import importlib.util
import json
import shutil
import sys
import textwrap
import unittest
from contextlib import contextmanager
from pathlib import Path
from uuid import uuid4


SCRIPT_ROOT = Path(__file__).resolve().parent
MODULE_PATH = SCRIPT_ROOT / "check_folder_architecture_main.py"
ENTRYPOINT_REGISTRY_PATH = SCRIPT_ROOT.parent / "entrypoint_contracts.json"
SPEC = importlib.util.spec_from_file_location("check_folder_architecture_main", MODULE_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"Unable to load checker module from {MODULE_PATH}")

MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)

check_governance_owned_contracts = MODULE._check_governance_owned_contracts
load_scope_manifest = MODULE._load_scope_manifest
python_entrypoint_filename = MODULE._python_entrypoint_filename
TMP_ROOT = SCRIPT_ROOT / ".tmp-test-workspaces"


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
        governance_root / "scripts/entrypoint_contracts.json",
        ENTRYPOINT_REGISTRY_PATH.read_text(encoding="utf-8"),
    )
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
                    {
                        "path": "templates/python-dual-entry/myapp",
                        "enforcement_mode": "enforce",
                        "owner": "scripts/check_folder_architecture/check_folder_architecture_main.py",
                    },
                    {
                        "path": "templates/pr-control-plane/scripts",
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
        "templates/python-dual-entry/myapp/cli/cli_main.py",
        "templates/python-dual-entry/myapp/core/core_main.py",
        "templates/python-dual-entry/myapp/gui/gui_main.py",
        "templates/python-dual-entry/myapp/myapp_main.py",
        "templates/python-dual-entry/myapp/runner/validation.py",
        "templates/python-dual-entry/myapp/runner/workflows.py",
        "templates/python-dual-entry/myapp/runner/text_transform.py",
        "templates/pr-control-plane/scripts/check_review_state/check_review_state_main.py",
        "templates/pr-control-plane/scripts/harness_gap/harness_gap_main.py",
        "templates/pr-control-plane/scripts/remediation_loop/remediation_loop_main.py",
        "templates/pr-control-plane/scripts/request_rerun/request_rerun_main.py",
        "templates/pr-control-plane/scripts/resolve_bot_threads/resolve_bot_threads_main.py",
        "templates/pr-control-plane/scripts/risk_policy_gate/risk_policy_gate_main.py",
        "templates/pr-control-plane/scripts/validate_browser_evidence/validate_browser_evidence_main.py",
    ):
        _write(governance_root / rel_path, "from __future__ import annotations\n")

    _write(
        governance_root / "templates/python-dual-entry/myapp/myapp_main.py",
        """
        from myapp.cli.cli_main import build_cli_request, has_cli_intent
        from myapp.gui.gui_main import start_gui
        """,
    )
    _write(
        governance_root / "templates/python-dual-entry/myapp/runner/runner_main.py",
        """
        from .validation import validate_job_config
        from .workflows import get_workflow
        """,
    )
    _write(
        governance_root / "templates/pr-control-plane/scripts/scripts_main.py",
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

    def test_invalid_registry_returns_none_and_issue(self) -> None:
        with _temporary_workspace() as tmp_root:
            governance_root = tmp_root
            _write(
                governance_root / "scripts/entrypoint_contracts.json",
                """
                {
                  "version": 1,
                  "runtime_code": {
                    "filename_pattern": "<authority>_<entrypoint_token>.<extension>",
                    "languages": {
                      "python": {
                        "artifact_kinds": {
                          "executable": {
                            "extension": "py"
                          }
                        }
                      }
                    }
                  },
                  "docs": {}
                }
                """,
            )

            issues = []
            resolved = python_entrypoint_filename("billing", governance_root, issues)

            self.assertIsNone(resolved)
            self.assertTrue(
                any("entrypoint_token" in issue.message for issue in issues),
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
