# AGENTS.MD (Repo) - Canonical Governance Pack

This repository maintains a reusable, repo-agnostic governance pack for autonomous coding agents.

## Canonical SSOT

- Canonical policy: `AGENTS.md`
- Context injection manifest: `agents-manifest.yaml`
- Cross-project authority decisions: `docs/agents/22-ssot-authority-decisions/ssot-authority-decisions.md`
- Folder-owned public contract filename registry: `scripts/entrypoint_contracts.json`

## Read Order (Top-Down)

1. `AGENTS.md` (authoritative rules and hard gates)
2. `agents-manifest.yaml` (context injection and profile routing)
3. `docs/agents/agents_index.md` (supporting branch map and when-to-read guidance)
4. Task-specific supporting docs/playbooks under `docs/agents/`
5. Project docs entrypoint: `docs/project/project_index.md` (goal, rules, architecture/protected behavior, data-truth, learning)

When vendored as `.governance/` in a target repo, use `.governance/AGENTS.md` and `.governance/agents-manifest.yaml`.

## Project docs (this repo)

- Entry point: `docs/project/project_index.md` (goal, rules, architecture/protected behavior, data-truth, learning)
- Project docs provide bounded authority memory only for durable truths that change future allowed behavior.
- Facts are owned by declared SSOT owners, not by file type; project docs may own data/config/constant/default facts when explicitly declared and validated.

## Repo-owned agent assets

- Canonical reusable platform assets live under `docs/agents/`.
- Current repo-owned asset classes:
  - Skills: `docs/agents/skills/`
  - Settings: `docs/agents/settings/`
  - MCP configs: `docs/agents/mcp/`
- Platform runtime policy lives in `docs/agents/platforms/00-platform-runtime-standards/platform-runtime-standards.md`.
- Concrete runtime path/support-level facts live in `docs/agents/platforms/runtime-projections.json`.
- Dated platform/runtime evidence lives in `docs/agents/platforms/platforms_index.md`.
- Runtime projection sources resolve from the governance root; runtime targets resolve from the project root (or `{HOME}` when explicitly declared).
- Use `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/setup_repo_platform_assets.ps1 -Force` to project supported assets into runtime locations for this repo.
- Default setup does not project repo-owned subagent runtime files or create `.cursor/rules/`.
- Legacy `.claude/agents/` and `.codex/agents/` surfaces from older checkouts are local-only after subagent projection retirement; remove stale copies manually if they conflict with `AGENTS.md`.
- Conflicting user-owned runtime files such as a non-link `.mcp.json` can cause setup to stop with an explicit error until you rename or remove the conflicting path.
- When vendored as `.governance/`, the linker auto-targets the parent project root and also accepts `-RepoRoot` for an explicit override.
- If the repo moves to a new filesystem path, rerun `scripts/setup_repo_platform_assets.ps1 -Force` so projections are rebuilt.

## Tool loader stubs

- `AGENTS.md` (required loader stub)
- `CLAUDE.md` (required Claude Code loader stub)

## Supporting docs

- Index: `docs/agents/agents_index.md`
- Authority decisions: `docs/agents/22-ssot-authority-decisions/ssot-authority-decisions.md`
- Facts and behavior must stay in their declared SSOT owner, which may be code, config, constants, artifacts, external systems, schemas, workbooks, or explicitly declared project docs (see `docs/agents/25-docs-ssot-policy/docs-ssot-policy.md`).

## Templates (reference implementations)

- Routing index: [`templates/templates_index.md`](templates/templates_index.md)
- Dual-entry GUI+CLI + scenario tests: `templates/python-dual-entry/`
  - Reference implementation only: follow `AGENTS.md` discovery/adoption rules; copy patterns, not files.
  - Run one scenario: `cd templates/python-dual-entry; python3 -m myapp --cli --scenario tests/scenarios/scenario_001_happy_path.json --verify`
  - Run all scenarios: `cd templates/python-dual-entry; python3 -m unittest -v`
  - If your Python 3 binary is named `python`, replace `python3` with `python`.

## Repo structure

