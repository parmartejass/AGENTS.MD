---
doc_type: policy
ssot_owner: AGENTS.md
update_trigger: logging/error requirements change
---

# 30 — Logging & Errors

## Logging (required)
- This delegated owner applies `AGENTS.md` Logging + Explicit Failure and owns channel, failure, reconciliation, and diagnostic mechanics; schema details remain at `docs/agents/playbooks/log-schema-template/log-schema-template.md`.
- Log workflow boundaries and failure points with context (paths, sheet, row identifiers).
- If a report/log sink is unavailable or degraded, user feedback must say that the diagnostic artifact is unavailable/degraded and preserve the workflow outcome separately.
- Machine-debuggable runs MUST use the event contract owned by `docs/agents/playbooks/log-schema-template/log-schema-template.md`; event names, phases, and reason codes route to that contract and the declared application enum owner.
- Redact sensitive keys by default (`token`, `password`, `secret`, `key`, `credential`) and store large payloads as summaries (size/hash/path reference) instead of raw dumps.

## Explicit outcomes and work reconciliation
- No `print()`.
- Use module-level logging (`logger = logging.getLogger(__name__)`) where applicable.
- Catch specific exceptions; log context; raise meaningful domain errors.
- Never "silently skip": if something is skipped, record **SKIPPED + reason** (log and/or run report).
- Never "silently pass": success or partial success must reconcile the known work universe (`planned`, `eligible`, `executed`, `skipped`, `failed`) or fail validation if the workflow cannot know what it was supposed to process.
- User-facing surfaces (CLI, GUI, reports, status panes) must show concise input/scope confirmation, progress or current processing phase for long work, terminal outcome, output/artifact path when produced, skip/failure reason, required user action, and run/report/log pointer when applicable.
- Keep user feedback concise and actionable; keep deep diagnostics in structured logs with redaction and summarized large payloads.

## Feedback channels
- User feedback: concise, actionable status only; no stack traces, raw payload dumps, or per-item floods in normal UI/CLI output.
- INFO logs: run boundaries, phase summaries, counts, artifact paths, and terminal outcomes.
- Structured event logs: machine-readable event payloads, timings, reason codes, counts, write effects, and resource witnesses.
- DEBUG logs: deeper diagnostics, still redacted and summarized for large payloads.

## Error taxonomy
Domain error ownership follows `AGENTS.md` FP-12. These names are non-normative examples; the application's declared error owner defines its taxonomy:
- `ConfigError`
- `ValidationError`
- `ExcelComError`
- `FileIOError`
- `WorkflowError`

## Catching policy
- Bare `except` and catch-all patterns that hide cause are prohibited.
- Catch specific exception categories (file, JSON, subprocess, library-specific COM/xlwings).

## Silent failures (rule)
- Rule: broad exception handlers must not hide failures.
  - Avoid: `except Exception: pass`
  - Avoid: `except Exception: return None/False/...` unless that sentinel is part of the function's explicit contract; otherwise record context/outcome (log/report) or raise a domain error
  - Definition: "explicit contract" means the sentinel meaning is documented (docstring/type) and callers handle it explicitly.
- If a workflow cannot resolve the required config/rule/intent authority for a branch, it must stop that branch with `FAILED` or `SKIPPED + reason`; it must not infer, duplicate, or silently default the business rule in orchestration code.
- No silent pass: when the workflow knows the work universe, the run summary must reconcile `planned = executed + skipped + failed`; zero eligible work must be `SKIPPED + reason` or `FAILED` unless the workflow contract declares a valid no-op.
- A valid no-op must still be visible as a terminal outcome with reason (for example `SKIPPED + VALID_NOOP`); do not report all-zero work as `SUCCESS`.
- If the workflow cannot know the item universe, it must emit `FAILED_VALIDATION` with `UNKNOWN_ITEM_UNIVERSE` or an equivalent reason unless that uncertainty is an explicit workflow contract.
- If execution continues after an error (best-effort loops), still surface it:
  - record a terminal per-item outcome + reason
  - reflect partial failure at the run level (see `AGENTS.md` "Standard Log Schema (Required when logs are emitted)")

## Witnesses (enforcement)
- **Static**: the Python-safety check behind `scripts/check_governance_core/check_governance_core_main.py` flags `BARE_EXCEPT` and `SILENT_EXCEPT`, and warns on `EXCEPT_RETURN_LITERAL`.
- **Runtime**: emit per-item outcome records, user-visible terminal summary, and run summary with work-count reconciliation (see `AGENTS.md` "Standard Log Schema (Required when logs are emitted)").
