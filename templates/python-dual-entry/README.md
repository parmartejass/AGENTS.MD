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

## Quickstart

```powershell
cd templates/python-dual-entry

# Run a real-file scenario end-to-end (and verify output matches expected)
python -m myapp --cli --scenario tests/scenarios/scenario_001_happy_path.json --verify

# Run all scenarios via the test harness (no third-party deps)
python -m unittest -v
```

## Where to look (SSOT)

- Entry dispatcher: `myapp/__main__.py`
- CLI entry: `myapp/cli_app.py`
- GUI entry: `myapp/gui_app.py`
- Orchestration: `myapp/runner.py`
- Workflow registry: `myapp/workflows.py`
- Core business logic: `myapp/core/`
- Scenarios (JSON): `tests/scenarios/`
- Fixtures + expected outputs: `tests/fixtures/`, `tests/expected/`

