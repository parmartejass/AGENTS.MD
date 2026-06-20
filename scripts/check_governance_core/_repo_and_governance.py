from __future__ import annotations

import re
import subprocess
from pathlib import Path
from typing import List

try:
    from ._instruction_derivation import DERIVATION_SCAFFOLD
    from ._shared import GIT_LS_FILES_TIMEOUT_SEC
except ImportError:  # pragma: no cover - script-path execution
    from _instruction_derivation import DERIVATION_SCAFFOLD
    from _shared import GIT_LS_FILES_TIMEOUT_SEC

TRACKED_SECRET_PATH_PATTERNS = (
    re.compile(r"(^|/)\.env($|\.local$|\.dev$|\.prod$|\.test$)", re.IGNORECASE),
    re.compile(r"(^|/)\.x_token\.json$", re.IGNORECASE),
    re.compile(
        r"(^|/)[^/]*(token|secret|credential|credentials)[^/]*\.(json|txt|env|ini|toml|yaml|yml)$",
        re.IGNORECASE,
    ),
)
UNRESOLVED_CITATION_PATTERNS = ("cite", "entity", "image_group")


def check_repo_hygiene(repo_root: Path) -> List[str]:
    errors: List[str] = []
    if not (repo_root / ".git").exists():
        return [f"Repo root does not appear to be a git repository: {repo_root}"]

    try:
        result = subprocess.run(
            ["git", "-C", str(repo_root), "ls-files"],
            check=True,
            capture_output=True,
            text=True,
            cwd=repo_root,
            timeout=GIT_LS_FILES_TIMEOUT_SEC,
        )
    except FileNotFoundError:
        return ["git is required for hygiene checks."]
    except subprocess.TimeoutExpired:
        return [f"git ls-files timed out after {GIT_LS_FILES_TIMEOUT_SEC}s for repo root: {repo_root}"]
    except subprocess.CalledProcessError as exc:
        details = " ".join(part.strip() for part in (exc.stderr, exc.stdout) if part and part.strip())
        if details:
            return [f"git ls-files failed for repo root: {repo_root}: {details[:500]}"]
        return [f"git ls-files failed for repo root: {repo_root}"]

    for raw in result.stdout.splitlines():
        path = raw.strip()
        if not path:
            continue
        norm = path.replace("\\", "/")

        if re.search(r"(^|/)__pycache__(/|$)", norm):
            errors.append(f"Tracked Python cache dir/file: {path}")
            continue
        if norm.endswith(".pyc") or norm.endswith(".pyo"):
            errors.append(f"Tracked Python bytecode: {path}")
            continue
        if re.search(r"(^|/)\.DS_Store$", norm) or re.search(r"(^|/)Thumbs\.db$", norm):
            errors.append(f"Tracked OS noise file: {path}")
            continue
        if norm.startswith("templates/python-dual-entry/tests/output/") and (
            norm != "templates/python-dual-entry/tests/output/.gitkeep"
        ):
            errors.append(
                "Tracked template runtime output file (must be ignored; "
                f"docs/generated/ governance artifacts are allowed): {path}"
            )
            continue
        if norm.startswith("X-Bookmarks Import/data/"):
            errors.append(f"Tracked secret-like or workspace-local file: {path}")
            continue
        if any(pattern.search(norm) for pattern in TRACKED_SECRET_PATH_PATTERNS):
            errors.append(f"Tracked secret-like or workspace-local file: {path}")
            continue

    return errors


def check_docs_for_unresolved_citations(repo_root: Path) -> List[str]:
    errors: List[str] = []
    docs_root = repo_root / "docs"
    if not docs_root.is_dir():
        return errors

    for md_file in docs_root.rglob("*.md"):
        try:
            lines = md_file.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError as exc:
            errors.append(f"Failed to read docs file for citation checks: {md_file} ({exc})")
            continue

        for line_no, line in enumerate(lines, start=1):
            if any(marker in line for marker in UNRESOLVED_CITATION_PATTERNS):
                rel = md_file.relative_to(repo_root).as_posix()
                errors.append(
                    f"Unresolved citation token in {rel}:{line_no}. "
                    "Replace `cite`/`entity`/`image_group` markers with resolvable references."
                )

    return errors


