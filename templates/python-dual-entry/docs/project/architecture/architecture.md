---
doc_type: reference
ssot_owner: myapp/runner/runner_main.py
update_trigger: entrypoints, workflow registry, or scenario harness changes
---

# Architecture (Dual-Entry)

## Boundary
- This root doc owns template entrypoint, folder-contract, owner, and execution-flow routing.
- It does not own reusable governance policy, template goals, data-truth routing, or operational learnings.

## When to create a branch-local owner subdoc
- Create an architecture subdoc when a stable structural truth cluster needs its own intent, boundary, invariant, change rule, and verification.
- Keep folder-contract mechanics in the runtime owners and reusable governance policy; route by identifier here.

## Current Summary
- `myapp/myapp_main.py` remains the only connector between CLI, GUI, and runner contracts.
- No branch-local architecture subdocs are declared.

## Branch-local owner subdocs
- None currently declared.

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
