---
doc_type: runbook
ssot_owner: AGENTS.md
update_trigger: new operational learnings/pitfalls discovered in real use
---

# Learning Notes

## Common pitfalls
- Python may not be runnable on some machines (Windows Store app aliases); prefer deterministic PowerShell checks when possible.
- Generated artifacts (e.g., `__pycache__/`, `*.pyc`, template outputs) must not be committed.

## Verification tips
- If a repo adopts this pack, run `scripts/check_project_docs.ps1` early to ensure docs+README linkage is in place.
