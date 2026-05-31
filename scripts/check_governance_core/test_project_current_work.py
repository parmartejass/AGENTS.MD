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
    "check_governance_core_manifest_and_docs_current_work", SCRIPT_ROOT / "_manifest_and_docs.py"
)
class ProjectCurrentWorkDocTests(unittest.TestCase):
    def test_project_docs_accepts_reviewed_empty_current_work_state(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = Path(tmp_dir)
            write_text(
                repo_root / "docs/project/goal/current-work.md",
                """
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
- Next checkpoint: update before work begins.

## Goal Alignment
- Durable intent owner: `docs/project/goal/goal.md`
- This file must not redefine project objective, acceptance criteria, non-goals, or durable intent.

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
""".lstrip(),
            )

            errors = MANIFEST_AND_DOCS._validate_project_authority_memory_docs(repo_root)

            self.assertFalse(errors, errors)

    def test_project_docs_accepts_active_current_work_prompt_contract(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = Path(tmp_dir)
            write_text(
                repo_root / "docs/project/goal/current-work.md",
                """
# Current Work

Status: active
Work item ID: CW-20260531-002
Last updated: 2026-05-31
Owner/context: test

## User Prompt
```text
Add the active work contract.
```

## Prompt Safety
- Storage decision: reviewed-safe
- Evidence: prompt reviewed by test.
- Prompt equality witness: manual test fixture.

## Goal Statement
- Add active work contract validation.

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
- DP-20260531-001 `[planned]`: Add source-derived plan validation; prompt/goal link: active prompt and work-item goal; SSOT owner: docs/project/goal/current-work.md; target files/docs: validator tests; witness: project docs check.

## Implementation Records
- Owner docs updated: pending.
- Changelog witness: pending.
- Change records: pending.

## Reconciliation
- Stale/rejected prompts: none.
- Stale/rejected plans: none.
- Unused artifacts: none.

## Supersession
- Superseded by: N/A
- Clear when: test completes.

## SSOT Layers
- Runtime truth: pending verification
- Semantic truth: validator contract
- Recorded truth: current-work.md

## Review Confirmation
- Pre-change review: complete
- Post-change review: pending
- Fulfillment: pending

## Closure Handoff
- Changelog witness: pending.
- Commit/push state: uncommitted
- Tracked artifact witness: pending.

## Next safe action
- Continue.

## Clear Rule
- Reset this file to `Status: no-active-work`; do not delete it.
""".lstrip(),
            )

            errors = MANIFEST_AND_DOCS._validate_project_authority_memory_docs(repo_root)

            self.assertFalse(errors, errors)

    def test_project_docs_rejects_active_current_work_missing_prompt(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = Path(tmp_dir)
            write_text(
                repo_root / "docs/project/goal/current-work.md",
                """
# Current Work

Status: active
Work item ID: CW-20260531-002
Last updated: 2026-05-31
Owner/context: test

## Goal Statement
- Add active work contract validation.

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
- Continue.

## Clear Rule
- Reset this file to `Status: no-active-work`; do not delete it.
""".lstrip(),
            )

            errors = MANIFEST_AND_DOCS._validate_project_authority_memory_docs(repo_root)

            self.assertTrue(any("must contain required field/section: ## User Prompt" in error for error in errors), errors)

    def test_project_docs_rejects_active_current_work_placeholder_prompt_and_goal(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = Path(tmp_dir)
            write_text(
                repo_root / "docs/project/goal/current-work.md",
                """
# Current Work

Status: active
Work item ID: CW-20260531-002
Last updated: 2026-05-31
Owner/context: test

## User Prompt
```text
TBD
```

## Prompt Safety
- Storage decision: reviewed-safe
- Evidence: prompt reviewed by test.
- Prompt equality witness: manual test fixture.

## Goal Statement
- TBD

## Status

## Goal Alignment

## Blockers

## Boundaries

## Derived Plan
- DP-20260531-001 `[planned]`: Add source-derived plan validation; prompt/goal link: active prompt and work-item goal; SSOT owner: docs/project/goal/current-work.md; target files/docs: validator tests; witness: project docs check.

## Implementation Records
- Owner docs updated: pending.
- Changelog witness: pending.
- Change records: pending.

## Reconciliation
- Stale/rejected prompts: none.
- Stale/rejected plans: none.
- Unused artifacts: none.

## Supersession

## SSOT Layers
- Runtime truth: pending verification
- Semantic truth: validator contract
- Recorded truth: current-work.md

## Review Confirmation
- Pre-change review: complete
- Post-change review: pending
- Fulfillment: pending

## Closure Handoff
- Changelog witness: pending.
- Commit/push state: uncommitted
- Tracked artifact witness: pending.

## Next safe action
- Continue.

## Clear Rule
- Reset this file to `Status: no-active-work`; do not delete it.
""".lstrip(),
            )

            errors = MANIFEST_AND_DOCS._validate_project_authority_memory_docs(repo_root)

            self.assertTrue(any("User Prompt section must contain active work content" in error for error in errors), errors)
            self.assertTrue(any("Goal Statement section must contain active work content" in error for error in errors), errors)

    def test_project_docs_rejects_active_current_work_blank_truth_and_review_values(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = Path(tmp_dir)
            write_text(
                repo_root / "docs/project/goal/current-work.md",
                """
# Current Work

Status: active
Work item ID: CW-20260531-002
Last updated: 2026-05-31
Owner/context: test

## User Prompt
```text
Implement prompt-first planning gate.
```

## Prompt Safety
- Storage decision: reviewed-safe
- Evidence: prompt reviewed by test.
- Prompt equality witness: manual test fixture.

## Goal Statement
- Implement prompt-first planning gate validation.

## Status

## Goal Alignment

## Blockers

## Boundaries

## Derived Plan
- DP-20260531-001 `[planned]`: Add source-derived plan validation; prompt/goal link: active prompt and work-item goal; SSOT owner: docs/project/goal/current-work.md; target files/docs: validator tests; witness: project docs check.

## Implementation Records
- Owner docs updated: pending.
- Changelog witness: pending.
- Change records: pending.

## Reconciliation
- Stale/rejected prompts: none.
- Stale/rejected plans: none.
- Unused artifacts: none.

## Supersession

## SSOT Layers
- Runtime truth:
- Semantic truth: validator contract
- Recorded truth: current-work.md

## Review Confirmation
- Pre-change review:
- Post-change review: pending
- Fulfillment: pending

## Closure Handoff
- Changelog witness: pending.
- Commit/push state: uncommitted
- Tracked artifact witness: pending.

## Next safe action
- Continue.

## Clear Rule
- Reset this file to `Status: no-active-work`; do not delete it.
""".lstrip(),
            )

            errors = MANIFEST_AND_DOCS._validate_project_authority_memory_docs(repo_root)

            self.assertTrue(any("non-placeholder value for Runtime truth" in error for error in errors), errors)
            self.assertTrue(any("non-placeholder value for Pre-change review" in error for error in errors), errors)
