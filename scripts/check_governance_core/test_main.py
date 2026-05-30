from __future__ import annotations

import contextlib
import importlib.util
import io
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


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

CHANGE_RECORDS = _load_module("check_governance_core_change_records", SCRIPT_ROOT / "_change_records.py")
REPO_AND_GOVERNANCE = _load_module(
    "check_governance_core_repo_and_governance", SCRIPT_ROOT / "_repo_and_governance.py"
)
GOVERNANCE_RESEARCH = _load_module(
    "governance_autoresearch",
    REPO_ROOT / "X-Bookmarks Import/skills/governance-autoresearch/scripts/governance_research.py",
)

ACTIVE_RESEARCH_FILES = (
    "docs/agents/mcp/00-mcp-standards/mcp-standards.md",
    "docs/agents/platforms/00-platform-runtime-standards/platform-runtime-standards.md",
)


class ChangeRecordReferenceTests(unittest.TestCase):
    def test_readme_checks_reference_resolves_through_existing_readme(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = Path(tmp_dir)
            write_text(repo_root / "README.md", "# Checks\n")

            self.assertTrue(CHANGE_RECORDS._reference_target_exists(repo_root, "README.md#checks"))
            self.assertTrue(CHANGE_RECORDS._reference_target_exists(repo_root, ".governance/README.md#checks"))

    def test_readme_checks_reference_does_not_mask_missing_readme(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = Path(tmp_dir)

            self.assertFalse(CHANGE_RECORDS._reference_target_exists(repo_root, "README.md#checks"))

    def test_invalid_reference_targets_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = Path(tmp_dir)
            write_text(repo_root / "README.md", "# Checks\n")

            self.assertFalse(CHANGE_RECORDS._reference_target_exists(repo_root, "../README.md#checks"))
            self.assertFalse(CHANGE_RECORDS._reference_target_exists(repo_root, "/README.md#checks"))


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


class GovernanceResearchTests(unittest.TestCase):
    def test_governance_files_all_exist(self) -> None:
        missing_files = [
            rel_path
            for rel_path in GOVERNANCE_RESEARCH.GOVERNANCE_FILES
            if not (REPO_ROOT / rel_path).is_file()
        ]

        self.assertEqual([], missing_files)

    def test_active_runtime_authorities_have_curated_topics(self) -> None:
        for rel_path in ACTIVE_RESEARCH_FILES:
            with self.subTest(rel_path=rel_path):
                self.assertIn(rel_path, GOVERNANCE_RESEARCH.GOVERNANCE_FILES)
                self.assertIn(rel_path, GOVERNANCE_RESEARCH.FILE_TOPIC_MAP)
                self.assertEqual(
                    GOVERNANCE_RESEARCH.FILE_TOPIC_MAP[rel_path],
                    GOVERNANCE_RESEARCH.extract_topics(rel_path),
                )

    def test_list_surface_includes_active_runtime_authorities(self) -> None:
        with patch.object(sys, "argv", ["governance_research.py", "--list"]):
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                GOVERNANCE_RESEARCH.main()

        output = stdout.getvalue()
        for rel_path in ACTIVE_RESEARCH_FILES:
            with self.subTest(rel_path=rel_path):
                self.assertIn(f"[OK] {rel_path}", output)

    def test_list_surface_reports_registered_missing_files(self) -> None:
        missing_file = "docs/agents/missing-active-topic.md"
        with (
            patch.object(GOVERNANCE_RESEARCH, "GOVERNANCE_FILES", [missing_file]),
            patch.dict(GOVERNANCE_RESEARCH.FILE_TOPIC_MAP, {missing_file: ["missing topic"]}, clear=True),
            patch.object(sys, "argv", ["governance_research.py", "--list"]),
        ):
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                GOVERNANCE_RESEARCH.main()

        output = stdout.getvalue()
        self.assertIn(f"[MISSING] {missing_file}", output)
        self.assertIn("Topics: missing topic", output)


if __name__ == "__main__":
    unittest.main()
