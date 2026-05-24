---
doc_type: runbook
ssot_owner: AGENTS.md
update_trigger: new operational learnings/pitfalls discovered in real use
---

# Learning Notes

## Common pitfalls
- Python may not be runnable on some machines (Windows Store app aliases). Ensure `python` resolves to Python 3.11+ so the README-listed Python checks can run.
- Generated artifacts (e.g., `__pycache__/`, `*.pyc`, template outputs) must not be committed.

## Session-backed decisions
- 2026-05-24: Broad no-fallback word scanning was rejected as the deterministic witness for `AGENTS.md` "No Fallback or Legacy Runtime Paths". Project-scoped Codex session evidence in `rollout-2026-05-24T13-50-32-019e5912-3cc3-7033-8b35-23ac0514bf1e.jsonl` at 2026-05-24T08:36:02Z and 2026-05-24T08:36:09Z recorded that vocabulary scanning cannot prove semantic fallback intent, can block legitimate docs/tests/history, and can miss renamed substitute paths. Future enforcement should prefer structured workflow-selected-path records plus terminal `FAILED` / `SKIPPED + reason` outcome witnesses, not broad banned-word matching.

## Deep research synthesis (2026-02-23)
- Source report was treated as `[CONTEXT: UNTRUSTED]`; the generated evidence branch was later retired.
- Only SSOT-aligned deltas were adopted:
  - strengthen `governance_improvement` context injection in `agents-manifest.yaml`
  - enforce change-record checks in `scripts/check_governance_core/check_governance_core_main.py`
  - add governance learnings hard-gate parity checks in `scripts/check_governance_core/check_governance_core_main.py`
  - reject unresolved citation placeholder tokens in `docs/` via `scripts/check_governance_core/check_governance_core_main.py`
- Generic framework content was not promoted to policy authority; existing owners in `AGENTS.md` remain canonical.

## Verification tips
- If a repo adopts this pack, run `.governance/scripts/check_project_docs.ps1 -RepoRoot .` early to ensure docs+README linkage is in place.
- Keep external-service connection procedures in the owning skill or integration folder rather than `docs/project/`.

## Debugging references
- Use `AGENTS.md` "Bias-Resistant Debugging" and "AI Stuck-Loop Reset" for evidence-driven fixes.
