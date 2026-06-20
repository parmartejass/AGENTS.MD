---
doc_type: playbook
ssot_owner: docs/agents/playbooks/project-docs-template/project-docs-template.md
update_trigger: project docs minimum set or header policy changes
---

# Playbook - Project Docs (Minimal SSOT-Friendly Set)

Use when:
- The user asks to add or improve project docs, or
- A repo has no clear docs entrypoint/runbook and adding one would materially reduce ambiguity for future work.
- Any required project docs from `AGENTS.md` Documentation SSOT Policy are missing (apply this playbook even if the task was not docs-specific).

Goal: create the required project-doc scaffold contract that captures declared project authority without duplicating non-owner facts.

## Required Scaffold Outputs
These outputs are the project-doc creation contract owned by this playbook. The contract includes which baseline project docs are created, what each root doc must own, what each root doc must not own, and the required starting structure for branch-local owner subdocs.

`AGENTS.md` owns the governing documentation hard gate. `docs/agents/25-docs-ssot-policy/docs-ssot-policy.md` owns the cross-doc policy mechanics: placement boundaries, routers, headers, optional-leaf routing, orphan-doc prevention, and validation boundaries.

- `docs/project/project_index.md` (router only; no header required)
- `docs/project/goal/goal_index.md` and `docs/project/goal/goal.md`
- `docs/project/rules/rules_index.md` and `docs/project/rules/rules.md`
- `docs/project/architecture/architecture_index.md` and `docs/project/architecture/architecture.md`
- `docs/project/data-truth/data-truth_index.md` and `docs/project/data-truth/data-truth.md`
- `docs/project/changelog/changelog_index.md` and `docs/project/changelog/changelog.md`
- `docs/project/learning/learning_index.md` and `docs/project/learning/learning.md`

Required references:
- README links to `docs/project/project_index.md`.
- Project rules cite `AGENTS.md` instead of restating governance rules.
- Routers and leaf docs follow the docs SSOT policy and `scripts/entrypoint_contracts.json`.

## Project-Doc Creation Contract (docs-first)
Use the placement and promotion policy in `docs/agents/25-docs-ssot-policy/docs-ssot-policy.md`. This playbook owns the required creation contract for the baseline project-doc branches and their primary root docs.

Required root-doc ownership:
- `docs/project/goal/goal.md`: durable project intent, objective, acceptance criteria, non-goals, and verification intent.
- `docs/project/architecture/architecture.md`: project boundaries, owner graph, responsibility splits, input-to-output flow, coupling boundaries, and structural relationships.
- `docs/project/rules/rules.md`: deterministic project-specific do/don't constraints and why they exist.
- `docs/project/data-truth/data-truth.md`: data-truth jurisdiction and routing to concrete owners such as schemas, config/defaults, source artifacts, samples, and external systems.
- `docs/project/changelog/changelog.md`: tracked closure records for completed non-trivial work after durable facts are promoted to their owners.
- `docs/project/learning/learning.md`: reusable operational learnings and recurring pitfalls; not change history.

Required root-doc shape:
- State what the branch owns.
- State what the branch does not own.
- State when to create a branch-local owner subdoc.
- Provide a short current summary.
- Route to branch-local owner subdocs.

Router contract:
- `docs/project/goal/goal_index.md` must route `goal.md`.
- Include branch-local owner subdoc routes only when creating or keeping that subdoc.
- Router files remain title plus route bullets only; do not add subsection headings to router files.

Branch-local owner subdocs:
- Live under the existing jurisdiction branch that owns the truth.
- Are created when adding the truth to the root doc would bloat or blur root jurisdiction.
- Own one stable truth cluster; they are not one prompt, one task, one commit, or a fixed category.
- Use natural sections when relevant: `Intent`, `Boundary`, `Invariant`, `Change rule`, `Verification`, and `References`.
- Do not add a broad escape-hatch section; if a truth can change, state the deterministic change rule.

Promotion test:
- What future behavior does this record change?
- Which single project-doc owner owns it?
- Which declared code/config/data/workflow/doc owner holds the fact?
- What verification witness and re-verification or supersession trigger keeps it current?

## Minimalism rules (prevent docs bloat)
- Prefer short bullet lists; avoid long prose.
- Keep each doc focused on what must be true "all the time" (invariants, entrypoints, verification commands).
- Do not copy constants/defaults/rules/data into non-owner docs; reference the SSOT owner by identifier/path.
- If a doc or doc-owned artifact is the declared owner for config, constants, defaults, source data, mappings, headers, thresholds, paths, schemas, samples, or external fields, declare that ownership in `docs/project/data-truth/data-truth.md` with a validation witness and update trigger.
- Use `docs/agents/20-sources-of-truth-map/sources-of-truth-map.md` when filling SSOT pointers to avoid parallel ownership.
- When a change impacts goal/verification/entrypoints/owners, update the affected doc in the same change.
- Keep parent routers routing-only: each `<authority>_index.md` should list direct children and include a `Required when:` trigger instead of restating the child doc in full.

