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

- MUST exercise the rollback path once against the release artifact.
- A rollback path that is only asserted stays unverified.
- Rollback path examples: prior known-good commit, feature flag, deploy revert command.
- Behavior changes MUST verify rollback leaves no inconsistent data state.

## Changelog closure record

- Use after completed non-trivial work promotes durable facts to their owning authority.
- The Lexicon (ssot) defines owning authority.
- Tracked project owner and valid mirror-surface authority: `SSOT-DEC-004`.
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
