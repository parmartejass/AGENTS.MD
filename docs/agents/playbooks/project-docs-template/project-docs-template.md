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

## Scaffold ownership

`AGENTS.md` Documentation SSOT Policy owns the constitutional trigger; `docs/agents/25-docs-ssot-policy/docs-ssot-policy.md` declares the required baseline set and README linkage. `docs/agents/25-docs-ssot-policy/docs-ssot-policy.md` owns placement, promotion, headers, routers, and validation boundaries. This playbook owns the initial root-doc and branch-local scaffold shape below; generated text MUST be adapted to verified project owners under `AGENTS.md` Instruction Derivation Gate.

## Root-doc creation shape

Each root doc states its jurisdiction, exclusions, current summary, branch-local subdoc trigger, and routes. The templates below declare the branch-specific ownership. A branch-local subdoc owns one stable truth cluster when adding it to the root would blur that jurisdiction; it is not a per-prompt, per-task, or per-commit record. Shared creation mechanics and the initial scaffold are owned by [owner-subdocs/owner-subdocs.md](owner-subdocs/owner-subdocs.md); apply that owner to every branch below when its trigger occurs.

Before creating or updating a record, resolve its material future-decision relevance, single owner, evidence and uncertainty, and supersession trigger through the docs SSOT policy. Use `docs/agents/20-sources-of-truth-map/sources-of-truth-map.md` for concept ownership. A new narrative owner requires its branch router route in the same change.

## Template use

The following blocks are scaffolds, not copies of project truth. Replace placeholders with verified owner facts; preserve provenance and verification status. README Checks remains the command owner: generated verification sections cite that command location or record deterministic manual steps. `AGENTS.md` FP-34 governs minimal content, and `Orchestration.md` governs all agent lifecycle and authorization decisions.

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
ssot_owner: docs/project/goal/goal.md
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
- <accepted project intent governing future work, or "No additional durable intent declared beyond the objective and acceptance criteria.">

## Non-goals
- <explicitly out of scope>

## Current Summary
- <short current-state summary of project intent and verification target>

## Branch-local owner subdocs
- None currently declared.

## Verification
- README Checks reference: <applicable command identifier/location>
- Manual witness when required: <deterministic steps and scope-based reason>
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
ssot_owner: docs/project/rules/rules.md
update_trigger: project-specific constraints change
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

## Governing routes
- Reusable governance: `AGENTS.md`.
- Documentation placement and routing: `docs/agents/25-docs-ssot-policy/docs-ssot-policy.md`.

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
ssot_owner: docs/project/architecture/architecture.md
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

## Current Summary
- <short current-state summary of the project architecture and primary authority boundaries>

## Branch-local owner subdocs
- None currently declared.
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
ssot_owner: docs/project/learning/learning.md
update_trigger: new operational learnings/pitfalls discovered in real runs
---

# Learning Notes

## Boundary
- This branch owns durable operational learnings, recurring pitfalls, and verification evidence governing future work.
- This branch does not own change history, work-status records, project rules, architecture contracts, or data truth.

## Current Summary
- No project-specific recurring learning is currently declared beyond `AGENTS.md`.

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
