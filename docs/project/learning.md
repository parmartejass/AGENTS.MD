---
doc_type: runbook
ssot_owner: AGENTS.md
update_trigger: new operational learnings/pitfalls discovered in real use
---

# Learning Notes

## Common pitfalls
- Python may not be runnable on some machines (Windows Store app aliases). Ensure `python` resolves correctly so `scripts/check_python_safety.py` can run.
- Generated artifacts (e.g., `__pycache__/`, `*.pyc`, template outputs) must not be committed.

## Nia runtime gotchas (2026-03-06)
- This repo already projects the canonical Nia skill into `.agents/skills/nia`; a missing `bash` command on `PATH` does not mean Nia is absent from the repo.
- This repo may keep `NIA_API_KEY` in `.env`; PowerShell/harness sessions do not necessarily auto-load `.env` into the current process environment.
- On Windows, Git Bash may exist at an explicit path even when `bash` is not on `PATH`; the bundled Nia `.sh` scripts still require `jq`.
- If Nia is relevant and the shell-script wrapper path is unavailable, verify the connection with a direct authenticated API smoke test before declaring Nia unavailable or falling back to non-Nia search.
- Never echo or log the Nia secret while performing that verification.

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
- For Nia connectivity, load `NIA_API_KEY` from the approved secret source without echoing it and expect a successful response from `https://apigcp.trynia.ai/v2/usage` before declaring the integration unavailable.

## Debugging references
- Use `AGENTS.md` "Bias-Resistant Debugging" and "AI Stuck-Loop Reset" for evidence-driven fixes.
