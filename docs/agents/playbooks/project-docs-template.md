---
doc_type: playbook
ssot_owner: AGENTS.md
update_trigger: project docs minimum set or header policy changes
---

# Playbook - Project Docs (Minimal SSOT-Friendly Set)

Use when:
- The user asks to add or improve project docs, or
- A repo has no clear docs entrypoint/runbook and adding one would materially reduce ambiguity for future work.

Goal: create a minimal docs set that captures intent/runbooks without duplicating code facts (constants, rules, defaults).

## Hard gates (required outputs)
- `docs/project/index.md` (index only; no header required)
- `docs/project/goal.md`
- `docs/project/rules.md`
- `docs/project/architecture.md`
- `docs/project/learning.md`

Also required:
- Add a README link to `docs/project/index.md` so docs are reachable (no orphan docs).
- Keep `docs/project/rules.md` project-specific: do not copy governance rules; reference `AGENTS.md`.

## Minimalism rules (prevent docs bloat)
- Prefer short bullet lists; avoid long prose.
- Keep each doc focused on what must be true "all the time" (invariants, entrypoints, verification commands).
- Never copy constants/defaults/rules into docs; reference the SSOT owner by identifier/path.
- When a change impacts goal/verification/entrypoints/owners, update the affected doc in the same change.

## README linkage (required)
Ensure `README.md` contains (at minimum):
- A link to `docs/project/index.md` (project docs entrypoint).
- A link to `AGENTS.md` (governance SSOT).
- A short "Checks" section listing the deterministic commands used to verify the repo.
  - Minimum governance checks:
    - `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/check_agents_manifest.ps1`
    - `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/check_docs_ssot.ps1`
    - `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/check_project_docs.ps1`
    - `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/check_repo_hygiene.ps1`
    - `python scripts/check_python_safety.py`

## Template files (copy/paste, then customize)

### `docs/project/index.md`
```md
# Project Docs

- Goal + acceptance criteria: `docs/project/goal.md`
- Do/Don't rules: `docs/project/rules.md`
- Architecture (SSOT pointers): `docs/project/architecture.md`
- Learning notes: `docs/project/learning.md`
```

### `docs/project/goal.md`
```md
---
doc_type: reference
ssot_owner: <workflow entrypoint path or workflow registry path>
update_trigger: requirements/acceptance criteria change OR workflow behavior changes
---

# Goal

## Objective
- <what the project does, in 1-3 bullets>

## Acceptance criteria
- <objectively verifiable criteria>

## Non-goals
- <explicitly out of scope>

## Verification
- Preferred: <exact test/run command(s)>
- If no tests: <deterministic manual check steps>
```

### `docs/project/rules.md`
```md
---
doc_type: policy
ssot_owner: AGENTS.md
update_trigger: governance rules change OR new recurring pitfalls emerge
---

# Rules (Do / Don't)

## Governance (authoritative)
- Follow `AGENTS.md` (do not duplicate its rules here).

## Do
- Add only project-specific rules/invariants not already covered by `AGENTS.md`.

## Don't
- Don't copy constants/defaults/rules into docs; reference SSOT owners instead.
- Don't add orphan docs; keep docs linked from `docs/project/index.md` and README.
```

### `docs/project/architecture.md`
```md
---
doc_type: reference
ssot_owner: <workflow registry path or main orchestration module>
update_trigger: entrypoints/modules/workflows layout changes
---

# Architecture

## Entrypoints
- <CLI entrypoint path + command>
- <GUI entrypoint path (if any)>

## SSOT pointers (concept -> owner)
- Constants:
- Config:
- Rules/validation:
- Workflows/orchestration:
- Reporting/run outcomes:

## Data flow (high level)
- Inputs:
- Outputs/artifacts:
- Side effects:
```

### `docs/project/learning.md`
```md
---
doc_type: runbook
ssot_owner: AGENTS.md
update_trigger: new operational learnings/pitfalls discovered in real runs
---

# Learning Notes

Keep this focused on:
- failure modes observed in real runs
- environment/permission gotchas
- verification tips (how to reproduce/confirm outcomes)

Avoid:
- duplicating constants/defaults (reference the SSOT owner instead)
- re-implementing business rules in prose (reference the named rule functions/workflows)
```

## Final linkage checklist
- `docs/project/index.md` exists and links to the other docs.
- README links to `docs/project/index.md`.
- Each non-index doc under `docs/` has the required header (`doc_type`, `ssot_owner`, `update_trigger`).
