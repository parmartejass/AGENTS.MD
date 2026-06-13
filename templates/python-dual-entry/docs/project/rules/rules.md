---
doc_type: policy
ssot_owner: AGENTS.md
update_trigger: repo governance rules change
---

# Rules (Do / Don't)

## Boundary
- This root doc owns template-local constraints that supplement the reusable governance pack.
- It does not own reusable governance policy, runtime architecture, data-truth routing, or task status.

## When to create a branch-local owner subdoc
- Create a rules subdoc when a stable template-specific constraint needs its own intent, boundary, invariant, change rule, and verification.
- Do not duplicate reusable governance policy in template rules subdocs.

## Current Summary
- Current rules keep the template thin, deterministic, and scenario-backed.
- No branch-local rules subdocs are declared.

## Branch-local owner subdocs
- None currently declared.

## Do

- Keep GUI/CLI thin; let `myapp/myapp_main.py` be the only connector that wires child folder contracts into `myapp.runner.runner_main.run_job()`.
- Centralize shared literals and JSON keys (SSOT) in one owner (example: `myapp/config_keys.py`).
- Add scenarios as JSON + real fixtures + expected outputs; ensure the harness runs them all.
- Log workflow boundaries and explicit failures (no silent skips).

## Don't

- Don't duplicate business logic between UI layers.
- Don't add ad-hoc "helper" copies for the same responsibility.
- Don't leave partial outputs behind (use a temp file + atomic replace).
