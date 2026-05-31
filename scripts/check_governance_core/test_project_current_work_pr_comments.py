from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT_ROOT = Path(__file__).resolve().parent


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
    "check_governance_core_manifest_and_docs_current_work_pr_comments", SCRIPT_ROOT / "_manifest_and_docs.py"
)


def _active_current_work_doc(*, status: str, prompt: str, commit_state: str, plan_status: str = "completed") -> str:
    return f"""
# Current Work

Status: {status}
Work item ID: CW-20260531-002
Last updated: 2026-05-31
Owner/context: test

## User Prompt
```text
{prompt}
```

## Prompt Safety
- Storage decision: reviewed-safe
- Evidence: prompt reviewed by test.
- Prompt equality witness: manual test fixture.

## Goal Statement
- Implement prompt-first planning gate validation.

## Status
- Last verified: 2026-05-31
- Evidence/version: test
- Re-verification trigger: test
- Current state: active test.
- Next checkpoint: finish test.

## Goal Alignment
- Durable intent owner: `docs/project/goal/goal.md`
- This file must not redefine project objective, acceptance criteria, non-goals, or durable intent.

## Blockers
- None.

## Boundaries
- Test boundary.

## Derived Plan
- DP-20260531-001 `[{plan_status}]`: Add source-derived plan validation; prompt/goal link: active prompt and work-item goal; SSOT owner: docs/project/goal/current-work.md; target files/docs: validator tests; witness: project docs check.

## Implementation Records
- Owner docs updated: validator tests.
- Changelog witness: not-required + reason:test fixture.
- Change records: not-required + reason:test fixture.

## Reconciliation
- Stale/rejected prompts: none.
- Stale/rejected plans: none.
- Unused artifacts: none.

## Supersession
- Superseded by: N/A
- Clear when: test completes.

## SSOT Layers
- Runtime truth: project docs check fixture.
- Semantic truth: validator contract.
- Recorded truth: current-work.md fixture.

## Review Confirmation
- Pre-change review: council fixture.
- Post-change review: post-change fixture.
- Fulfillment: recorded prompt and work-item goal fulfilled by fixture.

## Closure Handoff
- Changelog witness: not-required + reason:test fixture.
- Commit/push state: {commit_state}
- Tracked artifact witness: git status fixture.

## Next safe action
- Continue.

## Clear Rule
- Reset this file to `Status: no-active-work`; do not delete it.
""".lstrip()


def _no_active_current_work_doc_with_status_residue() -> str:
    return """
# Current Work

Status: no-active-work
Work item ID: CW-20260531-001
Last updated: 2026-05-31
Owner/context: test

## User Prompt
```text
N/A - no active work
```

## Prompt Safety
- Storage decision: N/A - no active work
- Evidence: N/A - no active work
- Prompt equality witness: N/A - no active work

## Goal Statement
- N/A - no active work

## Status
- Last verified: 2026-05-31
- Evidence/version: test
- Re-verification trigger: test
- Current state: no active handoff.
- Next checkpoint: resume DP-20260531-777 after blocker clears.

## Goal Alignment
- Durable intent owner: `docs/project/goal/goal.md`

## Blockers
- None.

## Boundaries
- None.

## Derived Plan
- N/A - no active work

## Implementation Records
- Owner docs updated: N/A - no active work
- Changelog witness: N/A - no active work
- Change records: N/A - no active work

## Reconciliation
- Stale/rejected prompts: N/A - no active work
- Stale/rejected plans: N/A - no active work
- Unused artifacts: N/A - no active work

## Supersession
- Superseded by: N/A
- Clear when: no active work remains.

## SSOT Layers
- Runtime truth: N/A - no active work
- Semantic truth: N/A - no active work
- Recorded truth: N/A - no active work

## Review Confirmation
- Pre-change review: N/A - no active work
- Post-change review: N/A - no active work
- Fulfillment: N/A - no active work

## Closure Handoff
- Changelog witness: N/A - no active work
- Commit/push state: N/A - no active work
- Tracked artifact witness: N/A - no active work

## Next safe action
- Update this file before starting work.

## Clear Rule
- Reset this file to `Status: no-active-work`; do not delete it.
""".lstrip()


class ProjectCurrentWorkPRCommentTests(unittest.TestCase):
    def test_project_docs_accepts_active_current_work_prompt_with_status_text(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = Path(tmp_dir)
            write_text(
                repo_root / "docs/project/goal/current-work.md",
                _active_current_work_doc(
                    status="active",
                    prompt="Reproduce this issue-template block:\nStatus: active",
                    commit_state="uncommitted",
                    plan_status="planned",
                ),
            )

            errors = MANIFEST_AND_DOCS._validate_project_authority_memory_docs(repo_root)

            self.assertFalse(errors, errors)

    def test_project_docs_rejects_no_active_work_residue_in_status_sections(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = Path(tmp_dir)
            write_text(repo_root / "docs/project/goal/current-work.md", _no_active_current_work_doc_with_status_residue())

            errors = MANIFEST_AND_DOCS._validate_project_authority_memory_docs(repo_root)

            self.assertTrue(any("no-active-work sections must not retain active prompt" in error for error in errors), errors)

    def test_project_docs_rejects_ready_to_clear_with_committed_only_handoff(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = Path(tmp_dir)
            write_text(
                repo_root / "docs/project/goal/current-work.md",
                _active_current_work_doc(
                    status="ready-to-clear",
                    prompt="Implement prompt-first planning gate.",
                    commit_state="committed:abcdef1",
                ),
            )

            errors = MANIFEST_AND_DOCS._validate_project_authority_memory_docs(repo_root)

            self.assertTrue(any("requires pushed/PR evidence or not-required + reason" in error for error in errors), errors)


if __name__ == "__main__":
    unittest.main()
