---
doc_type: playbook
ssot_owner: AGENTS.md
update_trigger: project docs minimum set or header policy changes
---

# Playbook - Project Docs (Minimal SSOT-Friendly Set)

Use when:
- The user asks to add or improve project docs, or
- A repo has no clear docs entrypoint/runbook and adding one would materially reduce ambiguity for future work.
- Any required project docs from `AGENTS.md` Documentation SSOT Policy are missing (apply this playbook even if the task was not docs-specific).

Goal: create a minimal docs set that captures intent/runbooks without duplicating code facts (constants, rules, defaults).

## Hard gates (required outputs)
- `docs/project/project_index.md` (router only; no header required)
- `docs/project/goal/goal_index.md` and `docs/project/goal/goal.md`
- `docs/project/rules/rules_index.md` and `docs/project/rules/rules.md`
- `docs/project/architecture/architecture_index.md` and `docs/project/architecture/architecture.md`
- `docs/project/learning/learning_index.md` and `docs/project/learning/learning.md`

Also required:
- Add a README link to `docs/project/project_index.md` so docs are reachable (no orphan docs).
- Keep `docs/project/rules/rules.md` project-specific: do not copy governance rules; reference `AGENTS.md`.
- Ensure every directory under `docs/` has the canonical router file resolved from `scripts/entrypoint_contracts.json`; project docs must participate in the repo-wide branched docs tree.
- Keep each leaf folder on the permanent router-plus-leaf pattern: `<authority>_index.md` routes, and router-linked descriptive sibling docs own the content.

## Minimalism rules (prevent docs bloat)
- Prefer short bullet lists; avoid long prose.
- Keep each doc focused on what must be true "all the time" (invariants, entrypoints, verification commands).
- Never copy constants/defaults/rules into docs; reference the SSOT owner by identifier/path.
- Use `docs/agents/20-sources-of-truth-map/sources-of-truth-map.md` when filling SSOT pointers to avoid parallel ownership.
- When a change impacts goal/verification/entrypoints/owners, update the affected doc in the same change.
- Keep parent routers routing-only: each `<authority>_index.md` should list direct children and include a `Required when:` trigger instead of restating the child doc in full.

## README linkage (required)
Ensure `README.md` contains (at minimum):
- A link to `docs/project/project_index.md` (project docs entrypoint).
- A link to `AGENTS.md` (governance SSOT).
- A short "Checks" section listing the deterministic commands used to verify the repo.
- Verification commands are SSOT in `README.md` section "Checks"; keep this playbook referential and do not duplicate the command list here.

## Template files (copy/paste, then customize)

### `docs/project/project_index.md`
```md
# Project Docs

- Governance SSOT: `AGENTS.md`
- Goal branch: `docs/project/goal/goal_index.md`
- Rules branch: `docs/project/rules/rules_index.md`
- Architecture branch: `docs/project/architecture/architecture_index.md`
- Learning branch: `docs/project/learning/learning_index.md`
- Change records (artifacts): `docs/project/change-records/`
```

### `docs/project/goal/goal_index.md`
```md
# Goal Branch Index

- [goal.md](goal.md) - Canonical project objective and acceptance criteria. Required when: confirming the repo's purpose, scope, or verification target.
```

### `docs/project/goal/goal.md`
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

### `docs/project/rules/rules_index.md`
```md
# Rules Branch Index

- [rules.md](rules.md) - Canonical project-specific do/don't rules. Required when: checking repo-local constraints that supplement but do not replace `AGENTS.md`.
```

### `docs/project/rules/rules.md`
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
- Don't add orphan docs; keep docs linked from `docs/project/project_index.md` and README.
```

### `docs/project/architecture/architecture_index.md`
```md
# Architecture Branch Index

- [architecture.md](architecture.md) - Canonical repo architecture and SSOT pointers. Required when: locating owners, entrypoints, checks, or authority relationships in this repo.
```

### `docs/project/architecture/architecture.md`
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

## Authority graph (required for non-trivial systems)
- <owner -> dependents>
```

### `docs/project/learning/learning_index.md`
```md
# Learning Branch Index

- [learning.md](learning.md) - Canonical operational learnings and pitfalls. Required when: checking recurring friction, verification tips, or prior governance lessons.
```

### `docs/project/learning/learning.md`
```md
---
doc_type: runbook
ssot_owner: AGENTS.md
update_trigger: new operational learnings/pitfalls discovered in real runs
---

# Learning Notes

Keep this focused on:
- failure modes observed in real runs
- environment/permission gotchas (the highest-signal content for any operational doc)
- verification tips (how to reproduce/confirm outcomes)
- common agent pitfalls (patterns that repeatedly cause rework or incorrect output)

Avoid:
- duplicating constants/defaults (reference the SSOT owner instead)
- re-implementing business rules in prose (reference the named rule functions/workflows)
```

## Final linkage checklist
- `docs/project/project_index.md` exists and links to the project branches.
- Each migrated project-doc branch has both a router `<authority>_index.md` and a canonical primary narrative leaf doc.
- README links to `docs/project/project_index.md`.
- Each non-router doc under `docs/` has the required header (`doc_type`, `ssot_owner`, `update_trigger`).
