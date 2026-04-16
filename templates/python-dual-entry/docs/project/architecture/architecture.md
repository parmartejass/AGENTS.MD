---
doc_type: reference
ssot_owner: myapp/runner/runner_main.py
update_trigger: entrypoints, workflow registry, or scenario harness changes
---

# Architecture (Dual-Entry)

## Entrypoints

- Canonical wrapper: `myapp/myapp_main.py`
- Package delegate (`python -m myapp`): `myapp/__main__.py`
- CLI: `myapp/cli/cli_main.py`
- GUI: `myapp/gui/gui_main.py`

## SSOT execution path

`myapp/myapp_main.py` is the only connector between the child folders. It wires:

- CLI request-building contract: `myapp/cli/cli_main.py`
- GUI startup contract: `myapp/gui/gui_main.py`
- Orchestration: `myapp/runner/runner_main.py`
- Runner-private workflow registry: `myapp/runner/workflows.py`
- Runner-private validation: `myapp/runner/validation.py`
- Runner-private text transform workflow: `myapp/runner/text_transform.py`
- Core logic (no GUI imports): `myapp/core/`
- Structured event contract: `myapp/log_contract.py`
- Structured event emitters: `myapp/observability.py`
- Logging setup + JSONL sink: `myapp/logging_config.py`

## Test path (real files)

- Scenarios: `tests/scenarios/*.json`
- Fixtures: `tests/fixtures/`
- Expected outputs: `tests/expected/`
- Harness: `tests/test_scenarios.py`
