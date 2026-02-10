# Python Dual-Entry Automation Template (GUI + CLI)

This folder is a copyable template for "dual-entry" automations:
- **Users** run a GUI.
- **Agents/Tests** run a CLI.

Both entry points call the same orchestration function: `myapp.runner.run_job()`.

## Use it as inspiration (not a spec)

Follow the repo's first principles in `AGENTS.md`:
- discover existing SSOT owners in your target repo (config/constants/logging/workflows/tests)
- adopt/extend them instead of introducing parallel modules
- copy only the parts you need (CLI-only vs GUI+CLI)

If any wording here conflicts with `AGENTS.md`, `AGENTS.md` wins.

## Quickstart

```powershell
cd templates/python-dual-entry

# Run a real-file scenario end-to-end (and verify output matches expected)
python -m myapp --cli --scenario tests/scenarios/scenario_001_happy_path.json --verify

# Run all scenarios via the test harness (no third-party deps)
python -m unittest -v

# Optional: write structured lifecycle events to a deterministic JSONL file
python -m myapp --cli --scenario tests/scenarios/scenario_001_happy_path.json --verify --event-log tests/output/run.events.jsonl
```

If `--event-log` is not provided, events are written to:
- `run-logs/<YYYYMMDD>/<run_id>.jsonl`

Each run emits:
- `run_start`
- `phase_transition`
- `failure_event` (when applicable)
- `item_terminal`
- `run_end`

## Where to look (SSOT)

- Canonical entry wrapper: `myapp/main.py`
- Package delegate for `python -m myapp`: `myapp/__main__.py`
- CLI entry: `myapp/cli_app.py`
- GUI entry: `myapp/gui_app.py`
- Orchestration: `myapp/runner.py`
- Workflow registry: `myapp/workflows.py`
- Structured event contract: `myapp/log_contract.py`
- Structured event emitters: `myapp/observability.py`
- Logging setup + JSONL sink: `myapp/logging_config.py`
- Core business logic: `myapp/core/`
- Scenarios (JSON): `tests/scenarios/`
- Fixtures + expected outputs: `tests/fixtures/`, `tests/expected/`
