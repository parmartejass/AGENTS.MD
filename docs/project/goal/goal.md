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
- Project docs remain a docs-first truth surface for this governance repo's durable intent, owner pointers, current-work status, and verification records without duplicating reusable governance policy.

## Durable intent
- Implement docs-first truth through declared owners: reusable governance policy lives in `AGENTS.md` and `docs/agents/`, while repo-local project authority records live under `docs/project/`.
- Keep durable project intent in this file; `docs/project/goal/current-work.md` is mandatory and owns the active-work authority record, including prompt, prompt safety, derived work-item goal, source-derived plan, implementation records, reconciliation, review, truth-layer witnesses, closure handoff, and next safe action.

## Non-goals
- This repo does not define domain business logic; templates are reference implementations only.
- Project docs must not restate reusable governance rules already owned by `AGENTS.md` or `docs/agents/`.

## Verification
- Run the commands listed in `README.md` section "Checks".
