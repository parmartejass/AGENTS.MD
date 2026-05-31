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
    "check_governance_core_manifest_and_docs_current_work_ready", SCRIPT_ROOT / "_manifest_and_docs.py"
)


class ProjectCurrentWorkReadyDocTests(unittest.TestCase):
    def test_project_docs_rejects_ready_to_clear_with_pending_review(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = Path(tmp_dir)
            write_text(
                repo_root / "docs/project/goal/current-work.md",
                """
# Current Work

Status: ready-to-clear
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

## Goal Alignment

## Blockers

## Boundaries

## Derived Plan
- DP-20260531-001 `[completed]`: Add source-derived plan validation; prompt/goal link: active prompt and work-item goal; SSOT owner: docs/project/goal/current-work.md; target files/docs: validator tests; witness: project docs check.

## Implementation Records
- Owner docs updated: validator tests.
- Changelog witness: CH-20260531-999.
- Change records: not-required + reason:test fixture.

## Reconciliation
- Stale/rejected prompts: none.
- Stale/rejected plans: none.
- Unused artifacts: none.

## Supersession

## SSOT Layers
- Runtime truth: project docs check fixture.
- Semantic truth: validator contract
- Recorded truth: current-work.md

## Review Confirmation
- Pre-change review: complete
- Post-change review: pending
- Fulfillment: complete

## Closure Handoff
- Changelog witness: CH-20260531-999.
- Commit/push state: not-required + reason:test fixture
- Tracked artifact witness: git status fixture.

## Next safe action
- Clear.

## Clear Rule
- Reset this file to `Status: no-active-work`; do not delete it.
""".lstrip(),
            )

            errors = MANIFEST_AND_DOCS._validate_project_authority_memory_docs(repo_root)

            self.assertTrue(any("ready-to-clear status cannot contain pending" in error for error in errors), errors)

    def test_project_docs_rejects_ready_to_clear_without_concrete_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = Path(tmp_dir)
            write_text(
                repo_root / "docs/project/goal/current-work.md",
                """
# Current Work

Status: ready-to-clear
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

## Goal Alignment

## Blockers

## Boundaries

## Derived Plan
- DP-20260531-001 `[completed]`: Add source-derived plan validation; prompt/goal link: active prompt and work-item goal; SSOT owner: docs/project/goal/current-work.md; target files/docs: validator tests; witness: project docs check.

## Implementation Records
- Owner docs updated: validator tests.
- Changelog witness: CH-20260531-999.
- Change records: not-required + reason:test fixture.

## Reconciliation
- Stale/rejected prompts: none.
- Stale/rejected plans: none.
- Unused artifacts: none.

## Supersession

## SSOT Layers
- Runtime truth: TBD
- Semantic truth: validator contract
- Recorded truth: current-work.md

## Review Confirmation
- Pre-change review: complete
- Post-change review: complete
- Fulfillment: complete

## Closure Handoff
- Changelog witness: CH-20260531-999.
- Commit/push state: not-required + reason:test fixture
- Tracked artifact witness: git status fixture.

## Next safe action
- Clear.

## Clear Rule
- Reset this file to `Status: no-active-work`; do not delete it.
""".lstrip(),
            )

            errors = MANIFEST_AND_DOCS._validate_project_authority_memory_docs(repo_root)

            self.assertTrue(any("requires concrete evidence for Runtime truth" in error for error in errors), errors)

    def test_project_docs_rejects_ready_to_clear_status_words_without_prompt_goal_fulfillment(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = Path(tmp_dir)
            write_text(
                repo_root / "docs/project/goal/current-work.md",
                """
# Current Work

Status: ready-to-clear
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
- DP-20260531-001 `[completed]`: Add source-derived plan validation; prompt/goal link: active prompt and work-item goal; SSOT owner: docs/project/goal/current-work.md; target files/docs: validator tests; witness: project docs check.

## Implementation Records
- Owner docs updated: validator tests.
- Changelog witness: CH-20260531-999.
- Change records: not-required + reason:test fixture.

## Reconciliation
- Stale/rejected prompts: none.
- Stale/rejected plans: none.
- Unused artifacts: none.

## Supersession

## SSOT Layers
- Runtime truth: verified
- Semantic truth: verified
- Recorded truth: verified

## Review Confirmation
- Pre-change review: complete
- Post-change review: complete
- Fulfillment: complete

## Closure Handoff
- Changelog witness: CH-20260531-999.
- Commit/push state: not-required + reason:test fixture
- Tracked artifact witness: git status fixture.

## Next safe action
- Clear.

## Clear Rule
- Reset this file to `Status: no-active-work`; do not delete it.
""".lstrip(),
            )

            errors = MANIFEST_AND_DOCS._validate_project_authority_memory_docs(repo_root)

            self.assertTrue(any("requires concrete evidence for Runtime truth" in error for error in errors), errors)
            self.assertTrue(
                any("ready-to-clear Fulfillment must reference the recorded prompt and work-item goal" in error for error in errors),
                errors,
            )

    def test_project_docs_rejects_ready_to_clear_with_open_plan_or_uncommitted_state(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = Path(tmp_dir)
            write_text(
                repo_root / "docs/project/goal/current-work.md",
                """
# Current Work

Status: ready-to-clear
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
- Owner docs updated: validator tests.
- Changelog witness: CH-20260531-999.
- Change records: not-required + reason:test fixture.

## Reconciliation
- Stale/rejected prompts: none.
- Stale/rejected plans: none.
- Unused artifacts: none.

## Supersession

## SSOT Layers
- Runtime truth: project docs check fixture.
- Semantic truth: validator contract.
- Recorded truth: current-work.md fixture.

## Review Confirmation
- Pre-change review: council fixture.
- Post-change review: post-change fixture.
- Fulfillment: recorded prompt and work-item goal fulfilled by fixture.

## Closure Handoff
- Changelog witness: CH-20260531-999.
- Commit/push state: uncommitted
- Tracked artifact witness: git status fixture.

## Next safe action
- Clear.

## Clear Rule
- Reset this file to `Status: no-active-work`; do not delete it.
""".lstrip(),
            )

            errors = MANIFEST_AND_DOCS._validate_project_authority_memory_docs(repo_root)

            self.assertTrue(any("Derived Plan cannot contain planned or in_progress items" in error for error in errors), errors)
            self.assertTrue(any("Closure Handoff cannot remain uncommitted" in error for error in errors), errors)


if __name__ == "__main__":
    unittest.main()
