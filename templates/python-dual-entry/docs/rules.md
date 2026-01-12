---
doc_type: policy
ssot_owner: AGENTS.md
update_trigger: repo governance rules change
---

# Rules (Do / Don't)

## Do

- Keep GUI/CLI thin; construct config and call `myapp.runner.run_job()`.
- Centralize shared literals and JSON keys (SSOT) in one owner (example: `myapp/config_keys.py`).
- Add scenarios as JSON + real fixtures + expected outputs; ensure the harness runs them all.
- Log workflow boundaries and explicit failures (no silent skips).

## Don't

- Don't duplicate business logic between UI layers.
- Don't add ad-hoc "helper" copies for the same responsibility.
- Don't leave partial outputs behind (use a temp file + atomic replace).