## README linkage (required)
Ensure `README.md` contains (at minimum):
- A link to `docs/project/project_index.md` (project docs entrypoint).
- A link to `AGENTS.md` (governance SSOT).
- A short "Checks" section listing the deterministic commands used to verify the repo.
- Verification commands are SSOT in `README.md` section "Checks"; keep this playbook referential and do not duplicate the command list here.

## Required Template Files (copy/paste, then customize)

### `docs/project/project_index.md`
```md
# Project Docs

- [docs/project/goal/goal_index.md](goal/goal_index.md) - Project durable intent and acceptance criteria. Required when: confirming project scope or verification intent.
- [docs/project/rules/rules_index.md](rules/rules_index.md) - Project-specific rules that supplement `AGENTS.md`. Required when: checking project-local do/don't rules.
- [docs/project/architecture/architecture_index.md](architecture/architecture_index.md) - Architecture, SSOT pointers, and protected behavior records. Required when: locating owners, entrypoints, protected invariants, or authority relationships.
- [docs/project/data-truth/data-truth_index.md](data-truth/data-truth_index.md) - Data-truth ownership, provenance, validation, and routing. Required when: locating declared data/config/constant/default/sample/workbook/external-system truth owners.
- [docs/project/changelog/changelog_index.md](changelog/changelog_index.md) - Tracked closure records for completed non-trivial work. Required when: closing non-trivial work or reviewing what changed and where durable facts were promoted.
- [docs/project/learning/learning_index.md](learning/learning_index.md) - Durable operational learnings and recurring pitfalls. Required when: checking prior lessons or recurring friction.
```

### `docs/project/goal/goal_index.md`
```md
# Goal Branch Index

- [goal.md](goal.md) - Durable project intent, objective, acceptance criteria, non-goals, and verification intent. Required when: confirming the repo's purpose, scope, or verification target.
```

### `docs/project/goal/goal.md`
```md
---
doc_type: reference
ssot_owner: <workflow coordinator entrypoint path or workflow registry path>
update_trigger: requirements/acceptance criteria change OR workflow behavior changes
---

# Goal

## Boundary
- This branch owns durable project intent, objectives, acceptance criteria, non-goals, and verification intent.
- This branch does not own implementation details, transient working notes, change history, or data/config/source truth owned elsewhere.

## Objective
- <what the project does, in 1-3 bullets>

## Acceptance criteria
- <objectively verifiable criteria>

## Durable intent
- <accepted project intent that should guide future work, or "No additional durable intent declared beyond the objective and acceptance criteria.">

## Non-goals
- <explicitly out of scope>

## When to create a branch-local owner subdoc
- Create a goal subdoc when a stable intent cluster needs its own intent, boundary, invariant, change rule, verification, and references.
- Do not create one subdoc per prompt, task, commit, or fixed truth category.

## Current Summary
- <short current-state summary of project intent and verification target>

## Branch-local owner subdocs
- None currently declared.

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

## Boundary
- This branch owns deterministic project-specific rules that supplement `AGENTS.md`.
- This branch does not own reusable governance rules, implementation constants, runtime predicates, or data truths owned elsewhere.

## Governance (authoritative)
- Follow `AGENTS.md` (do not duplicate its rules here).

## Current Summary
- No project-specific rules are currently declared beyond `AGENTS.md`.

## Do
- Add only project-specific rules/invariants not already covered by `AGENTS.md`.

## Don't
- Don't copy constants/defaults/rules/data into non-owner docs; reference SSOT owners instead.
- Don't add orphan docs; keep docs linked from `docs/project/project_index.md` and README.

## When to create a branch-local owner subdoc
- Create a rules subdoc when a stable project-specific rule cluster needs its own intent, boundary, invariant, change rule, verification, and references.
- Do not use this branch for generic governance policy already owned by `AGENTS.md` or `docs/agents/`.

## Branch-local owner subdocs
- None currently declared.
```

### `docs/project/architecture/architecture_index.md`
```md
# Architecture Branch Index

- [architecture.md](architecture.md) - Canonical repo architecture and SSOT pointers. Required when: locating owners, entrypoints, checks, or authority relationships in this repo.
```

When creating a branch-local owner subdoc such as `docs/project/architecture/protected-behavior.md`, add a direct router bullet:
```md
- [protected-behavior.md](protected-behavior.md) - Protected behavior records and replacement rules. Required when: the file exists because a behavior may be weakened, replaced, or superseded.
```

### `docs/project/architecture/architecture.md`
```md
---
doc_type: reference
ssot_owner: <workflow registry path or main runtime-coordination module>
update_trigger: entrypoints/modules/workflows layout changes
---

# Architecture

## Boundary
- This branch owns project boundaries, entrypoint and workflow ownership, responsibility splits, structural relationships, and authority graph routing.
- This branch does not own business/source data, transient task notes, or implementation-internal constants already owned by code/config/schema owners.

## Entrypoints
- <CLI entrypoint path + command>
- <GUI entrypoint path (if any)>

## SSOT pointers (concept -> owner)
- Constants:
- Config:
- Data truths:
- Rules/validation:
- Workflows/orchestration (runtime coordination only):
- Reporting/run outcomes:

## Data flow (high level)
- Inputs:
- Outputs/artifacts:
- Side effects:

## Authority graph (required for non-trivial systems)
- <owner -> dependents>

## When to create a branch-local owner subdoc
- Create an architecture subdoc when a stable behavior, boundary, workflow, integration, or module-authority cluster needs its own intent, boundary, invariant, change rule, verification, and references.
- Do not use branch-local subdocs as task logs or change history.

## Current Summary
- <short current-state summary of the project architecture and primary authority boundaries>

## Branch-local owner subdocs
- None currently declared.
```