def _extract_hard_gates_from_playbook_block(lines: List[str], start_idx: int) -> List[str]:
    gates: List[str] = []
    for index in range(start_idx, len(lines)):
        stripped = lines[index].strip()
        if stripped.startswith("## "):
            break
        if stripped.startswith("- "):
            gates.append(stripped[2:].strip())
    return gates


def _extract_hard_gates_from_prompt_pack(lines: List[str], start_idx: int) -> List[str]:
    in_code_block = False
    in_hard_gate_section = False
    gates: List[str] = []

    for index in range(start_idx, len(lines)):
        stripped = lines[index].strip()
        if stripped.startswith("## ") and index > start_idx:
            break
        if stripped.startswith("```"):
            in_code_block = not in_code_block
            continue
        if not in_code_block:
            continue
        if stripped == "Hard gates:" or stripped.startswith("Hard gates ("):
            in_hard_gate_section = True
            continue
        if not in_hard_gate_section:
            continue
        if stripped.startswith("- "):
            gates.append(stripped[2:].strip())
            continue
        if gates and (stripped == "" or not stripped.startswith("- ")):
            break

    return gates


def check_governance_playbook_hard_gates(governance_root: Path) -> List[str]:
    errors: List[str] = []
    playbook = governance_root / "docs/agents/playbooks/governance-learnings-template/governance-learnings-template.md"
    evidence_handoff = governance_root / "docs/agents/playbooks/governance-learnings-template/codex-session-log-review.md"
    if not playbook.is_file():
        return [f"Missing governance learnings playbook: {playbook}"]
    if not evidence_handoff.is_file():
        errors.append(f"Missing Codex session log evidence handoff playbook: {evidence_handoff}")

    lines = playbook.read_text(encoding="utf-8").splitlines()
    playbook_text = "\n".join(lines)
    forbidden_canonical_heading = "## Hard gates (canonical; keep wording in sync)"
    authority_heading = "## Authority References"
    prompt_heading = "## Prompt pack (copy/paste into any chat)"

    if forbidden_canonical_heading in playbook_text:
        errors.append(
            "Governance learnings playbook must not maintain a canonical Hard gates section; "
            "use Authority References plus a minimal copy/paste scaffold."
        )

    authority_indices = [idx for idx, line in enumerate(lines) if line.strip() == authority_heading]
    if len(authority_indices) != 1:
        errors.append("Governance learnings playbook must contain exactly one Authority References section.")

    prompt_indices = [idx for idx, line in enumerate(lines) if line.strip() == prompt_heading]
    if len(prompt_indices) != 1:
        errors.append("Governance learnings playbook must contain exactly one Prompt pack section.")
        return errors

    prompt_gates = _extract_hard_gates_from_prompt_pack(lines, prompt_indices[0] + 1)
    prompt_section_lines: List[str] = []
    for index in range(prompt_indices[0] + 1, len(lines)):
        if lines[index].strip().startswith("## "):
            break
        prompt_section_lines.append(lines[index])
    prompt_section_text = "\n".join(prompt_section_lines)

    required_authority_markers = (
        "Global hard gates, council requirements, and governance auto-edit rules are owned by `AGENTS.md`.",
        "Context-routing facts are owned by `agents-manifest.yaml`; this playbook must not keep a local injected-doc list.",
        "Docs placement, router behavior, and non-owner-doc limits are owned by `docs/agents/25-docs-ssot-policy/docs-ssot-policy.md`.",
        "This playbook owns the promotion/noise gate, evidence record shape, and copy/paste prompt scaffold for governance-learning work.",
    )
    for marker in required_authority_markers:
        if marker not in playbook_text:
            errors.append(f"Governance learnings playbook missing authority-reference marker: {marker}")

    if not prompt_gates:
        errors.append("Prompt pack Hard gates block is missing or empty in governance learnings playbook.")
        return errors
    if "Hard gates (copy/paste scaffold sourced from AGENTS.md):" not in prompt_section_text:
        errors.append(
            "Governance learnings playbook prompt pack must label hard gates as "
            "copy/paste scaffold sourced from AGENTS.md."
        )
    required_prompt_scaffold_gates = (
        "Read and follow `AGENTS.md`; if it is inaccessible, request it before doing any work.",
        "Execute the `AGENTS.md` Context Injection Procedure using the current `agents-manifest.yaml`.",
        "Execute the docs-first authority gate before any non-trivial plan, review, council output, implementation, or repo mutation.",
        "For governance auto-edit, apply the `AGENTS.md` Governance Auto-Edit Gate and Subagent Council before editing.",
        DERIVATION_SCAFFOLD,
        "Use docs placement and router rules from `docs/agents/25-docs-ssot-policy/docs-ssot-policy.md`; do not restate them here.",
    )
    for marker in required_prompt_scaffold_gates:
        if marker not in prompt_gates:
            errors.append(f"Governance learnings playbook prompt pack missing scaffold gate: {marker}")
    required_noise_gate_markers = (
        "## Promotion / Noise Gate",
        "PROMOTE_FOR_DEDUP",
        "DEFER_EVIDENCE_GAP",
        "REJECT_TASK_LOCAL",
        "REJECT_TOOL_BUDGET",
        "REJECT_TEMPORARY_EXECUTION_PREFERENCE",
        "REJECT_WEAK_EVIDENCE",
        "REJECT_CONFLICTS_WITH_SSOT",
        "REJECT_NON_GOVERNANCE",
        "Rejected candidates must include evidence, gate status, and rejection reason.",
        "must not emit draft governance deltas",
        "Target location: N/A + rejected",
        "Example rejection:",
        "REJECT_CONFLICTS_WITH_SSOT",
    )
    for marker in required_noise_gate_markers:
        if marker not in playbook_text:
            errors.append(f"Governance learnings playbook missing promotion/noise gate marker: {marker}")

    if evidence_handoff.is_file():
        evidence_text = evidence_handoff.read_text(encoding="utf-8")
        required_handoff_markers = (
            "Evidence collection owner: this file.",
            "Governance promotion/rejection owner: `governance-learnings-template.md` Promotion / Noise Gate.",
            "Do not encode concept-specific search terms in this playbook.",
            "Use only user-provided or user-approved log roots.",
            "max files:",
            "max bytes per file:",
            "max total bytes:",
            "max runtime seconds:",
            "PARTIAL_SEARCH",
            "budget_limits_hit",
            "FOUND",
            "NOT_FOUND_AFTER_COMPLETE_SEARCH",
            "PARTIAL_SEARCH",
            "INACCESSIBLE",
            "UNPARSEABLE",
            "AMBIGUOUS_TIMEFRAME",
            "This playbook ends after evidence handoff.",
        )
        for marker in required_handoff_markers:
            if marker not in evidence_text:
                errors.append(f"Codex session log handoff playbook missing required marker: {marker}")
    return errors


