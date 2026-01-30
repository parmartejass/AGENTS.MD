---
doc_type: runbook
ssot_owner: AGENTS.md
update_trigger: new operational learnings/pitfalls discovered in real use
---

# Learning Notes

## Common pitfalls
- Python may not be runnable on some machines (Windows Store app aliases). Ensure `python` resolves correctly so `scripts/check_python_safety.py` can run.
- Generated artifacts (e.g., `__pycache__/`, `*.pyc`, template outputs) must not be committed.

## Verification tips
- If a repo adopts this pack, run `.governance/scripts/check_project_docs.ps1 -RepoRoot .` early to ensure docs+README linkage is in place.

## Debugging references
- Use `AGENTS.md` "Bias-Resistant Debugging" and "AI Stuck-Loop Reset" for evidence-driven fixes.
