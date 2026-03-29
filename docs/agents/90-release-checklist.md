---
doc_type: runbook
ssot_owner: AGENTS.md
update_trigger: release gates change
---

# 90 - Release Checklist

## SSOT / No duplicates
- Release gate: SSOT, no-duplication, and no-orphan checks.
- If Excel/GUI: lifecycle and threading implementation checks.
- If module boundaries changed: high cohesion + low coupling, no cycles.

## Logging / Errors
- No `print()`.
- Exceptions are meaningful and include context.
- No silent skips; skipped work records a reason.
- Run the applicable README.md "Checks" section (this repo vs target repo/submodule) and ensure all listed commands pass.
- For bugfix/regression releases, include bias-resistant debugging evidence package.
- For behavior changes/new features, include shift-left baseline evidence.

## Excel COM (if applicable)
- Quit attempted and verified.
- PID-validated kill fallback exists and is time-bounded.
- Cleanup occurs in `finally`.

## GUI (if applicable)
- Queue + `after(...)` drain pattern enforced.
- Shutdown/cancel event exists and is respected.

## Rollback readiness
- Confirm a rollback or revert path exists for the release (e.g., prior known-good commit, feature flag, or deploy revert command).
- For behavior changes, verify rollback does not leave data in an inconsistent state.

## Docs + comments
- Docs do not duplicate facts; they reference identifiers and owners.
- Comments are "why-only" and do not restate logic/defaults.