### Branch-local owner subdoc example
```md
---
doc_type: reference
ssot_owner: docs/project/<branch>/<owner-subdoc>.md
update_trigger: intent, boundary, invariant, change rule, verification, or references change
---

# <Stable Truth Cluster Name>

## Intent
- <what the user wanted and why this truth exists>

## Boundary
- <what this truth covers>
- <what this truth does not cover, when needed>

## Invariant
- <what future work must preserve>

## Change Rule
- <exact condition under which this truth may change>

## Verification
- <deterministic command or manual witness>

## References
- <related owner docs, when jurisdiction crosses branches>
```

### `docs/project/data-truth/data-truth_index.md`
```md
# Data-Truth Branch Index

- [data-truth.md](data-truth.md) - Project data-truth ownership, provenance, validation, and routing records. Required when: locating declared data/config/constant/default/sample/workbook/external-system truth owners.
```

### `docs/project/data-truth/data-truth.md`
```md
---
doc_type: reference
ssot_owner: docs/project/data-truth/data-truth.md
update_trigger: data-truth ownership, provenance, validation, or routing changes
---

# Data Truth

## Purpose
- Record declared project data-truth owners and route consumers to them.
- Allow docs or doc-owned artifacts to own facts only when explicitly declared here or in the referenced owner.
- Prevent duplicate/non-owner copies of values, mappings, defaults, headers, thresholds, paths, or business/source data.

## Boundary
- This branch owns project-local data-truth routing and provenance notes when a project doc is the declared owner.
- This branch does not own facts already declared in code, config, schemas, source artifacts, samples, or external systems.

## Current Summary
- No project-owned data truths are currently declared here.

## When to create a branch-local owner subdoc
- Create a data-truth subdoc when a stable data/config/constant/default/source-artifact cluster needs its own intent, boundary, invariant, change rule, verification, and references.
- Do not create fixed truth-kind taxonomies or duplicate code/config/schema/source-owned values here.

## Change Rule
- Add or update a branch-local owner subdoc only when a concrete project data/config/constant/default/source-artifact truth must affect future behavior and no more specific owner already holds it.
- Rule: do not add policy records here to satisfy a checker.

## Branch-local owner subdocs
- None currently declared.

## Verification
- README "Checks" owns the deterministic project-doc and docs-router verification commands.
```

### `docs/project/changelog/changelog_index.md`
```md
# Changelog Branch Index

- [changelog.md](changelog.md) - Tracked closure records for completed non-trivial work. Required when: closing non-trivial work or reviewing what changed and where durable facts were promoted.
```

### `docs/project/changelog/changelog.md`
```md
---
doc_type: reference
ssot_owner: docs/project/changelog/changelog.md
update_trigger: non-trivial work closes OR closure-record field contract changes
---

# Changelog

## Boundary
- This branch owns tracked closure-record facts for completed non-trivial work.
- This branch does not own behavior, invariants, project goals, rules, data truth, architecture, implementation rationale, active work, raw prompts, transcripts, or unpromoted working evidence.

## Invariant
- Each closure record references the owning docs/code/config/data/workflow authority for durable facts, or records `N/A + reason`.
- A closure record must not substitute for owner-doc promotion.
- Raw secrets, credentials, PII, customer data, and oversized pasted artifacts must not be stored here.

## Field Contract
- Closure-record field template/order is owned by `docs/agents/90-release-checklist/release-checklist.md`.
- Entries must follow that owner instead of redefining the field template here.

## Entries
- None currently declared.
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

## Boundary
- This branch owns durable operational learnings, recurring pitfalls, and verification gotchas that should affect future work.
- This branch does not own change history, work-status records, project rules, architecture contracts, or data truth.

## Current Summary
- No project-specific recurring learning is currently declared beyond `AGENTS.md`.

## When to create a branch-local owner subdoc
- Create a learning subdoc when a recurring operational lesson needs its own intent, boundary, invariant, change rule, verification, and references.
- Do not use this branch as a chronological history or work-status record.

## Branch-local owner subdocs
- None currently declared.

## Verification
- <deterministic command or manual witness that confirms the learning still applies>
```

## Final linkage checklist
- `docs/project/project_index.md` exists and links to the project branches.
- Each migrated project-doc branch has both a router `<authority>_index.md` and a canonical primary narrative leaf doc.
- README links to `docs/project/project_index.md`.
- Each non-router doc under `docs/` has the required header (`doc_type`, `ssot_owner`, `update_trigger`).
- Project truth surfaces are routed through declared owner docs rather than working-evidence scaffolds.
