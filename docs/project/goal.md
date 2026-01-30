---
doc_type: reference
ssot_owner: AGENTS.md
update_trigger: repo objective, structure, or required checks change
---

# Goal

## Objective
- Maintain a reusable, repo-agnostic governance pack for autonomous coding agents.

## Acceptance criteria
- Governance SSOT is `AGENTS.md` and remains authoritative.
- Context injection remains deterministic via `agents-manifest.yaml`.
- Repo checks pass:
  - `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/check_agents_manifest.ps1`
  - `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/check_docs_ssot.ps1`
  - `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/check_project_docs.ps1`
  - `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/check_repo_hygiene.ps1`
  - `python scripts/check_python_safety.py`

## Non-goals
- This repo does not define domain business logic; templates are reference implementations only.

## Verification
- Run the checks listed in "Acceptance criteria".