def check_subagent_council_profile_coverage(governance_root: Path) -> List[str]:
    errors: List[str] = []
    agents_path = governance_root / "AGENTS.md"
    playbook_path = governance_root / "docs/agents/playbooks/governance-learnings-template/governance-learnings-template.md"

    if not agents_path.is_file():
        return [f"Missing AGENTS.md for subagent council profile-coverage checks: {agents_path}"]

    agents_text = agents_path.read_text(encoding="utf-8")
    required_agents_markers = (
        "### Profile-Aware Context Coverage",
        "After the Context Injection Procedure resolves matched profiles and injected files from `agents-manifest.yaml`",
        "Profile-aware coverage is required when any of these are true:",
        "one or more manifest profiles match and any resolved injected docs are decision-critical to planning or review",
        "one subagent per matched profile, or fewer subagents",
        "profile-to-reviewer/doc mapping",
        "Do not copy profile names or injected doc lists into this policy",
        "If a required profile doc or required reviewer/runtime path is unavailable",
        "record `SKIPPED`/`UNKNOWN` + reason",
        "`profile_doc_coverage`",
        "set `go_no_go = hold` unless the user explicitly accepts reduced coverage",
    )
    for marker in required_agents_markers:
        if marker not in agents_text:
            errors.append(f"AGENTS.md missing Subagent Council profile-coverage marker: {marker}")

    if not playbook_path.is_file():
        errors.append(f"Missing governance learnings playbook for profile-coverage checks: {playbook_path}")
        return errors

    playbook_text = playbook_path.read_text(encoding="utf-8")
    required_playbook_marker = (
        "- profile_doc_coverage (when `AGENTS.md` Profile-Aware Context Coverage applies):"
    )
    if required_playbook_marker not in playbook_text:
        errors.append(
            "Governance learnings playbook council summary block missing profile_doc_coverage marker."
        )

    return errors


