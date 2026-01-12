---
doc_type: policy
ssot_owner: AGENTS.md
update_trigger: logging/error requirements change
---

# 30 — Logging & Errors

## Logging (required)
- No `print()`.
- Use module-level logging where applicable.
- Log workflow boundaries and failure points with context (paths, sheet, row identifiers).

## Error taxonomy (recommended)
Maintain one owner for domain errors so failures are searchable and consistent, e.g.:
- `ConfigError`
- `ValidationError`
- `ExcelComError`
- `FileIOError`
- `WorkflowError`

## Catching policy
- Avoid bare `except` and avoid catch-all patterns that hide cause.
- Catch specific exception categories (file, JSON, subprocess, library-specific COM/xlwings).

