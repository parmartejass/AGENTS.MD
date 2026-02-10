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
- Prefer a structured event contract for machine-debuggable runs:
  - `run_start`, `phase_transition`, terminal item event, `run_end`
  - explicit `reason_code` + `reason_detail` on failures/skips
  - source attribution (`module`, `function`, `file`, `line`)
- Keep one SSOT owner for event names/phases/reason codes (no duplicate enums in multiple modules).
- Redact sensitive keys by default (`token`, `password`, `secret`, `key`, `credential`) and store large payloads as summaries (size/hash/path reference) instead of raw dumps.

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

## Silent failures (rule)
- Rule: broad exception handlers must not hide failures.
  - Avoid: `except Exception: pass`
  - Avoid: `except Exception: return None/False/...` unless that sentinel is part of the function's explicit contract; otherwise record context/outcome (log/report) or raise a domain error
  - Definition: "explicit contract" means the sentinel meaning is documented (docstring/type) and callers handle it explicitly.
- If execution continues after an error (best-effort loops), still surface it:
  - record a terminal per-item outcome + reason
  - reflect partial failure at the run level (see `AGENTS.md` "Standard Log Schema")

## Witnesses (enforcement)
- **Static**: `scripts/check_python_safety.py` flags `BARE_EXCEPT` and `SILENT_EXCEPT`, and warns on `EXCEPT_RETURN_LITERAL`.
- **Runtime**: emit per-item outcome records and a run summary (see `AGENTS.md` "Standard Log Schema").
