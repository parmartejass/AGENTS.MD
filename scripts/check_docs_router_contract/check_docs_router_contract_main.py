#!/usr/bin/env python3
from __future__ import annotations

import shutil
import unittest
from unittest import mock
from _fixtures import (
    check_docs_ssot,
    temporary_workspace,
    write_router_fixture,
)


class DocsRouterContractTests(unittest.TestCase):
    def test_router_plus_primary_leaf_passes_for_representative_folders(self) -> None:
        fixtures = (
            ("project/goal", "goal.md"),
            ("agents/00-principles", "principles.md"),
            ("agents/skills/00-skill-standards", "skill-standards.md"),
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
