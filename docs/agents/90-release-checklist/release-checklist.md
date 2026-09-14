---
doc_type: runbook
ssot_owner: AGENTS.md
update_trigger: release gates change
---

# 90 - Release Checklist

## Release evidence routes
Apply `AGENTS.md` FP-31 through FP-34 and Verification Floors. Release evidence MUST identify each applicable owner and its witness:
- SSOT, contracts, dependency direction, and pruning: `docs/agents/35-coding-principles/coding-principles.md`.
- Logging and explicit outcomes: `docs/agents/30-logging-errors/logging-errors.md`.
- COM ownership and cleanup: `docs/agents/50-excel-com-lifecycle/excel-com-lifecycle.md` when COM is in scope.
- UI thread and cancellation behavior: `docs/agents/60-gui-threading/gui-threading.md` when GUI work is in scope.
- Documentation placement and owner promotion: `docs/agents/25-docs-ssot-policy/docs-ssot-policy.md`.
- Repeatable verification commands: the applicable repository's README Checks.
- Bugfix/regression evidence: `AGENTS.md` Bias-Resistant Debugging and Verification Floors, with the applicable README Checks witness.
- Behavior-change/new-feature evidence: `AGENTS.md` Verification Floors and its shift-left quality baseline, with the applicable README Checks witness.
- Review and terminal decisions: `Orchestration.md`.

## Rollback readiness
- Confirm a rollback or revert path exists for the release (e.g., prior known-good commit, feature flag, or deploy revert command).
- For behavior changes, verify rollback does not leave data in an inconsistent state.

## Changelog (tracked closure record)
- Use after completed non-trivial work promotes durable facts to their owning docs/code/config/data/workflow authority.
- Tracked project owner and valid mirror-surface authority: `SSOT-DEC-004`.
- Tracked project path when project docs are available: `docs/project/changelog/changelog.md`.
- Field template/order:
  - Change ID/date/status:
  - Closure statement:
  - Owner promotion references for durable facts or `N/A + reason`:
  - Changed surfaces grouped by owner:
  - Verification command/manual witness and result:
  - Residual risks/follow-up:
  - Commit/PR reference or `N/A + reason`:
