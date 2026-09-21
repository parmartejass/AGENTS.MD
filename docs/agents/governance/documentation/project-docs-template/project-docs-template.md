---
doc_type: policy
ssot_owner: docs/agents/governance/documentation/project-docs-template/project-docs-template.md
update_trigger: project-doc scaffold shape or subdoc scaffold fields change
---

# Project Docs Scaffold

Jurisdiction: initial shape of project-doc root docs, branch routers, and branch-local owner subdocs.

## Root-doc creation shape
- Each root doc MUST state jurisdiction, exclusions, current summary, subdoc trigger, and routes.
- Generated text MUST be adapted to verified owners; placeholders MUST NOT ship as truth.
- Root docs MUST NOT absorb every branch truth when a stable cluster needs a smaller owner.
- Verification sections MUST cite the README Checks command or deterministic manual steps.

## Branch-local subdoc rule
- Create one subdoc per stable truth cluster that would blur the root jurisdiction.
- Prohibited: one subdoc per prompt, task, commit, or fixed truth category.
- Each subdoc MUST own one responsibility and stay under its existing branch.
- Its branch router route MUST land in the same change; orphan subdocs are Prohibited.

| Branch | Stable cluster and exclusion |
|---|---|
| Goal | Durable intent cluster; no per-prompt/task/commit records. |
| Rules | Project-specific rule cluster; reusable governance stays with its governance owner. |
| Architecture | Stable behavior, boundary, workflow, integration, or module-authority cluster; no task logs or history. |
| Data truth | Data/config/constant/default/source-artifact cluster; no truth taxonomy, no copied source-owned values. |
| Learning | Recurring operational lesson; no chronology or work-status records. |

## Template - project_index.md
```md
# Project Docs

- [docs/project/goal/goal_index.md](goal/goal_index.md) - Project durable intent and acceptance criteria. Required when: confirming project scope or verification intent.
- [docs/project/rules/rules_index.md](rules/rules_index.md) - Project-specific rules that supplement `AGENTS.md`. Required when: checking project-local do/don't rules.
- [docs/project/architecture/architecture_index.md](architecture/architecture_index.md) - Architecture, SSOT pointers, and protected behavior records. Required when: locating owners, entrypoints, protected invariants, or authority relationships.
- [docs/project/data-truth/data-truth_index.md](data-truth/data-truth_index.md) - Data-truth ownership, provenance, validation, and routing. Required when: locating declared data/config/constant/default/sample/workbook/external-system truth owners.
- [docs/project/changelog/changelog_index.md](changelog/changelog_index.md) - Tracked closure records for completed non-trivial work. Required when: closing non-trivial work or reviewing what changed and where durable facts were promoted.
- [docs/project/learning/learning_index.md](learning/learning_index.md) - Durable operational learnings and recurring pitfalls. Required when: checking prior lessons or recurring friction.
```

## Template - goal.md
```md
---
doc_type: reference
ssot_owner: docs/project/goal/goal.md
update_trigger: requirements or acceptance criteria change OR workflow behavior changes
---

# Goal

## Boundary
- This branch owns durable project intent, objectives, acceptance criteria, non-goals, and verification intent.
- This branch does not own implementation details, transient working notes, change history, or data/config/source truth owned elsewhere.

## Objective
- <what the project does>

## Acceptance criteria
- <objectively verifiable criterion>

## Durable intent
- <accepted intent governing future work>

## Non-goals
- <explicitly out of scope>

## Current Summary
- <current-state summary>

## Branch-local owner subdocs
- None currently declared.

## Verification
- <README Checks reference or deterministic manual witness>
```

## Template - rules.md
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

## Do
- <project-specific rule not already bound by `AGENTS.md`>

## Don't
- <project-specific prohibition>

## Current Summary
- <current-state summary>

## Branch-local owner subdocs
- None currently declared.
```

## Template - architecture.md
```md
---
doc_type: reference
ssot_owner: docs/project/architecture/architecture.md
update_trigger: entrypoints, modules, or workflow layout changes
---

# Architecture

## Boundary
- This branch owns project boundaries, entrypoint and workflow ownership, responsibility splits, structural relationships, and authority graph routing.
- This branch does not own business/source data, transient task notes, or implementation-internal constants already owned by code/config/schema owners.

## Entrypoints
- <path + command>

## SSOT pointers (concept -> owner)
- <concept>: <owner>
- Constants, Config, Data truths, Rules/validation, Workflows (runtime coordination only), Reporting/run outcomes: <owner each>

## Data flow (high level)
- <inputs, outputs, side effects>

## Authority graph (required for non-trivial systems)
- <owner -> dependents>

## Current Summary
- <current-state summary>

## Branch-local owner subdocs
- None currently declared.
```

## Template - data-truth.md
```md
---
doc_type: reference
ssot_owner: docs/project/data-truth/data-truth.md
update_trigger: data-truth ownership, provenance, validation, or routing changes
---

# Data Truth

## Purpose
- Record declared data-truth owners and route consumers; docs own facts only when declared; no duplicate or non-owner copies of values, mappings, defaults, headers, thresholds, paths, or business/source data.

## Boundary
- This branch owns project-local data-truth routing and provenance notes when a project doc is the declared owner.
- This branch does not own facts already declared in code, config, schemas, source artifacts, samples, or external systems.

## Current Summary
- <declared data-truth owners, or none declared>

## Change Rule
- Add or update a branch-local owner subdoc only when a concrete project data/config/constant/default/source-artifact truth must affect future behavior and no more specific owner already holds it.
- Rule: do not add policy records here to satisfy a checker.

## Branch-local owner subdocs
- None currently declared.

## Verification
- README Checks owns the deterministic project-doc and docs-router verification commands.
```

## Template - changelog.md
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
- <each record routes durable facts to their owner or records N/A + reason>
- A closure record must not substitute for owner-doc promotion.

## Field Contract
- Fields follow the release jurisdiction's closure-record template.

## Entries
- None currently declared.
```

## Template - learning.md
```md
---
doc_type: runbook
ssot_owner: docs/project/learning/learning.md
update_trigger: new operational learnings or pitfalls appear in real runs
---

# Learning Notes

## Boundary
- This branch owns durable operational learnings, recurring pitfalls, and verification evidence governing future work.
- This branch does not own change history, work-status records, project rules, architecture contracts, or data truth.

## Current Summary
- <current-state summary>

## Branch-local owner subdocs
- None currently declared.

## Verification
- <deterministic command or manual witness>
```

## Template - branch router
```md
# <Branch> Branch Index

- [<leaf>.md](<leaf>.md) - <what it owns>. Required when: <retrieval trigger>.
```

## Template - branch-local owner subdoc
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
- <what this truth covers and excludes>

## Invariant
- <what future work must preserve>

## Change Rule
- <exact condition under which this truth may change>

## Verification
- <deterministic command or manual witness>

## References
- <related owner docs when jurisdiction crosses branches>
```

## Final linkage checklist
- `docs/project/project_index.md` exists and links every project branch.
- Each branch has a router plus its canonical narrative leaf.
- The repository README links `docs/project/project_index.md`.
- Every non-router doc carries `doc_type`, `ssot_owner`, `update_trigger`.
- Project truth routes through declared owner docs, not working-evidence scaffolds.
