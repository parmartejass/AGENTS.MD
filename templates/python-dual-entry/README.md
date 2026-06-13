# Python Dual-Entry Automation Template (GUI + CLI)

This folder is a copyable template for "dual-entry" automations:
- **Users** run a GUI.
- **Agents/Tests** run a CLI.

Both flows converge through the same parent connector in `myapp/myapp_main.py`, which is the only folder allowed to wire the child contracts into `myapp.runner.runner_main.run_job()`.

## Use it as inspiration (not a spec)

Follow the repo's first principles in `AGENTS.md`:
- discover existing SSOT owners in your target repo (config/constants/logging/workflows/tests)
- adopt/extend them instead of introducing parallel modules
- copy only the parts you need (CLI-only vs GUI+CLI)

If any wording here conflicts with `AGENTS.md`, `AGENTS.md` wins.

Project docs entrypoint: `docs/project/project_index.md`.

## Quickstart

```sh
cd templates/python-dual-entry
PYTHON_EXE=${PYTHON_EXE:-python3}

# Run a real-file scenario end-to-end (and verify output matches expected)
$PYTHON_EXE -m myapp --cli --scenario tests/scenarios/scenario_001_happy_path.json --verify

# Run all scenarios via the test harness (no third-party deps)
$PYTHON_EXE -m unittest -v

# Optional: write structured lifecycle events to a deterministic JSONL file
$PYTHON_EXE -m myapp --cli --scenario tests/scenarios/scenario_001_happy_path.json --verify --event-log tests/output/run.events.jsonl
```

If `--event-log` is not provided, events are written to:
- `run-logs/<YYYYMMDD>/<run_id>.jsonl`

Each run emits:
- `run_start`
- `phase_transition`
- `failure_event` (when applicable)
- `item_terminal`
- `run_end`

## Checks

Set `PYTHON_EXE` to a Python 3.11+ executable when `python3` is not suitable on the current machine.

- Template scenarios: `$PYTHON_EXE -m unittest -v`
- Project docs checks: `pwsh -NoProfile -ExecutionPolicy Bypass -File ../../scripts/check_project_docs.ps1 -RepoRoot . -PythonExe "$PYTHON_EXE"`
- Template docs SSOT header/router checks: `pwsh -NoProfile -ExecutionPolicy Bypass -File ../../scripts/check_docs_ssot.ps1 -RepoRoot . -GovernanceRoot ../.. -PythonExe "$PYTHON_EXE"`
- Folder architecture checks: `$PYTHON_EXE ../../scripts/check_folder_architecture/check_folder_architecture_main.py --root .`
- Python safety checks: `$PYTHON_EXE ../../scripts/check_python_safety/check_python_safety_main.py --root .`

Cwd-specific projections of the repo-root README Checks from this folder:
- Docs router contract regression test: `$PYTHON_EXE ../../scripts/check_docs_router_contract/check_docs_router_contract_main.py`
- Agents manifest checks: `pwsh -NoProfile -ExecutionPolicy Bypass -File ../../scripts/check_agents_manifest.ps1 -PythonExe "$PYTHON_EXE"`
- Repo hygiene checks: `pwsh -NoProfile -ExecutionPolicy Bypass -File ../../scripts/check_repo_hygiene.ps1 -RepoRoot ../.. -PythonExe "$PYTHON_EXE"`

## Where to look (SSOT)

- Canonical entry wrapper: `myapp/myapp_main.py`
- Package delegate for `python -m myapp`: `myapp/__main__.py`
- CLI folder contract: `myapp/cli/cli_main.py`
- GUI folder contract: `myapp/gui/gui_main.py`
- Orchestration folder contract: `myapp/runner/runner_main.py`
- Parent-only wiring rule: `myapp/myapp_main.py` is the only connector between `cli`, `gui`, `core`, and `runner`
- Runner-private workflow registry: `myapp/runner/workflows.py`
- Runner-private validation: `myapp/runner/validation.py`
- Runner-private text transform workflow: `myapp/runner/text_transform.py`
- Structured event contract: `myapp/log_contract.py`
- Structured event emitters: `myapp/observability.py`
- Logging setup + JSONL sink: `myapp/logging_config.py`
- Core business logic folder: `myapp/core/` (public contract: `myapp/core/core_main.py`)
- Scenarios (JSON): `tests/scenarios/`
- Fixtures + expected outputs: `tests/fixtures/`, `tests/expected/`
