---
doc_type: runbook
ssot_owner: docs/agents/governance/release/release.md
update_trigger: release gates, evidence concerns, or changelog fields change
---

# Release

Jurisdiction: release evidence routing, rollback readiness, and the changelog closure record.

## Release evidence

- Release evidence MUST identify each applicable owning jurisdiction and its witness.

## Rollback readiness

- MUST exercise the rollback path once against the release artifact; an asserted-only path is unverified.
- Rollback path examples: prior known-good commit, feature flag, deploy revert command.
- Behavior changes MUST verify rollback leaves no inconsistent data state.

## Changelog closure record

- Use after completed non-trivial work promotes durable facts to their owning authority.
- Owning authority means the owning docs, code, config, data, or workflow owner.
- Tracked project owner and valid mirror-surface authority: `SSOT-DEC-004`.
- Tracked project path when project docs are available: the project changelog owner.
- Field template and order:

```
- Change ID/date/status:
- Closure statement:
- Owner promotion references for durable facts or `N/A + reason`:
- Changed surfaces grouped by owner:
- Verification command/manual witness and result:
- Residual risks/follow-up:
- Commit/PR reference or `N/A + reason`:
```
