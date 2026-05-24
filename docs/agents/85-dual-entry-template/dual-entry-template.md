---
doc_type: reference
ssot_owner: templates/python-dual-entry/myapp/runner/runner_main.py
update_trigger: template project layout or scenario format changes
---

# 85 - Dual-Entry Template (GUI + CLI + Real-File Scenarios)

This repo keeps *governance* in `AGENTS.md`, and keeps a **reference implementation** for a dual-entry automation in the template directory.

This template is **not a spec**. It exists so agents can copy *patterns* while still doing project-specific discovery and adopting existing SSOT owners.

## SSOT (reference implementation)

- Template root: `templates/python-dual-entry/`
- Parent folder contract: `templates/python-dual-entry/myapp/myapp_main.py`
- Runtime shim: `templates/python-dual-entry/myapp/__main__.py`
- CLI child entry (thin): `templates/python-dual-entry/myapp/cli/cli_main.py`
- GUI child entry (thin): `templates/python-dual-entry/myapp/gui/gui_main.py`
- Orchestration SSOT (runtime coordinator only): `templates/python-dual-entry/myapp/runner/runner_main.py`
- Runner private workflow registry: `templates/python-dual-entry/myapp/runner/workflows.py`
- Core logic SSOT: `templates/python-dual-entry/myapp/core/core_main.py`
- Scenario schema keys SSOT: `templates/python-dual-entry/myapp/config_keys.py`

## How to use it (avoid blind copying)

- Start with target-repo discovery: follow `docs/agents/10-repo-discovery/repo-discovery.md`.
- Adopt existing owners first: extend the repo's current config/constants/rules/logging/workflow registry instead of introducing parallel modules.
- Copy only the needed parts:
  - CLI-only automation: keep dispatcher+CLI+runner+workflow registry+scenario harness; skip the GUI.
  - GUI+CLI automation: keep both child entry layers thin and route everything through the parent contract plus `run_job()`.
- Prefer dependency-minimal verification: the template uses stdlib `unittest` so agents can run real scenarios without extra installs; if a repo already uses `pytest`, integrate there rather than requiring it.

## Project-based checklist (reason before you copy)

- Workflow registry exists and is indexed: `docs/agents/workflow-registry/workflow-registry.md`.
- Config keys and repeated literals have a single owner (avoid duplicates): `docs/agents/40-config-constants/config-constants.md`.
- Real-file scenarios cover at least one happy path and one failure path: `docs/agents/80-testing-real-files/testing-real-files.md`.
- If a GUI is involved, cancellation and queue/drain invariants are enforced: `docs/agents/60-gui-threading/gui-threading.md`.
- If Excel COM is involved, lifecycle is PID-scoped and time-bounded: `docs/agents/50-excel-com-lifecycle/excel-com-lifecycle.md`.

## Minimal project docs set (copy, then customize)

For the recommended minimal project docs set, see `AGENTS.md` "Documentation SSOT Policy (Hard Gate)".
This template provides an example implementation under `templates/python-dual-entry/docs/project/project_index.md`.

## Deterministic verification (copy/paste)

```powershell
cd templates/python-dual-entry

# Run a single scenario end-to-end and verify output vs expected
python -m myapp --cli --scenario tests/scenarios/scenario_001_happy_path.json --verify

# Run all JSON scenarios via the harness
python -m unittest -v
```

## Adding a new scenario (minimal)

1) Add a scenario JSON under `templates/python-dual-entry/tests/scenarios/`.
2) Add any input fixtures under `templates/python-dual-entry/tests/fixtures/`.
3) Add expected outputs under `templates/python-dual-entry/tests/expected/`.
4) Run `python -m unittest -v`.
