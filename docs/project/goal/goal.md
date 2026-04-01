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

## Non-goals
- This repo does not define domain business logic; templates are reference implementations only.

## Verification
- Run the commands listed in `README.md` section "Checks".
