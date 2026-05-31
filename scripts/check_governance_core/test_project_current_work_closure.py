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
    "check_governance_core_manifest_and_docs_current_work_closure", SCRIPT_ROOT / "_manifest_and_docs.py"
)


def _ready_current_work(changelog: str = "CH-20990101-999") -> str:
    return f"""
# Current Work Authority

Status: ready-to-clear
Work item ID: CW-20260531-777
Last updated: 2026-05-31
Owner/context: test

## User Prompt
```text
Implement docs-first closure validation.
```

## Prompt Safety
- Storage decision: reviewed-safe
- Evidence: prompt reviewed by test.
- Prompt equality witness: manual test fixture.

## Goal Statement
- Implement docs-first closure validation.

## Status

## Goal Alignment

## Blockers

## Boundaries

## Derived Plan
- DP-20260531-001 `[completed]`: Validate closure; prompt/goal link: prompt and work-item goal; SSOT owner: docs/project/goal/current-work.md; target files/docs: tests; witness: unit test.

## Implementation Records
- Owner docs updated: current-work validator test fixture.
- Changelog witness: {changelog}.
- Change records: not-required + reason:test fixture.

## Reconciliation
- Stale/rejected prompts: none found in fixture.
- Stale/rejected plans: none found in fixture.
- Unused artifacts: none found in fixture.

## Supersession

## SSOT Layers
- Runtime truth: unit fixture.
- Semantic truth: closure contract.
- Recorded truth: current-work fixture.

## Review Confirmation
- Pre-change review: unit fixture.
- Post-change review: unit fixture.
- Fulfillment: recorded prompt and work-item goal fulfilled by fixture.

## Closure Handoff
- Changelog witness: {changelog}.
- Commit/push state: not-required + reason:test fixture
- Tracked artifact witness: unit fixture.

## Next safe action
- Clear.

## Clear Rule
- Reset this file to `Status: no-active-work`; do not delete it.
""".lstrip()


class ProjectCurrentWorkClosureDocTests(unittest.TestCase):
    def test_ready_to_clear_rejects_missing_changelog_witness(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = Path(tmp_dir)
            write_text(repo_root / "docs/project/goal/current-work.md", _ready_current_work())

            errors = MANIFEST_AND_DOCS._validate_project_authority_memory_docs(repo_root)

            self.assertTrue(any("CH-20990101-999 but changelog.md is missing" in error for error in errors), errors)

    def test_ready_to_clear_requires_changelog_entry_to_reference_current_work(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = Path(tmp_dir)
            write_text(repo_root / "docs/project/goal/current-work.md", _ready_current_work("CH-20260531-777"))
            write_text(
                repo_root / "docs/project/learning/changelog.md",
                """
### CH-20260531-777 - Fixture
- Date: 2026-05-31
- Status: accepted
- Change type: current-work
- Changed owners/files: docs/project/goal/current-work.md
- Current work: CW-20260531-000
- Context: fixture
- Decision/change: fixture
- Validation: fixture
- Evidence/version: fixture
- Commit/push state: not-required + reason:test fixture
- Superseded by: N/A
- Follow-up required: N/A
""".lstrip(),
            )

            errors = MANIFEST_AND_DOCS._validate_project_authority_memory_docs(repo_root)

            self.assertTrue(any("must reference current work CW-20260531-777" in error for error in errors), errors)


if __name__ == "__main__":
    unittest.main()
