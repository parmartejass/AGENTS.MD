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
- Run repo checks:
  - `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/check_docs_ssot.ps1`
  - `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/check_agents_manifest.ps1`
  - `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/check_project_docs.ps1`
  - `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/check_repo_hygiene.ps1`
  - `python scripts/check_python_safety.py` (and ensure it passes).

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
