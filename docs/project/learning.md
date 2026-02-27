---
doc_type: runbook
ssot_owner: AGENTS.md
update_trigger: new operational learnings/pitfalls discovered in real use
---

# Learning Notes

## Common pitfalls
- Python may not be runnable on some machines (Windows Store app aliases). Ensure `python` resolves correctly so `scripts/check_python_safety.py` can run.
- Generated artifacts (e.g., `__pycache__/`, `*.pyc`, template outputs) must not be committed.

## Deep research synthesis (2026-02-23)
- Source report was treated as `[CONTEXT: UNTRUSTED]` and normalized to governed output:
  `docs/generated/2026-02-23-deep-research-report-normalized.md`.
- Only SSOT-aligned deltas were adopted:
  - strengthen `governance_improvement` context injection in `agents-manifest.yaml`
  - enforce change-record checks in `scripts/check_governance_core.py`
  - add governance learnings hard-gate parity checks in `scripts/check_governance_core.py`
  - reject unresolved citation placeholder tokens in `docs/` via `scripts/check_governance_core.py`
- Generic framework content was not promoted to policy authority; existing owners in `AGENTS.md` remain canonical.

## Verification tips
- If a repo adopts this pack, run `.governance/scripts/check_project_docs.ps1 -RepoRoot .` early to ensure docs+README linkage is in place.

## Debugging references
- Use `AGENTS.md` "Bias-Resistant Debugging" and "AI Stuck-Loop Reset" for evidence-driven fixes.