def check_docs_first_prompt_classification(governance_root: Path) -> List[str]:
    agents_path = governance_root / "AGENTS.md"
    if not agents_path.is_file():
        return [f"Missing AGENTS.md for docs-first prompt classification checks: {agents_path}"]

    agents_text = agents_path.read_text(encoding="utf-8")
    required_markers = (
        "Classify user intent before project-doc promotion:",
        "Basic task: no project-doc update is required when the request does not change future allowed behavior.",
        "Durable truth: promote the durable fact to the owning project doc before or with implementation.",
        "Ambiguous truth change: ask before treating the fact as project truth.",
        "Agent findings are not project truth unless they preserve existing documented intent, correct an owner doc under its change rule, or are confirmed by the user.",
        "If implementation changes behavior, accepted inputs/outputs, purpose, boundaries, invariants, or project rules, update the owning doc before closure.",
    )
    return [
        f"AGENTS.md missing docs-first prompt-classification marker: {marker}"
        for marker in required_markers
        if marker not in agents_text
    ]


def check_governance_authority_decisions(governance_root: Path) -> List[str]:
    errors: List[str] = []
    concept_map_rel = "docs/agents/20-sources-of-truth-map/sources-of-truth-map.md"
    registry_entry_rel = "docs/agents/22-ssot-authority-decisions/ssot-authority-decisions_index.md"
    registry_doc_rel = "docs/agents/22-ssot-authority-decisions/ssot-authority-decisions.md"
    registry_path = governance_root / registry_doc_rel
    if not registry_path.is_file():
        return [f"Missing governance authority decision registry: {registry_path}"]

    agents_path = governance_root / "AGENTS.md"
    if not agents_path.is_file():
        errors.append(f"Missing required governance file for authority decision checks: {agents_path}")
    else:
        agents_text = agents_path.read_text(encoding="utf-8")
        if concept_map_rel not in agents_text:
            errors.append(f"AGENTS.md must reference {concept_map_rel}")

    registry_text = registry_path.read_text(encoding="utf-8")
    for marker in ("## Scope", "## Entry Contract", "## Active Decisions"):
        if marker not in registry_text:
            errors.append(f"Governance authority decision registry missing required section '{marker}'.")

    required_refs = [
        ("docs/agents/agents_index.md", governance_root / "docs/agents/agents_index.md", registry_entry_rel),
        (concept_map_rel, governance_root / concept_map_rel, registry_doc_rel),
    ]
    for label, path, required_ref in required_refs:
        if not path.is_file():
            errors.append(f"Missing required governance file for authority decision checks: {path}")
            continue
        if required_ref not in path.read_text(encoding="utf-8"):
            errors.append(f"{label} must reference {required_ref}")

    return errors