```text
.
|- AGENTS.md
|- agents-manifest.yaml
|- docs/
|  |- docs_index.md
|  |- agents/
|  |  |- agents_index.md
|  |  |- 00-principles/
|  |  |  |- principles_index.md
|  |  |- 35-authority-bounded-modules/
|  |  |  |- authority-bounded-modules_index.md
|  |  |- playbooks/
|  |  |  |- playbooks_index.md
|  |  |  |- design-principles-checklist/
|  |  |  |  |- design-principles-checklist_index.md
|  |  |- platforms/
|  |  |  |- platforms_index.md
|  |  |  |- 00-platform-runtime-standards/
|  |  |  |  |- platform-runtime-standards_index.md
|  |  |- settings/
|  |  |  |- settings_index.md
|  |  |- skills/
|  |  |  |- skills_index.md
|  |- project/
|     |- project_index.md
|     |- architecture/
|     |  |- architecture_index.md
|     |- data-truth/
|     |  |- data-truth_index.md
|     |  |- data-truth.md
|     |- goal/
|     |  |- goal_index.md
|     |  |- goal.md
|     |- learning/
|     |  |- learning_index.md
|     |- rules/
|        |- rules_index.md
|- scripts/
|  |- check_folder_architecture/
|  |  |- check_folder_architecture_main.py
|  |- check_governance_core/
|  |  |- check_governance_core_main.py
|  |- check_python_safety/
|  |  |- check_python_safety_main.py
|  |- *.ps1
|- templates/
|  |- templates_index.md
|  |- python-dual-entry/
|  |  |- myapp/
|  |     |- cli/cli_main.py
|  |     |- core/core_main.py
|  |     |- gui/gui_main.py
|  |     |- myapp_main.py
|  |     |- runner/runner_main.py
|  |     |- runner/workflows.py
```

Project docs-first truth is owned by the durable project docs routed from `docs/project/project_index.md`; new project docs must be routed owner docs with declared scope, update triggers, and verification witnesses.

## Use in other repos (submodule)

> IMPORTANT: Git does not auto-pull submodules by default.
>
> When cloning a repo that uses this pack, you must use `--recurse-submodules`:
>
> ```powershell
> git clone --recurse-submodules <repo-url>
> ```
>
> Otherwise `.governance/` will be empty. See "Cloning a repo that uses this pack" below.

### Step 1: Add the governance pack as a submodule

```powershell
cd "C:\path\to\your\project"
git submodule add -b main https://github.com/parmartejass/AGENTS.MD.git .governance
```

### Step 2: Create loader stubs at project root

Create these files in your project root so every coding assistant/tool lands on the same governance SSOT. The loader body is intentionally minimal: `.governance/AGENTS.md` owns the hard gates and context-injection procedure, and `.governance/agents-manifest.yaml` owns routing facts.

Use this shared body for each loader:

```md
# <loader title>

Required loader:
- Open and follow `.governance/AGENTS.md` before doing any work.
- If `.governance/` is missing or empty in a fresh clone, run `git submodule update --init --recursive`.
- If you cannot access repository files, request that the user paste `.governance/AGENTS.md`.
- After reading `.governance/AGENTS.md`, execute its current Context Injection Procedure.
- Project-specific docs remain under `docs/project/`.
```

Loader titles:
- `AGENTS.md` (required): `# AGENTS.md (Loader Stub)`
- `CLAUDE.md` (required for Claude Code): `# CLAUDE.md (Loader Stub)`

**Note**:
- Keep your project docs under `docs/project/` (do not copy `docs/agents` into the project root).

### Step 3: Commit

```powershell
git add .
git commit -m "Add governance pack as submodule"
```

### Updating governance (when pack gets updates)

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .governance/scripts/sync-governance.ps1
git add .governance
git commit -m "Update governance pack"
```

### Editing governance (from inside a project)

Changes to `.governance/` must be committed to the submodule repo (`AGENTS.MD`), not the parent.

```powershell
# 1. Go INTO the submodule
cd .governance

# 2. Make sure you're on main and up to date
git checkout main
git pull origin main

# 3. Create branch, edit, commit, push
git checkout -b fix/my-change
# ... make edits ...
git add .
git commit -m "My change"
git push origin fix/my-change

# 4. Create PR in AGENTS.MD repo (github.com/parmartejass/AGENTS.MD), merge to main

