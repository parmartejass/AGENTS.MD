---
doc_type: policy
ssot_owner: docs/agents/governance/coding/logging/logging.md
update_trigger: logging outcomes, the print prohibition, or silent-failure rules change
---

# Logging

Jurisdiction: logging outcomes and the silent-failure rules for implementation code.

```yaml
baseline:
  interface: the Python stdlib logging package
  pattern: "library and application records reach one configured sink with identifying context; secrets redacted"
  reason: "stdlib logging is the sink every library already writes into; a parallel logging facade orphans library records and duplicates configuration authority"
  exception: none
```

- MUST log workflow boundaries and failures with identifying context.
- Code MUST NOT call `print()`.
- MUST NOT hide or swallow a failure; every caught failure is logged with context and re-raised or returned as a contracted outcome.
