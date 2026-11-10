---
doc_type: playbook
ssot_owner: docs/agents/playbooks/run-outcomes/run-outcomes.md
update_trigger: per-item or per-run outcome, reconciliation, or user-facing result rules change
---

# Run Outcomes

Jurisdiction: per-item and per-run outcomes, their reconciliation, and user-facing result content.

```yaml
baseline:
  interface: the standard logging facility
  pattern: "one outcome vocabulary owner per application; logs, reports, and UI reuse it unchanged"
  reason: one outcome vocabulary for logs, reports, and UI; a second vocabulary drifts from the recorded run
  exception: none
```

- A run result MUST reconcile with its per-item outcomes; a mismatch is a failure.
- Zero executed work MUST NOT be reported as success.
- User cancellation or a declared deadline MUST NOT be reported as failure.
- User-facing results MUST NOT carry stack traces or raw payload dumps.
