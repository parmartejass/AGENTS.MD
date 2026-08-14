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
- `AGENTS.md` owns the exact three root authorities; `agents-manifest.yaml` deterministically routes only assigned-lead and subagent task authorities.
- The root/main reads and follows only `AGENTS.md` and its three declared root authorities, delegates once, and receives only a terminal result, `hold`, or authority-grounded superseding-plan summary, while the assigned lead owns all task-specific routing, council, execution, verification, and closure work inside its subtree.
- Repo checks pass (single command SSOT: `README.md` section "Checks").
- Governance-core consumers use one documented plain-data public API; check ordering and reconciliation have one engine owner, and private checker modules remain replaceable without consumer migration.
- Governance research consumers resolve `AGENTS.md` and the complete router-linked governance Markdown corpus through that public API; task-routing membership never substitutes for document topology.
- Project docs remain a docs-first truth surface for this governance repo's durable intent, owner pointers, tracked closure records, and verification records without duplicating reusable governance policy.
- Repo-owned runtime projections, tracked root runtime copies, and reference application templates are retired; reusable source assets remain under `docs/agents/`.

## Durable intent
- Implement docs-first truth through declared owners: reusable governance policy lives in `AGENTS.md` and `docs/agents/`, while repo-local project authority records live under `docs/project/`.
- Keep completed non-trivial work auditable through tracked closure records in `docs/project/changelog/changelog.md` after durable facts are promoted to their owning docs/code/config/data/workflow authorities.
- Keep durable project intent in this file. Working evidence becomes project truth only when selected durable facts are promoted into the owning project doc.

## Boundary
- This root doc owns stable project purpose, accepted scope, non-goals, and verification intent.
- It does not own reusable governance policy, project architecture, data-truth routing, closure records, operational learnings, or task/session ledgers.

## When to create a branch-local owner subdoc
- Create a goal subdoc when a durable user decision changes what the project is built to preserve and would bloat or blur this root objective.
- Keep task coordination, source prompt text, and closure evidence out of this branch unless selected durable facts are promoted into an owner doc.

## Current Summary
- The governance repo maintains a reusable governance pack.
- Project truth authority, tracked closure records, and non-owner evidence surfaces are governed by `SSOT-DEC-004` in `docs/agents/22-ssot-authority-decisions/ssot-authority-decisions.md`.

## Branch-local owner subdocs
- None currently declared.

## Non-goals
- This repo does not define domain business logic.
- Project docs must not restate reusable governance rules already owned by `AGENTS.md` or `docs/agents/`.

## Verification
- Run the commands listed in `README.md` section "Checks".
