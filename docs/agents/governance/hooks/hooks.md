---
doc_type: policy
ssot_owner: docs/agents/governance/hooks/hooks.md
update_trigger: hook enforcement scope, blocking contract, or committed-hook review rules change
---

# Hooks

Jurisdiction: deterministic enforcement of hard gates through runtime hooks declared in committed platform payloads.

## Baseline
```yaml
baseline:
  interface: the runtime's native hook configuration inside the committed platform settings payload
  pattern: "each enforced hard gate blocks deterministically through the runtime's deny contract; the obligation stays owned by its jurisdiction"
  reason: "instruction files are context, not enforced configuration; a hook is the only mechanism that blocks an action regardless of model judgment"
  exception: none
```

## Rules
- A hard gate that must hold regardless of model judgment MUST be enforced deterministically, not only instructed.
- A hook MUST NOT be the only record of a rule; the obligation stays with its owning jurisdiction.
- Session-lifecycle hooks MUST NOT re-inject a source the runtime already loads.
- Only the runtime's deny contract blocks; other non-zero exits are non-blocking warnings.
- A hook that mutates the tool call MUST use the runtime's `updatedInput` contract and Record the mutation.
- A committed hook MUST be reviewed as executable code before merge.
- A hook that interpolates a secret MUST list it in `allowedEnvVars`; a hook MUST NOT contain a literal secret.
- `disableAllHooks` MUST NOT be set in a committed payload.
