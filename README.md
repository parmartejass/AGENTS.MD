# AGENTS.MD (Repo) - Canonical Governance Pack

This repository maintains a reusable, repo-agnostic governance pack for autonomous coding agents.

## Canonical SSOT

- Canonical policy: `AGENTS.md`
- Context injection manifest: `agents-manifest.yaml`
- Cross-project authority decisions: `docs/agents/22-ssot-authority-decisions/ssot-authority-decisions.md`
- Docs router filename contract: `scripts/check_governance_core/_docs_routes.py`
- Python script entrypoint contract: `scripts/check_folder_architecture/check_folder_architecture_main.py`

## Read Order (Top-Down)

1. `AGENTS.md` (authoritative rules and hard gates)
2. `agents-manifest.yaml` (context injection and profile routing)
3. `docs/agents/agents_index.md` (supporting branch map and when-to-read guidance)
4. Task-specific supporting docs/playbooks under `docs/agents/`
5. Project docs entrypoint: `docs/project/project_index.md` (goal, rules, architecture/protected behavior, data-truth, learning)

When vendored as `.governance/` in a target repo, use `.governance/AGENTS.md` and `.governance/agents-manifest.yaml`.

## Project docs (this repo)

- Entry point: `docs/project/project_index.md` (goal, rules, architecture/protected behavior, data-truth, changelog, learning)
- Project docs provide bounded authority memory for durable truths that change future allowed behavior plus tracked closure records for completed non-trivial work.
- Facts are owned by declared SSOT owners, not by file type; project docs may own data/config/constant/default facts when explicitly declared and validated.

## Repo-owned agent assets

- Canonical reusable platform assets live under `docs/agents/`.
- Current repo-owned asset classes:
  - Skills: `docs/agents/skills/`
  - Settings: `docs/agents/settings/`
  - MCP configs: `docs/agents/mcp/`
- Runtime installation is consumer-owned; this repo does not track root runtime copies or projection mappings.

## Tool loader stubs

- `AGENTS.md` (required loader stub)
- `CLAUDE.md` (required Claude Code loader stub)

## Supporting docs

- Index: `docs/agents/agents_index.md`
- Authority decisions: `docs/agents/22-ssot-authority-decisions/ssot-authority-decisions.md`
- Facts and behavior must stay in their declared SSOT owner, which may be code, config, constants, artifacts, external systems, schemas, workbooks, or explicitly declared project docs (see `docs/agents/25-docs-ssot-policy/docs-ssot-policy.md`).

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
|  |  |- 35-coding-principles/
|  |  |  |- coding-principles_index.md
|  |  |- playbooks/
|  |  |  |- playbooks_index.md
|  |  |- settings/
|  |  |  |- settings_index.md
|  |  |- skills/
|  |  |  |- skills_index.md
|  |- project/
|     |- project_index.md
|     |- architecture/
|     |  |- architecture_index.md
|     |- changelog/
|     |  |- changelog_index.md
|     |  |- changelog.md
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
git -C .governance checkout main
git -C .governance pull --ff-only origin main
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
If your Python 3 binary is named `python`, replace `python3` with `python`.

This repo:
- Docs router contract regression test: `python3 scripts/check_docs_router_contract/check_docs_router_contract_main.py` (use `python` if `python3` is unavailable)
- Docs SSOT header checks (all `docs/` except index pages): `python3 scripts/check_governance_core/check_governance_core_main.py --only-docs-ssot --repo-root . --governance-root .` (use `python` if `python3` is unavailable)
- Project docs checks (required files + README linkage): `python3 scripts/check_governance_core/check_governance_core_main.py --only-project-docs --repo-root . --governance-root .` (use `python` if `python3` is unavailable)
- Folder architecture checks (declared Python roots, explicit workspace exceptions, and script folder contracts): `python3 scripts/check_folder_architecture/check_folder_architecture_main.py` (use `python` if `python3` is unavailable)
- Folder architecture regression tests (vendored governance boundary + scope): `python3 -m unittest -v scripts/check_folder_architecture/test_main.py` (use `python -m unittest -v ...` if `python3` is unavailable)
- Cross-platform core governance checks (manifest + docs SSOT + project docs + governance authority decisions + hygiene + playbook parity + unresolved citation tokens): `python3 scripts/check_governance_core/check_governance_core_main.py` (use `python` if `python3` is unavailable)
  - Core governance regression tests: `python3 -m unittest discover -s scripts/check_governance_core -p "test*.py" -v` (use `python -m unittest discover -s ...` if `python3` is unavailable)
  - Strict safety mode: `python3 scripts/check_governance_core/check_governance_core_main.py --fail-on-safety-warnings`
- Python safety baseline checks: `python3 scripts/check_python_safety/check_python_safety_main.py` (add `--fail-on-warnings` to enforce warnings; use `python` if `python3` is unavailable)

Target repo (submodule under `.governance/`):
- Docs router contract regression test: `python3 .governance/scripts/check_docs_router_contract/check_docs_router_contract_main.py` (use `python` if `python3` is unavailable)
- Docs SSOT header checks: `python3 .governance/scripts/check_governance_core/check_governance_core_main.py --repo-root . --only-docs-ssot` (use `python` if `python3` is unavailable)
- Project docs checks: `python3 .governance/scripts/check_governance_core/check_governance_core_main.py --repo-root . --only-project-docs` (use `python` if `python3` is unavailable)
- Folder architecture checks: `python3 .governance/scripts/check_folder_architecture/check_folder_architecture_main.py --root .` (use `python` if `python3` is unavailable)
- Cross-platform core governance checks: `python3 .governance/scripts/check_governance_core/check_governance_core_main.py --repo-root .` (use `python` if `python3` is unavailable)
  - Strict safety mode: `python3 .governance/scripts/check_governance_core/check_governance_core_main.py --repo-root . --fail-on-safety-warnings`
- Python safety baseline checks: `python3 .governance/scripts/check_python_safety/check_python_safety_main.py --root .` (add `--fail-on-warnings` to enforce warnings; use `python` if `python3` is unavailable)
