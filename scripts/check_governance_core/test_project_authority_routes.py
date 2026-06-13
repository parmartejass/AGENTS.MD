from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

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

MANIFEST_AND_DOCS = _load_module(
    "check_governance_core_manifest_and_docs", SCRIPT_ROOT / "_manifest_and_docs.py"
)


def _write_minimal_project_docs(repo_root: Path, *, extra_project_routes: str = "") -> None:
    write_text(
        repo_root / "docs/project/project_index.md",
        f"""
# Project Branch Index

- [goal/goal_index.md](goal/goal_index.md) - Goal. Required when: checking goal.
- [rules/rules_index.md](rules/rules_index.md) - Rules. Required when: checking rules.
- [architecture/architecture_index.md](architecture/architecture_index.md) - Architecture. Required when: checking architecture.
- [data-truth/data-truth_index.md](data-truth/data-truth_index.md) - Data truth. Required when: checking data truth.
- [learning/learning_index.md](learning/learning_index.md) - Learning. Required when: checking learning.
{extra_project_routes}
""".lstrip(),
    )
    for folder in ("goal", "rules", "architecture", "data-truth", "learning"):
        router_name = f"{folder}_index.md"
        leaf_name = f"{folder}.md"
        write_text(
            repo_root / "docs/project" / folder / router_name,
            f"# {folder.title()} Branch Index\n\n- [{leaf_name}]({leaf_name}) - Leaf. Required when: checking {folder}.\n",
        )
        write_text(
            repo_root / "docs/project" / folder / leaf_name,
            """
---
doc_type: reference
ssot_owner: AGENTS.md
update_trigger: test fixture changes
---

# Leaf

## Scope
- Test fixture.

## Verification
- Test fixture.
""".lstrip(),
        )


class ProjectAuthorityRouteDocTests(unittest.TestCase):
    def test_optional_leaf_routes_require_existing_targets_with_uppercase_extension(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = Path(tmp_dir)
            write_text(
                repo_root / "docs/project/architecture/protected-behavior.md",
                "# Protected Behavior\n",
            )
            write_text(
                repo_root / "docs/project/architecture/architecture_index.md",
                """
# Architecture Branch Index

- [architecture.md](architecture.md) - Canonical architecture. Required when: checking architecture.
- [missing.MD](missing.MD) - Broken route. Required when: testing.
""".lstrip(),
            )

            errors = MANIFEST_AND_DOCS._validate_project_optional_leaf_routes(repo_root)

            self.assertTrue(any("references missing local route target: missing.MD" in error for error in errors), errors)

    def test_branch_local_subdoc_passes_when_routed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = Path(tmp_dir)
            _write_minimal_project_docs(repo_root)
            write_text(
                repo_root / "docs/project/goal/goal_index.md",
                """
# Goal Branch Index

- [goal.md](goal.md) - Goal. Required when: checking goal.
- [steering-truth.md](steering-truth.md) - Branch-local owner subdoc. Required when: checking steering truth.
""".lstrip(),
            )
            write_text(
                repo_root / "docs/project/goal/steering-truth.md",
                """
---
doc_type: reference
ssot_owner: docs/project/goal/steering-truth.md
update_trigger: steering truth changes
---

# Steering Truth
""".lstrip(),
            )

            errors = MANIFEST_AND_DOCS.check_project_docs(repo_root, "", REPO_ROOT)

            self.assertFalse(any("steering-truth" in error for error in errors), errors)

    def test_branch_local_subdoc_fails_when_orphan(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = Path(tmp_dir)
            _write_minimal_project_docs(repo_root)
            write_text(
                repo_root / "docs/project/goal/steering-truth.md",
                """
---
doc_type: reference
ssot_owner: docs/project/goal/steering-truth.md
update_trigger: steering truth changes
---

# Steering Truth
""".lstrip(),
            )

            errors = MANIFEST_AND_DOCS.check_project_docs(repo_root, "", REPO_ROOT)

            self.assertTrue(any("goal_index.md must reference steering-truth.md" in error for error in errors), errors)

    def test_branch_local_route_fails_when_target_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = Path(tmp_dir)
            _write_minimal_project_docs(repo_root)
            write_text(
                repo_root / "docs/project/goal/goal_index.md",
                """
# Goal Branch Index

- [goal.md](goal.md) - Goal. Required when: checking goal.
- [missing-owner.md](missing-owner.md) - Missing branch-local owner. Required when: checking missing owner.
""".lstrip(),
            )

            errors = MANIFEST_AND_DOCS.check_project_docs(repo_root, "", REPO_ROOT)

            self.assertTrue(any("references missing local route target: missing-owner.md" in error for error in errors), errors)

    def test_project_docs_does_not_reject_branch_local_doc_names_by_substring(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = Path(tmp_dir)
            _write_minimal_project_docs(repo_root)
            write_text(
                repo_root / "docs/project/goal/goal_index.md",
                """
# Goal Branch Index

- [goal.md](goal.md) - Goal. Required when: checking goal.
- [memory-bank.md](memory-bank.md) - Routed branch-local owner. Required when: checking memory-bank.
- [transcripts.md](transcripts.md) - Routed branch-local owner. Required when: checking transcripts.
""".lstrip(),
            )
            for name in ("memory-bank", "transcripts"):
                write_text(
                    repo_root / f"docs/project/goal/{name}.md",
                    f"""
---
doc_type: reference
ssot_owner: docs/project/goal/{name}.md
update_trigger: routed owner changes
---

# {name}
""".lstrip(),
                )

            errors = MANIFEST_AND_DOCS.check_project_docs(repo_root, "", REPO_ROOT)

            self.assertFalse(any("memory-bank" in error or "transcripts" in error for error in errors), errors)

    def test_project_docs_requires_docs_ssot_policy_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            governance_root = Path(tmp_dir)
            write_text(governance_root / "scripts/entrypoint_contracts.json", (REPO_ROOT / "scripts/entrypoint_contracts.json").read_text(encoding="utf-8"))

            errors = MANIFEST_AND_DOCS.check_project_docs(Path(tmp_dir), "", governance_root)

            self.assertTrue(
                any("Missing docs SSOT policy" in error for error in errors),
                errors,
            )
