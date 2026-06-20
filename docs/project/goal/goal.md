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
- Repo checks pass (single command SSOT: `README.md` section "Checks").
- Project docs remain a docs-first truth surface for this governance repo's durable intent, owner pointers, tracked closure records, and verification records without duplicating reusable governance policy.

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
- This repo does not define domain business logic; templates are reference implementations only.
- Project docs must not restate reusable governance rules already owned by `AGENTS.md` or `docs/agents/`.

## Verification
- Run the commands listed in `README.md` section "Checks".
