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


class InstructionDerivationGateTests(unittest.TestCase):
    def _write_compliant_tree(self, governance_root: Path, *, include_body_noise: bool = False) -> None:
        body_noise = "\nThis body mentions memory, transcript, fallback, and temporary plan as non-authority examples.\n" if include_body_noise else ""
        write_text(
            governance_root / "AGENTS.md",
            """
### 1A) Instruction Derivation Gate (Hard Gate)
Classify each source before deriving obligations
Only a declared owner defines obligations.
User prompts provide intent, scope, and acceptance criteria.
Missing owner, conflicting owners, unknown optionality/defaultability, missing witness, or unclear precedence is an authority gap.
""".lstrip(),
        )
        write_text(
            governance_root / "docs/agents/20-sources-of-truth-map/sources-of-truth-map.md",
            "instruction derivation rules for prompts, plans, checklists, generated artifacts, and downstream scaffolds\n",
        )
        write_text(
            governance_root / "docs/agents/25-docs-ssot-policy/docs-ssot-policy.md",
            "Universal instruction derivation across prompts, plans, checklists, examples, generated artifacts, and downstream scaffolds is owned by `AGENTS.md`\n",
        )
        self._write_prompt_surface(
            governance_root / "docs/agents/playbooks/governance-learnings-template/governance-learnings-template.md",
            1,
            body_noise,
        )
        self._write_prompt_surface(
            governance_root / "docs/agents/playbooks/ai-coding-prompt-template/ai-coding-prompt-template.md",
            2,
            body_noise,
        )
        self._write_prompt_surface(
            governance_root / "docs/agents/15-stuck-in-loop-generate-fresh-restart-prompt/stuck-in-loop-generate-fresh-restart-prompt.md",
            2,
            body_noise,
        )

    def _write_prompt_surface(self, path: Path, count: int, body_noise: str) -> None:
        blocks = []
        for _index in range(count):
            blocks.append(
                f"""
```text
Hard gates (copy/paste scaffold sourced from AGENTS.md):
- Read and follow `AGENTS.md`; if it is inaccessible, request it before doing any work.
- {INSTRUCTION_DERIVATION.DERIVATION_SCAFFOLD}
```
{body_noise}
""".lstrip()
            )
        write_text(path, "\n".join(blocks))

    def test_compliant_instruction_derivation_scaffolds_pass(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            governance_root = Path(tmp_dir)
            self._write_compliant_tree(governance_root)

            errors = INSTRUCTION_DERIVATION.check_instruction_derivation_gate(governance_root)

            self.assertEqual([], errors)

    def test_body_terms_do_not_trigger_banned_word_scanning(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            governance_root = Path(tmp_dir)
            self._write_compliant_tree(governance_root, include_body_noise=True)

            errors = INSTRUCTION_DERIVATION.check_instruction_derivation_gate(governance_root)

            self.assertEqual([], errors)

    def test_rejects_missing_agents_owner_marker(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            governance_root = Path(tmp_dir)
            self._write_compliant_tree(governance_root)
            write_text(governance_root / "AGENTS.md", "### 1A) Instruction Derivation Gate (Hard Gate)\n")

            errors = INSTRUCTION_DERIVATION.check_instruction_derivation_gate(governance_root)

            self.assertTrue(any("AGENTS.md missing instruction-derivation marker" in error for error in errors), errors)

    def test_rejects_prompt_surface_missing_derivation_scaffold(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            governance_root = Path(tmp_dir)
            self._write_compliant_tree(governance_root)
            write_text(
                governance_root / "docs/agents/playbooks/ai-coding-prompt-template/ai-coding-prompt-template.md",
                """
```text
Hard gates (copy/paste scaffold sourced from AGENTS.md):
- Read and follow `AGENTS.md`; if it is inaccessible, request it before doing any work.
```
""".lstrip(),
            )

            errors = INSTRUCTION_DERIVATION.check_instruction_derivation_gate(governance_root)

            self.assertTrue(any("prompt scaffold block 1 missing instruction-derivation line" in error for error in errors), errors)

    def test_scaffold_line_outside_prompt_block_does_not_satisfy_block(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            governance_root = Path(tmp_dir)
            self._write_compliant_tree(governance_root)
            write_text(
                governance_root / "docs/agents/playbooks/ai-coding-prompt-template/ai-coding-prompt-template.md",
                f"""
```text
Hard gates (copy/paste scaffold sourced from AGENTS.md):
- Read and follow `AGENTS.md`; if it is inaccessible, request it before doing any work.
- {INSTRUCTION_DERIVATION.DERIVATION_SCAFFOLD}
```

```text
Hard gates (copy/paste scaffold sourced from AGENTS.md):
- Read and follow `AGENTS.md`; if it is inaccessible, request it before doing any work.
```

Outside a prompt block: {INSTRUCTION_DERIVATION.DERIVATION_SCAFFOLD}
""".lstrip(),
            )

            errors = INSTRUCTION_DERIVATION.check_instruction_derivation_gate(governance_root)

            self.assertTrue(any("prompt scaffold block 2 missing instruction-derivation line" in error for error in errors), errors)


if __name__ == "__main__":
    unittest.main()
