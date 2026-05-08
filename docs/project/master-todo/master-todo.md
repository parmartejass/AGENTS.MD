---
doc_type: runbook
ssot_owner: AGENTS.md
update_trigger: remediation scope, sequencing, or verification evidence changes
---

# Master To-Do

## Scope
- Track staged governance remediation at a summary level.
- Governance rules remain owned by `AGENTS.md`.
- Context-injection routing remains owned by `agents-manifest.yaml`.
- Runtime projection authority remains active for Cursor, Claude, Codex, settings, MCP, and skill projections.
- ACP placeholders, automation runbooks, integration notes, generated analyses, and PR-control-plane templates were retired on 2026-05-08; detailed historical evidence lives in change records.

## Acceptance criteria
- One owner for each active governance concept.
- One effective checker rule set for council summaries, manifest checks, project-doc checks, stale retired references, and repo hygiene.
- README "Checks" remains the single verification-command SSOT.
- Context injection and discovery guidance are internally consistent.
- Project and template docs reference owners instead of restating literals or check lists.

## Completed remediation
- 2026-03-29: staged SSOT drift remediation across runtime ownership, checker parity, supporting docs, and strict-safety closure.
- 2026-05-08: governance cleanup retired stale ACP, automation, generated research, integration, PR-control-plane, and repo-owned subagent projection surfaces while preserving runtime projection authority for Cursor, Claude, Codex, skills, settings, and MCP.

## Open follow-ups
- Keep change records current when governance surfaces are retired.
- Keep stale-reference checks strict for active docs and explicit for historical records.

## Council checkpoints
- Use the `AGENTS.md` "Subagent Council (Hard Gate)" section as the governing procedure for each stage.
- Record pre-change and post-change council summaries in the relevant change record before final closure.
