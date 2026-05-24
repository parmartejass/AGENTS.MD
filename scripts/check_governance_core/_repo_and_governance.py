from __future__ import annotations

import re
import subprocess
from pathlib import Path
from typing import List

try:
    from ._shared import GIT_LS_FILES_TIMEOUT_SEC
except ImportError:  # pragma: no cover - script-path execution
    from _shared import GIT_LS_FILES_TIMEOUT_SEC

TRACKED_SECRET_PATH_PATTERNS = (
    re.compile(r"(^|/)\.env($|\.local$|\.dev$|\.prod$|\.test$)", re.IGNORECASE),
    re.compile(r"(^|/)\.x_token\.json$", re.IGNORECASE),
    re.compile(
        r"(^|/)[^/]*(token|secret|credential|credentials)[^/]*\.(json|txt|env|ini|toml|yaml|yml)$",
        re.IGNORECASE,
    ),
)
UNRESOLVED_CITATION_PATTERNS = (
    "cite",
    "entity",
    "image_group",
)
RETIRED_ACTIVE_REFERENCE_PATTERNS = (
    "docs/agents/acp/",
    "docs/agents/automation/",
    "docs/agents/integrations/",
    "docs/generated/",
    "templates/automation-loop/",
    "templates/pr-control-plane/",
)
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


def check_docs_for_retired_active_references(repo_root: Path) -> List[str]:
    errors: List[str] = []
    docs_root = repo_root / "docs"
    if not docs_root.is_dir():
        return errors

    for doc_file in docs_root.rglob("*"):
        if not doc_file.is_file():
            continue
        rel_under_docs = doc_file.relative_to(docs_root)
        if "change-records" in rel_under_docs.parts:
            continue
        rel_path = doc_file.relative_to(repo_root).as_posix()
        try:
            text = doc_file.read_text(encoding="utf-8", errors="replace")
        except OSError as exc:
            errors.append(f"Failed to read docs file for retired-reference checks: {rel_path} ({exc})")
            continue
        for pattern in RETIRED_ACTIVE_REFERENCE_PATTERNS:
            if pattern in text:
                errors.append(
                    f"Retired path reference in active docs: {rel_path} contains {pattern}. "
                    "Move historical references to change records with the 'retired:' prefix."
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
        if stripped == "Hard gates:":
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
    canonical_heading = "## Hard gates (canonical; keep wording in sync)"
    prompt_heading = "## Prompt pack (copy/paste into any chat)"

    canonical_indices = [idx for idx, line in enumerate(lines) if line.strip() == canonical_heading]
    if len(canonical_indices) != 1:
        errors.append("Governance learnings playbook must contain exactly one canonical Hard gates section.")
        return errors

    prompt_indices = [idx for idx, line in enumerate(lines) if line.strip() == prompt_heading]
    if len(prompt_indices) != 1:
        errors.append("Governance learnings playbook must contain exactly one Prompt pack section.")
        return errors

    canonical_gates = _extract_hard_gates_from_playbook_block(lines, canonical_indices[0] + 1)
    prompt_gates = _extract_hard_gates_from_prompt_pack(lines, prompt_indices[0] + 1)

    if not canonical_gates:
        errors.append("Canonical Hard gates section is empty in governance learnings playbook.")
        return errors
    if not prompt_gates:
        errors.append("Prompt pack Hard gates block is missing or empty in governance learnings playbook.")
        return errors
    if canonical_gates != prompt_gates:
        errors.append(
            "Prompt pack Hard gates block does not match canonical Hard gates section in "
            "docs/agents/playbooks/governance-learnings-template/governance-learnings-template.md."
        )
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
