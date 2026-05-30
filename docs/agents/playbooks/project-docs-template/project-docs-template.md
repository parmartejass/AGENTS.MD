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

Goal: create a minimal docs set that captures declared project authority without duplicating non-owner facts.

## Required Scaffold Outputs
These outputs are the project-doc scaffold owned by this playbook. `AGENTS.md` owns the governing documentation hard gate, and `docs/agents/25-docs-ssot-policy/docs-ssot-policy.md` owns the placement and router policy.

- `docs/project/project_index.md` (router only; no header required)
- `docs/project/goal/goal_index.md` and `docs/project/goal/goal.md`
- `docs/project/rules/rules_index.md` and `docs/project/rules/rules.md`
- `docs/project/architecture/architecture_index.md` and `docs/project/architecture/architecture.md`
- `docs/project/data-truth/data-truth_index.md` and `docs/project/data-truth/data-truth.md`
- `docs/project/learning/learning_index.md` and `docs/project/learning/learning.md`

Required references:
- README links to `docs/project/project_index.md`.
- Project rules cite `AGENTS.md` instead of restating governance rules.
- Routers and leaf docs follow the docs SSOT policy and `scripts/entrypoint_contracts.json`.

## Bounded authority memory structure (docs-first)
Use the placement and promotion policy in `docs/agents/25-docs-ssot-policy/docs-ssot-policy.md`. This playbook owns scaffold shape and copy/paste templates only.

Scaffold placement:
- `docs/project/goal/current-work.md`: active intent, current status, next checkpoint, supersession pointer.
- `docs/project/architecture/protected-behavior.md`: protected behavior invariant, current mechanism owner, accepted tradeoff, replacement/change rule, deterministic witness.
- `docs/project/data-truth/data-truth.md`: data-truth owner, source format/provenance, validation witness, consumers, and change rule.
- `docs/project/learning/changelog.md`: concise promoted change/supersession history; evidence pointers only, not all reasoning.
- `docs/project/change-records/*.json`: structured verification artifacts when artifact-based verification is enabled.

Triggered-leaf router rule:
- Include a triggered leaf route only when creating or keeping that leaf.
- Router files remain title plus route bullets only; do not add subsection headings to router files.

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

## Template files (copy/paste, then customize)

### `docs/project/project_index.md`
```md
# Project Docs

- [docs/project/goal/goal_index.md](goal/goal_index.md) - Project objective, acceptance criteria, and current work status. Required when: confirming project scope or resuming active work.
- [docs/project/rules/rules_index.md](rules/rules_index.md) - Project-specific rules that supplement `AGENTS.md`. Required when: checking project-local do/don't rules.
- [docs/project/architecture/architecture_index.md](architecture/architecture_index.md) - Architecture, SSOT pointers, and protected behavior records. Required when: locating owners, entrypoints, protected invariants, or authority relationships.
- [docs/project/data-truth/data-truth_index.md](data-truth/data-truth_index.md) - Data-truth ownership, provenance, validation, and routing. Required when: locating declared data/config/constant/default/sample/workbook/external-system truth owners.
- [docs/project/learning/learning_index.md](learning/learning_index.md) - Durable operational learnings and authority changelog routing. Required when: checking prior lessons or durable authority changes.
```

### `docs/project/goal/goal_index.md`
```md
# Goal Branch Index

- [goal.md](goal.md) - Canonical project objective and acceptance criteria. Required when: confirming the repo's purpose, scope, or verification target.
```

When creating `docs/project/goal/current-work.md`, add this router bullet:
```md
- [current-work.md](current-work.md) - Active intent and current status. Required when: the file exists because in-flight work or prior status constrains the next change.
```

### `docs/project/goal/goal.md`
```md
---
doc_type: reference
ssot_owner: <workflow coordinator entrypoint path or workflow registry path>
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

### `docs/project/goal/current-work.md` (optional)
```md
---
doc_type: runbook
ssot_owner: docs/project/goal/current-work.md
update_trigger: active user intent, status, checkpoint, or supersession changes
---

# Current Work

Status: active|paused|blocked|ready-to-clear
Work item ID: CW-YYYYMMDD-NNN
Last updated: YYYY-MM-DD
Owner/context: <agent/user/process, if relevant>

## Active intent
- <one durable current goal, or "None">

## Status
- Last verified:
- Evidence/version:
- Re-verification trigger:
- Current state:
- Next checkpoint:

