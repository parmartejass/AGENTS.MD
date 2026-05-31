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


class ProjectAuthorityRouteDocTests(unittest.TestCase):
    def test_required_current_work_route_requires_existing_target(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = Path(tmp_dir)
            write_text(
                repo_root / "docs/project/goal/goal_index.md",
                """
# Goal Branch Index

- [goal.md](goal.md) - Canonical goal. Required when: checking goal.
- [current-work.md](current-work.md) - Live work status. Required when: checking handoff.
""".lstrip(),
            )

            errors = MANIFEST_AND_DOCS._validate_project_optional_leaf_routes(repo_root)

            self.assertTrue(any("references missing local route target: current-work.md" in error for error in errors), errors)

    def test_required_current_work_route_requires_router_link(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = Path(tmp_dir)
            write_text(
                repo_root / "docs/project/goal/goal_index.md",
                """
# Goal Branch Index

- [goal.md](goal.md) - Canonical goal. Required when: checking goal.
""".lstrip(),
            )
            write_text(repo_root / "docs/project/goal/current-work.md", "# Current Work\n")

            errors = MANIFEST_AND_DOCS._validate_project_optional_leaf_routes(repo_root)

            self.assertTrue(
                any("must reference required current-work.md" in error for error in errors),
                errors,
            )

    def test_required_current_work_route_requires_existing_target_with_uppercase_extension(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = Path(tmp_dir)
            write_text(
                repo_root / "docs/project/goal/goal_index.md",
                """
# Goal Branch Index

- [goal.md](goal.md) - Canonical goal. Required when: checking goal.
- [missing.MD](missing.MD) - Broken route. Required when: testing.
""".lstrip(),
            )

            errors = MANIFEST_AND_DOCS._validate_project_optional_leaf_routes(repo_root)

            self.assertTrue(any("references missing local route target: missing.MD" in error for error in errors), errors)
            self.assertTrue(any("must reference required current-work.md" in error for error in errors), errors)

    def test_project_docs_requires_current_work_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = Path(tmp_dir)

            errors = MANIFEST_AND_DOCS.check_project_docs(repo_root, "", REPO_ROOT)

            self.assertTrue(any("Missing required file: docs/project/goal/current-work.md" in error for error in errors), errors)

    def test_project_docs_rejects_parallel_memory_like_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = Path(tmp_dir)
            write_text(repo_root / "docs/project/authority-memory/authority-memory_index.md", "# Authority Memory\n")

            errors = MANIFEST_AND_DOCS.check_project_docs(repo_root, "", REPO_ROOT)

            self.assertTrue(any("Forbidden parallel memory docs path exists" in error for error in errors), errors)

    def test_project_docs_rejects_parallel_memories_like_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = Path(tmp_dir)
            write_text(repo_root / "docs/project/memories/memories_index.md", "# Memories\n")

            errors = MANIFEST_AND_DOCS.check_project_docs(repo_root, "", REPO_ROOT)

            self.assertTrue(any("Forbidden parallel memory docs path exists" in error for error in errors), errors)

    def test_project_docs_rejects_parallel_transcript_like_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = Path(tmp_dir)
            write_text(repo_root / "docs/project/transcripts/transcripts_index.md", "# Transcripts\n")

            errors = MANIFEST_AND_DOCS.check_project_docs(repo_root, "", REPO_ROOT)

            self.assertTrue(any("Forbidden parallel memory docs path exists" in error for error in errors), errors)

    def test_project_docs_rejects_parallel_memory_variant_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = Path(tmp_dir)
            write_text(repo_root / "docs/project/memory-bank/memory-bank_index.md", "# Memory Bank\n")
            write_text(repo_root / "docs/project/authority_memories/authority_memories_index.md", "# Memories\n")
            write_text(
                repo_root / "docs/project/session-transcripts/session-transcripts_index.md",
                "# Transcripts\n",
            )

            errors = MANIFEST_AND_DOCS.check_project_docs(repo_root, "", REPO_ROOT)

            self.assertGreaterEqual(sum("Forbidden parallel memory docs path exists" in error for error in errors), 3)

    def test_project_docs_requires_policy_owner_for_parallel_memory_rule(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            governance_root = Path(tmp_dir)
            write_text(governance_root / "scripts/entrypoint_contracts.json", (REPO_ROOT / "scripts/entrypoint_contracts.json").read_text(encoding="utf-8"))
            write_text(
                governance_root / "docs/agents/25-docs-ssot-policy/docs-ssot-policy.md",
                "# Policy without no-parallel rule\n",
            )

            errors = MANIFEST_AND_DOCS.check_project_docs(Path(tmp_dir), "", governance_root)

            self.assertTrue(
                any("Docs SSOT policy must state the no-parallel-memory-doc-tree rule" in error for error in errors),
                errors,
            )

    def test_project_docs_rejects_duplicate_current_work_status(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = Path(tmp_dir)
            write_text(
                repo_root / "docs/project/goal/current-work.md",
                """
# Current Work

Status: `active`
Status: `blocked`
Work item ID: `CW-20260531-001`
Last updated: `2026-05-31`

## User Prompt
```text
Prompt.
```

## Goal Statement
- Goal.

## Status

## Goal Alignment

## Blockers

## Boundaries

## Supersession

## SSOT Layers
- Runtime truth: pending verification
- Semantic truth: validator contract
- Recorded truth: current-work.md

## Review Confirmation
- Pre-change review: complete
- Post-change review: pending
- Fulfillment: pending

## Next safe action

Continue.

## Clear Rule

Clear when done.
""".lstrip(),
            )

            errors = MANIFEST_AND_DOCS.check_project_docs(repo_root, "", REPO_ROOT)

            self.assertTrue(any("contains duplicate Status fields" in error for error in errors), errors)
