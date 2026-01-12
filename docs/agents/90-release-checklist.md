---
doc_type: runbook
ssot_owner: AGENTS.md
update_trigger: release gates change
---

# 90 — Release Checklist

## SSOT / No duplicates
- No repeated literals representing the same concept.
- No repeated conditions: rules are named and centralized.
- No parallel lifecycle or GUI threading implementations.

## Logging / Errors
- No `print()`.
- Exceptions are meaningful and include context.
- No silent skips; skipped work records a reason.
- Run repo checks: `python scripts/check_python_safety.py` (and ensure it passes).

## Excel COM (if applicable)
- Quit attempted and verified.
- PID-validated kill fallback exists and is time-bounded.
- Cleanup occurs in `finally`.

## GUI (if applicable)
- Queue + `after(...)` drain pattern enforced.
- Shutdown/cancel event exists and is respected.

## Docs + comments
- Docs do not duplicate facts; they reference identifiers and owners.
- Comments are “why-only” and do not restate logic/defaults.
