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
    "check_governance_core_manifest_and_docs_current_work_security", SCRIPT_ROOT / "_manifest_and_docs.py"
)


class ProjectCurrentWorkSecurityDocTests(unittest.TestCase):
    def test_project_docs_rejects_secret_like_prompt_and_missing_plan(self) -> None:
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
Use api_key = abc123secretvalue.
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
- Pending plan.

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

            self.assertTrue(any("unsafe secret-like pattern" in error for error in errors), errors)
            self.assertTrue(any("Derived Plan section must contain at least one DP-* plan item" in error for error in errors), errors)

    def test_project_docs_rejects_common_token_prefix_prompt(self) -> None:
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
Use ghp_1234567890abcdefghijklmnop.
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
- DP-20260531-001 `[planned]`: Validate token pattern; prompt/goal link: active prompt and work-item goal; SSOT owner: docs/project/goal/current-work.md; target files/docs: validator tests; witness: project docs check.

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

            self.assertTrue(any("unsafe secret-like pattern" in error for error in errors), errors)


if __name__ == "__main__":
    unittest.main()
