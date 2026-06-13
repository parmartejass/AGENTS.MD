#!/usr/bin/env python3
from __future__ import annotations

import shutil
import subprocess
import unittest
from unittest import mock
from _fixtures import (
    DOCS_SSOT_SCRIPT_PATH,
    POLICY_DOC,
    POWERSHELL_TIMEOUT_SEC,
    _write as write,
    assert_negative_powershell_case,
    check_docs_ssot,
    powershell_executable,
    run_powershell_docs_check_output,
    temporary_workspace,
    write_parent_chain,
    write_router_fixture,
)


class DocsRouterContractTests(unittest.TestCase):
    def test_malformed_registry_reports_explicit_error(self) -> None:
        with temporary_workspace() as tmp_root:
            repo_root = tmp_root / "repo"
            governance_root = tmp_root / "governance"

            write(governance_root / "docs/agents/25-docs-ssot-policy/docs-ssot-policy.md", POLICY_DOC)
            write(
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
                  "docs": {
                    "public_leaf_patterns": {
                      "plain_folder_default": "<authority>.md",
                      "numbered_governance_folder": "<authority>.md",
                      "dated_evidence_folder": "evidence.md"
                    },
                    "authority_resolution": {
                      "numbered_governance_folder_regex": "^[0-9]{2}-(?P<authority>.+)$",
                      "dated_evidence_folder_regex": "^[0-9]{4}-[0-9]{2}-[0-9]{2}-.+$",
                      "dated_evidence_authority": "evidence"
                    },
                    "public_leaf_model": {
                      "minimum_public_leaf_count": 1
                    },
                    "explicit_family_exceptions": {
                      "identity_files": ["SKILL.md", "mcp.json"]
                    }
                  }
                }
                """,
            )
            write_parent_chain(repo_root, "project/goal")
            write(
                repo_root / "docs/project/goal/goal.md",
                """
                ---
                doc_type: reference
                ssot_owner: AGENTS.md
                update_trigger: fixture changes
                ---

                # Goal
                """,
            )

            errors, _warnings = check_docs_ssot(repo_root, governance_root)
            self.assertTrue(any("docs.router_pattern" in error for error in errors), errors)

    def test_router_plus_primary_leaf_passes_for_representative_folders(self) -> None:
        fixtures = (
            ("project/goal", "goal.md"),
            ("agents/00-principles", "principles.md"),
            ("agents/platforms/00-platform-runtime-standards", "platform-runtime-standards.md"),
        )
        for rel_dir, leaf_name in fixtures:
            with self.subTest(rel_dir=rel_dir):
                with temporary_workspace() as tmp_root:
                    repo_root = tmp_root / "repo"
                    governance_root = tmp_root / "governance"
                    write_router_fixture(repo_root, governance_root, rel_dir, leaf_name)

                    errors, _warnings = check_docs_ssot(repo_root, governance_root)
                    self.assertEqual(errors, [], errors)

    def test_router_missing_primary_leaf_link_fails(self) -> None:
        with temporary_workspace() as tmp_root:
            repo_root = tmp_root / "repo"
            governance_root = tmp_root / "governance"

            write_router_fixture(
                repo_root,
                governance_root,
                "project/goal",
                "goal.md",
                router_target="missing.md",
            )

            errors, _warnings = check_docs_ssot(repo_root, governance_root)
            self.assertTrue(any("goal.md" in error for error in errors), errors)

    def test_router_link_case_mismatch_fails(self) -> None:
        with temporary_workspace() as tmp_root:
            repo_root = tmp_root / "repo"
            governance_root = tmp_root / "governance"

            write_router_fixture(
                repo_root,
                governance_root,
                "project/goal",
                "goal.md",
                router_target="Goal.md",
            )

            errors, _warnings = check_docs_ssot(repo_root, governance_root)
            self.assertTrue(any("goal.md" in error for error in errors), errors)

    def test_multiple_public_leafs_pass(self) -> None:
        with temporary_workspace() as tmp_root:
            repo_root = tmp_root / "repo"
            governance_root = tmp_root / "governance"

            write_router_fixture(
                repo_root,
                governance_root,
                "project/goal",
                "goal.md",
                extra_leaf_names=["acceptance.md"],
            )

            errors, _warnings = check_docs_ssot(repo_root, governance_root)
            self.assertEqual(errors, [], errors)

    def test_content_bearing_router_fails(self) -> None:
        with temporary_workspace() as tmp_root:
            repo_root = tmp_root / "repo"
            governance_root = tmp_root / "governance"

            write_router_fixture(
                repo_root,
                governance_root,
                "project/goal",
                "goal.md",
                content_bearing_router=True,
            )

            errors, _warnings = check_docs_ssot(repo_root, governance_root)
            self.assertTrue(any("routing-only" in error for error in errors), errors)

    def test_prefix_suffix_trick_does_not_satisfy_direct_child_link(self) -> None:
        with temporary_workspace() as tmp_root:
            repo_root = tmp_root / "repo"
            governance_root = tmp_root / "governance"

            write_router_fixture(
                repo_root,
                governance_root,
                "project/goal",
                "goal.md",
                router_target="goal-other/goal.md",
            )

            errors, _warnings = check_docs_ssot(repo_root, governance_root)
            self.assertTrue(any("missing route" in error for error in errors), errors)

    def test_root_absolute_router_target_fails(self) -> None:
        with temporary_workspace() as tmp_root:
            repo_root = tmp_root / "repo"
            governance_root = tmp_root / "governance"

            write_router_fixture(
                repo_root,
                governance_root,
                "project/goal",
                "goal.md",
                router_target="/goal.md",
            )

            errors, _warnings = check_docs_ssot(repo_root, governance_root)
            self.assertTrue(any("invalid or out-of-bounds" in error for error in errors), errors)

    @unittest.skipIf(powershell_executable() is None, "PowerShell is not available in PATH.")
    def test_powershell_checker_matches_negative_router_contract_case(self) -> None:
        with temporary_workspace() as tmp_root:
            repo_root = tmp_root / "repo"
            governance_root = tmp_root / "governance"

            write_router_fixture(
                repo_root,
                governance_root,
                "project/goal",
                "goal.md",
                router_target="../goal.md",
            )
            assert_negative_powershell_case(repo_root, governance_root)

    @unittest.skipIf(powershell_executable() is None, "PowerShell is not available in PATH.")
    def test_powershell_checker_rejects_root_absolute_router_target(self) -> None:
        with temporary_workspace() as tmp_root:
            repo_root = tmp_root / "repo"
            governance_root = tmp_root / "governance"

            write_router_fixture(
                repo_root,
                governance_root,
                "project/goal",
                "goal.md",
                router_target="/goal.md",
            )
            assert_negative_powershell_case(repo_root, governance_root)

    @unittest.skipIf(powershell_executable() is None, "PowerShell is not available in PATH.")
    def test_powershell_checker_rejects_case_mismatched_router_target(self) -> None:
        with temporary_workspace() as tmp_root:
            repo_root = tmp_root / "repo"
            governance_root = tmp_root / "governance"

            write_router_fixture(
                repo_root,
                governance_root,
                "project/goal",
                "goal.md",
                router_target="Goal.md",
            )
            assert_negative_powershell_case(repo_root, governance_root)

    @unittest.skipIf(powershell_executable() is None, "PowerShell is not available in PATH.")
    def test_powershell_checker_reports_malformed_registry_schema_error(self) -> None:
        with temporary_workspace() as tmp_root:
            repo_root = tmp_root / "repo"
            governance_root = tmp_root / "governance"

            write(governance_root / "docs/agents/25-docs-ssot-policy/docs-ssot-policy.md", POLICY_DOC)
            write(
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
                  "docs": {
                    "public_leaf_patterns": {
                      "plain_folder_default": "<authority>.md",
                      "numbered_governance_folder": "<authority>.md",
                      "dated_evidence_folder": "evidence.md"
                    },
                    "authority_resolution": {
                      "numbered_governance_folder_regex": "^[0-9]{2}-(?P<authority>.+)$",
                      "dated_evidence_folder_regex": "^[0-9]{4}-[0-9]{2}-[0-9]{2}-.+$",
                      "dated_evidence_authority": "evidence"
                    },
                    "public_leaf_model": {
                      "minimum_public_leaf_count": 1
                    },
                    "explicit_family_exceptions": {
                      "identity_files": ["SKILL.md", "mcp.json"]
                    }
                  }
                }
                """,
            )
            (repo_root / "docs").mkdir(parents=True, exist_ok=True)

            combined_output = run_powershell_docs_check_output(repo_root, governance_root)
            self.assertIn("docs.router_pattern", combined_output)

    @unittest.skipIf(powershell_executable() is None, "PowerShell is not available in PATH.")
    def test_powershell_checker_timeout_reports_deterministic_failure(self) -> None:
        with temporary_workspace() as tmp_root:
            repo_root = tmp_root / "repo"
            governance_root = tmp_root / "governance"

            write_router_fixture(
                repo_root,
                governance_root,
                "project/goal",
                "goal.md",
                router_target="../goal.md",
            )
            with mock.patch(
                "subprocess.run",
                side_effect=subprocess.TimeoutExpired(
                    cmd=["pwsh", "-File", str(DOCS_SSOT_SCRIPT_PATH)],
                    timeout=POWERSHELL_TIMEOUT_SEC,
                    output="partial stdout",
                    stderr="partial stderr",
                ),
            ):
                with self.assertRaisesRegex(AssertionError, r"timed out after 30s"):
                    assert_negative_powershell_case(repo_root, governance_root)

    def test_temporary_workspace_cleanup_failure_reports_failed_cleanup(self) -> None:
        tmp_root = None
        real_rmtree = shutil.rmtree
        with mock.patch("_fixtures.shutil.rmtree", side_effect=OSError("locked fixture")):
            with self.assertRaisesRegex(RuntimeError, r"FAILED_CLEANUP: Unable to remove temporary workspace"):
                with temporary_workspace() as workspace_root:
                    tmp_root = workspace_root
                    self.assertTrue(tmp_root.is_dir())

        if tmp_root is not None and tmp_root.exists():
            real_rmtree(tmp_root)


if __name__ == "__main__":
    unittest.main()
