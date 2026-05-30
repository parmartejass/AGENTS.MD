from __future__ import annotations

from pathlib import Path
from typing import List, Tuple


DERIVATION_SCAFFOLD = (
    "Derive task instructions from declared SSOT owners; if ownership is unknown or conflicting, "
    "stop and report the authority gap before acting."
)

PROMPT_SCAFFOLD_SURFACES: Tuple[Tuple[str, int], ...] = (
    ("docs/agents/playbooks/governance-learnings-template/governance-learnings-template.md", 1),
    ("docs/agents/playbooks/ai-coding-prompt-template/ai-coding-prompt-template.md", 2),
    ("docs/agents/15-stuck-in-loop-generate-fresh-restart-prompt/stuck-in-loop-generate-fresh-restart-prompt.md", 2),
)
SCAFFOLD_LABEL = "Hard gates (copy/paste scaffold sourced from AGENTS.md):"


def _extract_scaffold_blocks(text: str) -> List[str]:
    lines = text.splitlines()
    blocks: List[str] = []
    for index, line in enumerate(lines):
        if line.strip() != SCAFFOLD_LABEL:
            continue
        block_lines: List[str] = []
        for next_line in lines[index + 1 :]:
            stripped = next_line.strip()
            if stripped.startswith("```"):
                break
            if block_lines and not stripped.startswith("- "):
                break
            if stripped.startswith("- "):
                block_lines.append(stripped)
        blocks.append("\n".join(block_lines))
    return blocks


def check_instruction_derivation_gate(governance_root: Path) -> List[str]:
    errors: List[str] = []
    agents = governance_root / "AGENTS.md"
    if not agents.is_file():
        return [f"Missing AGENTS.md at governance root: {agents}"]

    agents_text = agents.read_text(encoding="utf-8")
    required_agents_markers = (
        "### 1A) Instruction Derivation Gate (Hard Gate)",
        "Classify each source before deriving obligations",
        "Only a declared owner defines obligations.",
        "User prompts provide intent, scope, and acceptance criteria.",
        "Missing owner, conflicting owners, unknown optionality/defaultability, missing witness, or unclear precedence is an authority gap.",
    )
    for marker in required_agents_markers:
        if marker not in agents_text:
            errors.append(f"AGENTS.md missing instruction-derivation marker: {marker}")

    source_map = governance_root / "docs/agents/20-sources-of-truth-map/sources-of-truth-map.md"
    if source_map.is_file():
        source_map_text = source_map.read_text(encoding="utf-8")
        if "instruction derivation rules for prompts, plans, checklists, generated artifacts, and downstream scaffolds" not in source_map_text:
            errors.append("Sources-of-truth map must route instruction derivation to AGENTS.md.")
    else:
        errors.append(f"Missing sources-of-truth map: {source_map}")

    docs_policy = governance_root / "docs/agents/25-docs-ssot-policy/docs-ssot-policy.md"
    if docs_policy.is_file():
        docs_policy_text = docs_policy.read_text(encoding="utf-8")
        if "Universal instruction derivation across prompts, plans, checklists, examples, generated artifacts, and downstream scaffolds is owned by `AGENTS.md`" not in docs_policy_text:
            errors.append("Docs SSOT policy must route universal instruction derivation to AGENTS.md.")
    else:
        errors.append(f"Missing docs SSOT policy: {docs_policy}")

    for rel_path, minimum_count in PROMPT_SCAFFOLD_SURFACES:
        path = governance_root / rel_path
        if not path.is_file():
            errors.append(f"Missing prompt scaffold surface: {rel_path}")
            continue
        text = path.read_text(encoding="utf-8")
        if "Hard gates (canonical; keep wording in sync)" in text:
            errors.append(f"{rel_path} must not keep a local canonical hard-gates section.")
        scaffold_blocks = _extract_scaffold_blocks(text)
        if len(scaffold_blocks) < minimum_count:
            errors.append(
                f"{rel_path} must label each prompt hard-gates block as a copy/paste scaffold sourced from AGENTS.md."
            )
        for block_index, block in enumerate(scaffold_blocks, start=1):
            if DERIVATION_SCAFFOLD not in block:
                errors.append(f"{rel_path} prompt scaffold block {block_index} missing instruction-derivation line.")

    return errors
