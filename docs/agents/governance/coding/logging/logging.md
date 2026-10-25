---
doc_type: policy
ssot_owner: docs/agents/governance/coding/logging/logging.md
update_trigger: logging channels, error taxonomy, catching policy, or silent-failure rules change
---

# Logging

Jurisdiction: logging channels, error taxonomy, explicit failure outcomes, and the catching and silent-failure rules for implementation code.

## Logging required
- MUST log workflow boundaries and failure points with context.
- Context MUST include paths, sheet, and row identifiers when applicable.
- MUST log through the logger instead of `print()`.
- MUST use a module-level logger (`logger = logging.getLogger(__name__)`).
- Logging MUST be configured exactly once, at the process entrypoint, through `dictConfig`.
- Handler attachment and level setting MUST happen only in that configuration.
- Redaction MUST be a logging filter attached in the configuration.
- That filter MUST apply the security owner's redaction rules to every record.
- Redaction MUST happen only in that filter, never at call sites.
- A file sink MUST declare a rotation trigger and a bounded backup count.
- MUST catch specific exceptions, log context, and raise meaningful domain errors.

## Baseline
```yaml
baseline:
  interface: the Python stdlib logging package configured once through logging.config.dictConfig
  pattern: "module-level getLogger(__name__); one dictConfig at the entrypoint; QueueHandler plus QueueListener in front of a JSON-lines file sink; redaction as a filter before the formatter"
  reason: "stdlib logging is the sink every library already writes into; a parallel logging facade orphans library records and duplicates configuration authority"
  exception: "a structured-logging processor layer only when it renders through the same stdlib handlers, recorded as one supersession"
```

## Log channels
- INFO: run boundaries, phase summaries, counts, artifact paths, terminal outcomes.
- Structured events: event payloads, timings, reason codes, counts, write effects, resource witnesses.
- DEBUG: deeper diagnostics, still redacted and payload-summarized.

## Error taxonomy
- The application's declared error owner MUST define its taxonomy.
- Example names only, non-normative: `ConfigError`, `ValidationError`, `ExcelComError`, `FileIOError`, `WorkflowError`.

## Catching policy
- Prohibited: bare `except`, and catch-all patterns that hide the cause.
- MUST catch specific exception categories (file, JSON, subprocess, library-specific).

## Silent failures
- Broad exception handlers MUST keep failures visible.
- Prohibited: `except Exception: pass`.
- Prohibited: `except Exception: return None/False/...`, unless the sentinel is an explicit contract.
- The Lexicon (ssot) defines an explicit contract for a sentinel.
- Otherwise MUST record context and outcome, or raise a domain error.
- A branch with unresolvable config/rule/intent authority MUST stop with `FAILED` or `SKIPPED + reason`.
- Prohibited: orchestration code inferring, duplicating or silently defaulting that business rule.

## Witnesses
- Static: the Python-safety check behind the governance-core package public contract (`scripts/check_governance_core/`) flags `BARE_EXCEPT`, `SILENT_EXCEPT` and warns `EXCEPT_RETURN_LITERAL`.
- Runtime: one recorded dictConfig call, a listener started and then stopped in `finally`, and a redaction filter on every handler.
