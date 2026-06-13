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

INSTRUCTION_DERIVATION = _load_module(
    "check_governance_core_instruction_derivation", SCRIPT_ROOT / "_instruction_derivation.py"
)
REPO_AND_GOVERNANCE = _load_module(
    "check_governance_core_repo_and_governance", SCRIPT_ROOT / "_repo_and_governance.py"
)


class GovernancePlaybookHardGatePositiveTests(unittest.TestCase):
    def test_compliant_governance_learning_playbook_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = Path(tmp_dir)
            playbook_dir = repo_root / "docs/agents/playbooks/governance-learnings-template"
            write_text(
                playbook_dir / "governance-learnings-template.md",
                f"""
## Authority References
- Global hard gates, council requirements, and governance auto-edit rules are owned by `AGENTS.md`.
- Context-routing facts are owned by `agents-manifest.yaml`; this playbook must not keep a local injected-doc list.
- Docs placement, router behavior, and non-owner-doc limits are owned by `docs/agents/25-docs-ssot-policy/docs-ssot-policy.md`.
- This playbook owns the promotion/noise gate, evidence record shape, and copy/paste prompt scaffold for governance-learning work.

## Promotion / Noise Gate
PROMOTE_FOR_DEDUP
DEFER_EVIDENCE_GAP
REJECT_TASK_LOCAL
REJECT_TOOL_BUDGET
REJECT_TEMPORARY_EXECUTION_PREFERENCE
REJECT_WEAK_EVIDENCE
REJECT_CONFLICTS_WITH_SSOT
REJECT_NON_GOVERNANCE
Rejected candidates must include evidence, gate status, and rejection reason.
must not emit draft governance deltas
Target location: N/A + rejected
Example rejection:

## Prompt pack (copy/paste into any chat)

```text
Hard gates (copy/paste scaffold sourced from AGENTS.md):
- Read and follow `AGENTS.md`; if it is inaccessible, request it before doing any work.
- Execute the `AGENTS.md` Context Injection Procedure using the current `agents-manifest.yaml`.
- Execute the docs-first authority gate before any non-trivial plan, review, council output, implementation, or repo mutation.
- For governance auto-edit, apply the `AGENTS.md` Governance Auto-Edit Gate and Subagent Council before editing.
- {INSTRUCTION_DERIVATION.DERIVATION_SCAFFOLD}
- Use docs placement and router rules from `docs/agents/25-docs-ssot-policy/docs-ssot-policy.md`; do not restate them here.
```
""".lstrip(),
            )
            write_text(
                playbook_dir / "codex-session-log-review.md",
                """
Evidence collection owner: this file.
Governance promotion/rejection owner: `governance-learnings-template.md` Promotion / Noise Gate.
Do not encode concept-specific search terms in this playbook.
Use only user-provided or user-approved log roots.
max files:
max bytes per file:
max total bytes:
max runtime seconds:
PARTIAL_SEARCH
budget_limits_hit
FOUND
NOT_FOUND_AFTER_COMPLETE_SEARCH
INACCESSIBLE
UNPARSEABLE
AMBIGUOUS_TIMEFRAME
This playbook ends after evidence handoff.
""".lstrip(),
            )

            errors = REPO_AND_GOVERNANCE.check_governance_playbook_hard_gates(repo_root)

            self.assertEqual([], errors)

    def test_docs_first_prompt_classification_markers_pass(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = Path(tmp_dir)
            write_text(
                repo_root / "AGENTS.md",
                """
## Mandatory Execution Loop (Follow For Every Task)

0) **Docs-first authority gate**:
   - Classify user intent before project-doc promotion:
     - Basic task: no project-doc update is required when the request does not change future allowed behavior.
     - Durable truth: promote the durable fact to the owning project doc before or with implementation.
     - Ambiguous truth change: ask before treating the fact as project truth.
   - Agent findings are not project truth unless they preserve existing documented intent, correct an owner doc under its change rule, or are confirmed by the user.
   - If implementation changes behavior, accepted inputs/outputs, purpose, boundaries, invariants, or project rules, update the owning doc before closure.
""".lstrip(),
            )

            errors = REPO_AND_GOVERNANCE.check_docs_first_prompt_classification(repo_root)

            self.assertEqual([], errors)

    def test_docs_first_prompt_classification_markers_fail_when_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = Path(tmp_dir)
            write_text(repo_root / "AGENTS.md", "# AGENTS\n")

            errors = REPO_AND_GOVERNANCE.check_docs_first_prompt_classification(repo_root)

            self.assertTrue(any("Basic task" in error for error in errors), errors)
            self.assertTrue(any("Durable truth" in error for error in errors), errors)
            self.assertTrue(any("Ambiguous truth change" in error for error in errors), errors)


if __name__ == "__main__":
    unittest.main()
