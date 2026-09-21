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
  pattern: "one hook per hard gate, scoped by matcher, blocking through the runtime's deny contract, with a declared timeout; the obligation stays owned by its jurisdiction"
  reason: "instruction files are context, not enforced configuration; a hook is the only mechanism that blocks an action regardless of model judgment"
  exception: none
```

## Enforcement
- A hard gate that must hold regardless of model judgment MUST have a hook, not only a prose rule.
- A hook enforces an obligation owned by a named jurisdiction; it MUST NOT be the only record of a rule.
- Session-lifecycle hooks MUST NOT re-inject a source the runtime already loads.

## Hook contract
- A blocking hook MUST return the runtime's deny contract with a reason; other non-zero exits are non-blocking warnings.
- A hook MUST be scoped by matcher to the tool calls it governs; a hook that fires on every call is Prohibited.
- A hook MUST declare its timeout.
- A hook that mutates the tool call MUST use the runtime's `updatedInput` contract and Record the mutation.

## Safety
- A committed hook MUST be reviewed as executable code under the security jurisdiction before merge.
- A hook that interpolates a secret MUST list it explicitly (`allowedEnvVars`); a literal secret in a hook is Prohibited.
- `disableAllHooks` MUST NOT be set in a committed payload.
