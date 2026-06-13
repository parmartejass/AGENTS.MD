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

REPO_AND_GOVERNANCE = _load_module(
    "check_governance_core_repo_and_governance_playbook_negative", SCRIPT_ROOT / "_repo_and_governance.py"
)


class GovernanceLearningPlaybookTests(unittest.TestCase):
    def _write_playbook_tree(self, repo_root: Path, playbook_body: str, handoff_body: str | None = None) -> None:
        playbook_dir = repo_root / "docs/agents/playbooks/governance-learnings-template"
        write_text(playbook_dir / "governance-learnings-template.md", playbook_body)
        if handoff_body is not None:
            write_text(playbook_dir / "codex-session-log-review.md", handoff_body)

    def test_governance_learning_playbook_rejects_canonical_hard_gate_copy(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = Path(tmp_dir)
            self._write_playbook_tree(
                repo_root,
                """
## Hard gates (canonical; keep wording in sync)
- Read and follow `AGENTS.md` (SSOT).

## Prompt pack (copy/paste into any chat)

```text
Hard gates:
- Read and follow `AGENTS.md` (SSOT).
```
""".lstrip(),
                "Evidence collection owner: this file.\n",
            )

            errors = REPO_AND_GOVERNANCE.check_governance_playbook_hard_gates(repo_root)

            self.assertTrue(
                any("must not maintain a canonical Hard gates section" in error for error in errors),
                errors,
            )

    def test_governance_learning_playbook_requires_noise_gate(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = Path(tmp_dir)
            self._write_playbook_tree(
                repo_root,
                """
## Authority References
- Global hard gates, council requirements, and governance auto-edit rules are owned by `AGENTS.md`.
- Context-routing facts are owned by `agents-manifest.yaml`; this playbook must not keep a local injected-doc list.
- Docs placement, router behavior, and non-owner-doc limits are owned by `docs/agents/25-docs-ssot-policy/docs-ssot-policy.md`.
- This playbook owns the promotion/noise gate, evidence record shape, and copy/paste prompt scaffold for governance-learning work.

## Prompt pack (copy/paste into any chat)

```text
Hard gates (copy/paste scaffold sourced from AGENTS.md):
- Read and follow `AGENTS.md`; if it is inaccessible, request it before doing any work.
- Execute the `AGENTS.md` Context Injection Procedure using the current `agents-manifest.yaml`.
- Execute the docs-first authority gate before any non-trivial plan, review, council output, implementation, or repo mutation.
- For governance auto-edit, apply the `AGENTS.md` Governance Auto-Edit Gate and Subagent Council before editing.
- Use docs placement and router rules from `docs/agents/25-docs-ssot-policy/docs-ssot-policy.md`; do not restate them here.
```
""".lstrip(),
                "Evidence collection owner: this file.\n",
            )

            errors = REPO_AND_GOVERNANCE.check_governance_playbook_hard_gates(repo_root)

            self.assertTrue(
                any("missing promotion/noise gate marker: ## Promotion / Noise Gate" in error for error in errors),
                errors,
            )

    def test_governance_learning_playbook_requires_handoff_leaf(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = Path(tmp_dir)
            self._write_playbook_tree(
                repo_root,
                """
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
- Use docs placement and router rules from `docs/agents/25-docs-ssot-policy/docs-ssot-policy.md`; do not restate them here.
```
""".lstrip(),
            )

            errors = REPO_AND_GOVERNANCE.check_governance_playbook_hard_gates(repo_root)

            self.assertTrue(
                any("Missing Codex session log evidence handoff playbook" in error for error in errors),
                errors,
            )

    def test_governance_learning_playbook_requires_scaffold_gates_inside_prompt_pack(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = Path(tmp_dir)
            self._write_playbook_tree(
                repo_root,
                """
## Authority References
- Global hard gates, council requirements, and governance auto-edit rules are owned by `AGENTS.md`.
- Context-routing facts are owned by `agents-manifest.yaml`; this playbook must not keep a local injected-doc list.
- Docs placement, router behavior, and non-owner-doc limits are owned by `docs/agents/25-docs-ssot-policy/docs-ssot-policy.md`.
- This playbook owns the promotion/noise gate, evidence record shape, and copy/paste prompt scaffold for governance-learning work.

Required elsewhere but not in prompt:
- Execute the `AGENTS.md` Context Injection Procedure using the current `agents-manifest.yaml`.
- Execute the docs-first authority gate before any non-trivial plan, review, council output, implementation, or repo mutation.
- For governance auto-edit, apply the `AGENTS.md` Governance Auto-Edit Gate and Subagent Council before editing.
- Use docs placement and router rules from `docs/agents/25-docs-ssot-policy/docs-ssot-policy.md`; do not restate them here.

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
```
""".lstrip(),
            )

            errors = REPO_AND_GOVERNANCE.check_governance_playbook_hard_gates(repo_root)

            self.assertTrue(
                any("prompt pack missing scaffold gate" in error for error in errors),
                errors,
            )

    def test_subagent_council_profile_coverage_requires_agents_and_playbook_markers(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = Path(tmp_dir)
            write_text(
                repo_root / "AGENTS.md",
                """
## Subagent Council (Hard Gate)
### Profile-Aware Context Coverage
After the Context Injection Procedure resolves matched profiles and injected files from `agents-manifest.yaml`, council planning must account for that manifest-resolution witness.
Profile-aware coverage is required when any of these are true:
one or more manifest profiles match and any resolved injected docs are decision-critical to planning or review
Coverage may be one subagent per matched profile, or fewer subagents when one reviewer is explicitly assigned multiple profiles. The merged council summary must make the profile-to-reviewer/doc mapping auditable. Do not copy profile names or injected doc lists into this policy.
If a required profile doc or required reviewer/runtime path is unavailable, record `SKIPPED`/`UNKNOWN` + reason in `profile_doc_coverage` and set `go_no_go = hold` unless the user explicitly accepts reduced coverage.
""".lstrip(),
            )
            write_text(
                repo_root / "docs/agents/playbooks/governance-learnings-template/governance-learnings-template.md",
                """
Council summary block (required before Step 4; follow `AGENTS.md` "Subagent Council (Hard Gate)"):
- profile_doc_coverage (when `AGENTS.md` Profile-Aware Context Coverage applies):
""".lstrip(),
            )

            errors = REPO_AND_GOVERNANCE.check_subagent_council_profile_coverage(repo_root)

            self.assertEqual([], errors)

    def test_subagent_council_profile_coverage_rejects_missing_playbook_marker(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = Path(tmp_dir)
            write_text(
                repo_root / "AGENTS.md",
                """
## Subagent Council (Hard Gate)
### Profile-Aware Context Coverage
After the Context Injection Procedure resolves matched profiles and injected files from `agents-manifest.yaml`, council planning must account for that manifest-resolution witness.
Profile-aware coverage is required when any of these are true:
one or more manifest profiles match and any resolved injected docs are decision-critical to planning or review
Coverage may be one subagent per matched profile, or fewer subagents when one reviewer is explicitly assigned multiple profiles. The merged council summary must make the profile-to-reviewer/doc mapping auditable. Do not copy profile names or injected doc lists into this policy.
If a required profile doc or required reviewer/runtime path is unavailable, record `SKIPPED`/`UNKNOWN` + reason in `profile_doc_coverage` and set `go_no_go = hold` unless the user explicitly accepts reduced coverage.
""".lstrip(),
            )
            write_text(
                repo_root / "docs/agents/playbooks/governance-learnings-template/governance-learnings-template.md",
                "Council summary block:\n",
            )

            errors = REPO_AND_GOVERNANCE.check_subagent_council_profile_coverage(repo_root)

            self.assertTrue(
                any("missing profile_doc_coverage marker" in error for error in errors),
                errors,
            )

    def test_subagent_council_profile_coverage_rejects_missing_single_profile_trigger(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = Path(tmp_dir)
            write_text(
                repo_root / "AGENTS.md",
                """
## Subagent Council (Hard Gate)
### Profile-Aware Context Coverage
After the Context Injection Procedure resolves matched profiles and injected files from `agents-manifest.yaml`, council planning must account for that manifest-resolution witness.
Profile-aware coverage is required when any of these are true:
Coverage may be one subagent per matched profile, or fewer subagents when one reviewer is explicitly assigned multiple profiles. The merged council summary must make the profile-to-reviewer/doc mapping auditable. Do not copy profile names or injected doc lists into this policy.
If a required profile doc or required reviewer/runtime path is unavailable, record `SKIPPED`/`UNKNOWN` + reason in `profile_doc_coverage` and set `go_no_go = hold` unless the user explicitly accepts reduced coverage.
""".lstrip(),
            )
            write_text(
                repo_root / "docs/agents/playbooks/governance-learnings-template/governance-learnings-template.md",
                """
Council summary block (required before Step 4; follow `AGENTS.md` "Subagent Council (Hard Gate)"):
- profile_doc_coverage (when `AGENTS.md` Profile-Aware Context Coverage applies):
""".lstrip(),
            )

            errors = REPO_AND_GOVERNANCE.check_subagent_council_profile_coverage(repo_root)

            self.assertTrue(
                any("one or more manifest profiles match" in error for error in errors),
                errors,
            )

    def test_subagent_council_profile_coverage_rejects_missing_no_duplication_guard(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = Path(tmp_dir)
            write_text(
                repo_root / "AGENTS.md",
                """
## Subagent Council (Hard Gate)
### Profile-Aware Context Coverage
After the Context Injection Procedure resolves matched profiles and injected files from `agents-manifest.yaml`, council planning must account for that manifest-resolution witness.
Profile-aware coverage is required when any of these are true:
one or more manifest profiles match and any resolved injected docs are decision-critical to planning or review
Coverage may be one subagent per matched profile, or fewer subagents when one reviewer is explicitly assigned multiple profiles. The merged council summary must make the profile-to-reviewer/doc mapping auditable.
If a required profile doc or required reviewer/runtime path is unavailable, record `SKIPPED`/`UNKNOWN` + reason in `profile_doc_coverage` and set `go_no_go = hold` unless the user explicitly accepts reduced coverage.
""".lstrip(),
            )
            write_text(
                repo_root / "docs/agents/playbooks/governance-learnings-template/governance-learnings-template.md",
                """
Council summary block (required before Step 4; follow `AGENTS.md` "Subagent Council (Hard Gate)"):
- profile_doc_coverage (when `AGENTS.md` Profile-Aware Context Coverage applies):
""".lstrip(),
            )

            errors = REPO_AND_GOVERNANCE.check_subagent_council_profile_coverage(repo_root)

            self.assertTrue(
                any("Do not copy profile names" in error for error in errors),
                errors,
            )

    def test_subagent_council_profile_coverage_rejects_missing_unavailable_context_guard(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = Path(tmp_dir)
            write_text(
                repo_root / "AGENTS.md",
                """
## Subagent Council (Hard Gate)
### Profile-Aware Context Coverage
After the Context Injection Procedure resolves matched profiles and injected files from `agents-manifest.yaml`, council planning must account for that manifest-resolution witness.
Profile-aware coverage is required when any of these are true:
one or more manifest profiles match and any resolved injected docs are decision-critical to planning or review
Coverage may be one subagent per matched profile, or fewer subagents when one reviewer is explicitly assigned multiple profiles. The merged council summary must make the profile-to-reviewer/doc mapping auditable. Do not copy profile names or injected doc lists into this policy.
If profile context is unavailable, record the reduced scope in `profile_doc_coverage` and set `go_no_go = hold` unless the user explicitly accepts reduced coverage.
""".lstrip(),
            )
            write_text(
                repo_root / "docs/agents/playbooks/governance-learnings-template/governance-learnings-template.md",
                """
Council summary block (required before Step 4; follow `AGENTS.md` "Subagent Council (Hard Gate)"):
- profile_doc_coverage (when `AGENTS.md` Profile-Aware Context Coverage applies):
""".lstrip(),
            )

            errors = REPO_AND_GOVERNANCE.check_subagent_council_profile_coverage(repo_root)

            self.assertTrue(
                any("required profile doc or required reviewer/runtime path" in error for error in errors),
                errors,
            )
            self.assertTrue(
                any("`SKIPPED`/`UNKNOWN` + reason" in error for error in errors),
                errors,
            )

if __name__ == "__main__":
    unittest.main()
