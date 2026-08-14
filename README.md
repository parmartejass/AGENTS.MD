# AGENTS.MD (Repo) - Canonical Governance Pack

This repository maintains a reusable, repo-agnostic governance pack for autonomous coding agents.

## Canonical SSOT

- Canonical policy: `AGENTS.md`
- Assigned-lead and subagent authority-routing manifest: `agents-manifest.yaml`
- Cross-project authority decisions: `docs/agents/22-ssot-authority-decisions/ssot-authority-decisions.md`
- Governance-core public API and docs router contract: `scripts/check_governance_core/check_governance_core_main.py`
- Repository structure and Python-safety checks: `scripts/check_governance_core/check_governance_core_main.py`

## Read Order (Top-Down)

1. `AGENTS.md` (authoritative rules and hard gates)
2. The root/main reads and follows only `AGENTS.md` and the three authorities owned by its "Assigned-Lead Authority Routing Procedure (Hard Gate)".
3. The root/main delegates once using the canonical line owned by that procedure.
4. The assigned lead reads `agents-manifest.yaml`, resolves applicable task authorities, and owns the complete task/council workflow inside its subtree.
5. `docs/agents/agents_index.md` and project docs are read by the assigned lead when manifest triggers or routed authorities apply.

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
|  |- check_governance_core/
|  |  |- check_governance_core_main.py
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

Create these files in your project root so every coding assistant/tool lands on the same governance SSOT. The loader body is intentionally minimal: `.governance/AGENTS.md` owns the hard gates, root authorities, and role boundary; `.governance/agents-manifest.yaml` owns assigned-lead and subagent task routing.

Use this shared body for each loader:

```md
# <loader title>

Required loader:
- Open and follow `.governance/AGENTS.md` before doing any work.
- If `.governance/` is missing or empty in a fresh clone, run `git submodule update --init --recursive`.
- If you cannot access repository files, request that the user paste `.governance/AGENTS.md`.
- Follow the root/main boundary and canonical delegation route owned by `.governance/AGENTS.md` "Assigned-Lead Authority Routing Procedure (Hard Gate)"; the assigned lead owns all task-specific authority routing, council, execution, and verification work.
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
- Docs SSOT header checks (all `docs/` except index pages): `python3 scripts/check_governance_core/check_governance_core_main.py --only-docs-ssot --repo-root . --governance-root .` (use `python` if `python3` is unavailable)
- Project docs checks (required files + README linkage): `python3 scripts/check_governance_core/check_governance_core_main.py --only-project-docs --repo-root . --governance-root .` (use `python` if `python3` is unavailable)
- Cross-platform governance checks (manifest, docs, project docs, repository hygiene/structure, and Python safety): `python3 scripts/check_governance_core/check_governance_core_main.py` (use `python` if `python3` is unavailable)
  - Core governance regression tests: `python3 -m unittest discover -s scripts/check_governance_core -p "test*.py" -v` (use `python -m unittest discover -s ...` if `python3` is unavailable)
  - Strict safety mode: `python3 scripts/check_governance_core/check_governance_core_main.py --fail-on-safety-warnings`

Target repo (submodule under `.governance/`):
- Docs SSOT header checks: `python3 .governance/scripts/check_governance_core/check_governance_core_main.py --repo-root . --only-docs-ssot` (use `python` if `python3` is unavailable)
- Project docs checks: `python3 .governance/scripts/check_governance_core/check_governance_core_main.py --repo-root . --only-project-docs` (use `python` if `python3` is unavailable)
- Cross-platform governance checks: `python3 .governance/scripts/check_governance_core/check_governance_core_main.py --repo-root .` (use `python` if `python3` is unavailable)
  - Strict safety mode: `python3 .governance/scripts/check_governance_core/check_governance_core_main.py --repo-root . --fail-on-safety-warnings`

## Governance-core programmatic API

`scripts.check_governance_core.check_governance_core_main` is the only supported programmatic boundary. `run_checks(request)` accepts optional `repo_root`, `governance_root`, `mode` (`full`, `docs`, or `project_docs`), and `fail_on_safety_warnings`; it returns a plain mapping with `api_version`, terminal `status`, ordered per-check records, reconciled `planned`/`eligible`/`executed`/`skipped`/`failed` check IDs, `errors`, and `warnings`. `resolve_documents(request)` accepts explicit contained, non-aliased roots and returns `AGENTS.md` followed by the deterministic depth-first terminal Markdown leaves reachable from `docs/agents/agents_index.md`; `agents-manifest.yaml` routes tasks and does not define the research corpus. Invalid, escaped, aliased, missing, cyclic, or duplicate topology fails explicitly with an empty document list, so consumers do not maintain shadow file lists.

The API reads repository/governance files through one cached bounded filesystem inventory and uses bounded `git ls-files -z` only for owner-declared tracked-state rules. Git stdout and stderr are captured incrementally in bounded memory with a deadline and bounded cleanup; subprocess, capture, or cleanup failures produce explicit failed outcomes. Relevant readable file families reject aliases before consumers can open them and enforce byte limits only across files that family reads. Full mode composes all registered governance, docs, repository-structure, and Python-safety checks; narrow modes scan only their docs scope. Strict mode promotes safety warnings to failures. Generic `Popen` use remains a warning; Python safety keeps one explicit inventory-owner exception whose lifecycle is verified directly by failure-path tests. The API creates no temporary files and does not edit repository-owned files. Invalid inputs return `FAILED_VALIDATION`; check failures return `FAILED`. Consumers must not import private modules. Add a cohesive private handler plus one registry entry to extend checks; new request fields, modes, check IDs, or output fields require an intentional public-contract change with regression coverage.