## Boundaries
- <protected scope boundaries that affect the next change>

## Supersession
- Superseded by:
- Clear when:

## Next safe action
- <next action a future agent can safely take>

## Clear Rule
- When this work is complete, fold durable outcomes into owner docs, add changelog entries if authority changed, then remove or reset this file. Do not preserve completed task logs here.
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
- Don't copy constants/defaults/rules/data into non-owner docs; reference SSOT owners instead.
- Don't add orphan docs; keep docs linked from `docs/project/project_index.md` and README.
```

### `docs/project/architecture/architecture_index.md`
```md
# Architecture Branch Index

- [architecture.md](architecture.md) - Canonical repo architecture and SSOT pointers. Required when: locating owners, entrypoints, checks, or authority relationships in this repo.
```

When creating `docs/project/architecture/protected-behavior.md`, add this router bullet:
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
```

### `docs/project/architecture/protected-behavior.md` (triggered)
```md
---
doc_type: reference
ssot_owner: docs/project/architecture/protected-behavior.md
update_trigger: protected behavior, current mechanism, tradeoff, or witness changes
---

# Protected Behavior

## Records

### PB-YYYYMMDD-NNN - <behavior name>
- Status: active|proposed|deprecated|superseded
- Behavior:
- Scope:
- Protected because:
- Current mechanism:
- Required equivalence:
- Verification:
- Evidence/version:
- Re-verification trigger:
- Allowed changes:
- Weakening rule:
- Related data truths:
- Related rules:
- Supersedes:
- Superseded by:
- Last verified:
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

## Record Schema
Each durable data-truth record uses this shape:
- ID: `DT-YYYYMMDD-NNN`
- Status: `active | proposed | deprecated | superseded`
- Truth type: `input-artifact | source-artifact | workbook | schema | config | constant | default | external-system | mapping | threshold | path | sample-data | document-owned`
- Owner SSOT:
- Doc role: `owner | router | provenance | interpretation | validation`
- Scope:
- Statement:
- Provenance:
- Consumers:
- Validation:
- Change rule:
- Related protected behavior:
- Related rules:
- Supersedes:
- Superseded by:
- Last verified:
- Evidence/version:
- Re-verification trigger:

## Records
- No project-owned data truths are currently declared here.

This is an explicit reviewed-empty registry state for project-owned data-truth records.
- Reviewed-empty date:
- Evidence:
- Scope: this statement does not claim that no data/config/constants/defaults exist in the repo; it only states that no project-owned data-truth record has been promoted here yet.
- Next update trigger: add `DT-*` records when a concrete project data/config/constant/default/source-artifact authority must affect future behavior.
- Rule: do not add policy records here to satisfy a checker.
```

### `docs/project/learning/learning_index.md`
```md
# Learning Branch Index

- [learning.md](learning.md) - Canonical operational learnings and pitfalls. Required when: checking recurring friction, verification tips, or prior governance lessons.
```

When creating `docs/project/learning/changelog.md`, add this router bullet:
```md
- [changelog.md](changelog.md) - Concise promoted change and supersession notes. Required when: the file exists because a durable project authority record changed.
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
- duplicating constants/defaults/data from a different owner (reference the SSOT owner instead)
- re-implementing business rules in prose (reference the named rule functions; workflows only coordinate runtime execution)
```

### `docs/project/learning/changelog.md` (triggered)
```md
---
doc_type: reference
ssot_owner: docs/project/learning/changelog.md
update_trigger: durable project authority records are added, superseded, or retired
---

# Changelog

## Entries

### CH-YYYYMMDD-NNN - <short title>
- Date: YYYY-MM-DD
- Status: proposed|accepted|corrected|deprecated|superseded|rolled-back
- Change type: goal|rule|architecture|data-truth|protected-behavior|source-owner|current-work|governance-policy|other
- Changed owners/files:
- Context:
- Decision/change:
- Consequences/tradeoffs:
- Validation:
- Evidence/version:
- Supersedes:
- Superseded by:
- Follow-up required:
```

## Final linkage checklist
- `docs/project/project_index.md` exists and links to the project branches.
- Each migrated project-doc branch has both a router `<authority>_index.md` and a canonical primary narrative leaf doc.
- README links to `docs/project/project_index.md`.
- Each non-router doc under `docs/` has the required header (`doc_type`, `ssot_owner`, `update_trigger`).
