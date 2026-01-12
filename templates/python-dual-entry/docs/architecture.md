---
doc_type: reference
ssot_owner: myapp/runner.py
update_trigger: entrypoints, workflow registry, or scenario harness changes
---

# Architecture (Dual-Entry)

## Entrypoints

- Dispatcher: `myapp/__main__.py`
- CLI: `myapp/cli_app.py`
- GUI: `myapp/gui_app.py`

## SSOT execution path

Both CLI and GUI call:

- Orchestration: `myapp/runner.py`
- Workflow registry: `myapp/workflows.py`
- Core logic (no GUI imports): `myapp/core/`

## Test path (real files)

- Scenarios: `tests/scenarios/*.json`
- Fixtures: `tests/fixtures/`
- Expected outputs: `tests/expected/`
- Harness: `tests/test_scenarios.py`