# 5. Back in parent repo, update pointer to latest main
cd ..
git submodule update --remote .governance
git add .governance
git commit -m "Update governance"
```

> WARNING: Do not commit `.governance/` changes from the parent repo directory.
> The parent only tracks a pointer (SHA) to a commit; it cannot store file changes.

### Cloning a repo that uses this pack

**Option A: Clone with submodules (recommended)**

```powershell
git clone --recurse-submodules <repo-url>
```

**Option B: Already cloned without submodules? Initialize manually:**

```powershell
git submodule update --init
```

**Option C: Pull updates including submodule changes:**

```powershell
git pull --recurse-submodules
```

Note: If `.governance/` folder is empty, run `git submodule update --init`.

### Troubleshooting

| Problem | Solution |
|---------|----------|
| `.governance/` is empty | `git submodule update --init` |
| Submodule shows "modified" but you didn't change it | Check for local edits in `.governance/` first (`git -C .governance status --short`), then run `git submodule update --force .governance` only if you intend to discard those local edits |
| Accidentally edited from parent repo | Go into `.governance/`, commit there, push, then update parent |
| Changes not appearing after update | `git submodule update --remote .governance` |
| Detached HEAD in submodule | From inside `.governance/`: `git checkout main`, then `git pull origin main` |

## Checks

Python checks require Python 3.11+.
Python-backed PowerShell wrappers (`setup_repo_platform_assets.ps1`, `check_docs_ssot.ps1`, `check_project_docs.ps1`) accept `-PythonExe <path>` when `python3`/`python` do not resolve to Python 3.11+.
When `-PythonExe` is omitted, these scripts use the resolver declared in `scripts/_python_check_runner.ps1` and print the selected executable when Python-backed validation runs. Validator wrappers require a validator success marker before reporting success.
On macOS or POSIX shells where `powershell` is unavailable, use `pwsh` for the same PowerShell commands. On this machine, use `/opt/homebrew/bin/python3.12` for bare Python checks and pass `-PythonExe /opt/homebrew/bin/python3.12` to Python-backed PowerShell wrappers when the default `python3` is below 3.11. For template commands, set `PYTHON_EXE=/opt/homebrew/bin/python3.12` when the default `python3` is below 3.11.

This repo:
- Platform asset bootstrap/repair smoke (writes the repo-owned runtime projections): `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/setup_repo_platform_assets.ps1 -Force`
  - If `python3`/`python` do not resolve to Python 3.11+, pass `-PythonExe <path>` for TOML settings validation.
  - Default path witness: `.cursor/rules/` is not created and no repo-owned subagent runtime projection is attempted.
  - If setup stops on a conflicting non-link runtime file such as `.mcp.json`, rename or remove that path and rerun.
  - If setup stops on a plain directory-link stub that points to the canonical source, rerun with `-Force -RepairPlainDirectoryStubs`.
- Docs SSOT header checks (all `docs/` except index pages): `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/check_docs_ssot.ps1`
  - PowerShell wrapper for the Python docs SSOT/router validator.
- Docs router contract regression test: `python3 scripts/check_docs_router_contract/check_docs_router_contract_main.py` (use `python` if `python3` is unavailable)
- Agents manifest checks: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/check_agents_manifest.ps1`
- Project docs checks (required files + README linkage): `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/check_project_docs.ps1`
- Repo hygiene checks (no runtime/generated artifact noise tracked): `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/check_repo_hygiene.ps1`
- Folder architecture checks (declared Python roots, explicit workspace exceptions, and repo-owned/template folder contracts): `python3 scripts/check_folder_architecture/check_folder_architecture_main.py` (use `python` if `python3` is unavailable)
- Folder architecture regression tests (vendored governance boundary + scope): `python3 -m unittest -v scripts/check_folder_architecture/test_main.py` (use `python -m unittest -v ...` if `python3` is unavailable)
- Cross-platform core governance checks (manifest + docs SSOT + project docs + governance authority decisions + hygiene + playbook parity + unresolved citation tokens): `python3 scripts/check_governance_core/check_governance_core_main.py` (use `python` if `python3` is unavailable)
  - Core governance regression tests: `python3 -m unittest discover -s scripts/check_governance_core -p "test*.py" -v` (use `python -m unittest discover -s ...` if `python3` is unavailable)
  - Strict safety mode: `python3 scripts/check_governance_core/check_governance_core_main.py --fail-on-safety-warnings`
- Python safety baseline checks: `python3 scripts/check_python_safety/check_python_safety_main.py` (add `--fail-on-warnings` to enforce warnings; use `python` if `python3` is unavailable)
- Template structured logging contract tests: `cd templates/python-dual-entry && python3 -m unittest -v tests.test_logging_contract` (use `python` if `python3` is unavailable)

Target repo (submodule under `.governance/`):
- Docs SSOT header checks: `powershell -NoProfile -ExecutionPolicy Bypass -File .governance/scripts/check_docs_ssot.ps1 -RepoRoot .`
  - PowerShell wrapper for the Python docs SSOT/router validator.
- Docs router contract regression test: `python3 .governance/scripts/check_docs_router_contract/check_docs_router_contract_main.py` (use `python` if `python3` is unavailable)
- Agents manifest checks: `powershell -NoProfile -ExecutionPolicy Bypass -File .governance/scripts/check_agents_manifest.ps1`
- Project docs checks: `powershell -NoProfile -ExecutionPolicy Bypass -File .governance/scripts/check_project_docs.ps1 -RepoRoot .`
- Repo hygiene checks: `powershell -NoProfile -ExecutionPolicy Bypass -File .governance/scripts/check_repo_hygiene.ps1 -RepoRoot .`
- Folder architecture checks: `python3 .governance/scripts/check_folder_architecture/check_folder_architecture_main.py --root .` (use `python` if `python3` is unavailable)
- Cross-platform core governance checks: `python3 .governance/scripts/check_governance_core/check_governance_core_main.py --repo-root .` (use `python` if `python3` is unavailable)
  - Strict safety mode: `python3 .governance/scripts/check_governance_core/check_governance_core_main.py --repo-root . --fail-on-safety-warnings`
- Python safety baseline checks: `python3 .governance/scripts/check_python_safety/check_python_safety_main.py --root .` (add `--fail-on-warnings` to enforce warnings; use `python` if `python3` is unavailable)
