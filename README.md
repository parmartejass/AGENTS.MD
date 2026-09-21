# AGENTS.MD (Repo) - Canonical Governance Pack

This repository maintains a reusable, repo-agnostic governance pack for autonomous coding agents.

## Canonical SSOT

- Fundamental Principles, constitutional policy, and conflict precedence: `AGENTS.md`
- Agent roles and finite workflow: `Orchestration.md`
- Governance Agent authority-routing manifest: `agents-manifest.yaml`
- Cross-project authority decisions: `docs/agents/governance/ssot/authority-decisions/authority-decisions.md`
- Governance-core public API, docs router contract, repository structure, and Python-safety checks: `scripts/check_governance_core/check_governance_core_main.py`

## Read Order (Top-Down)

1. Open `AGENTS.md`, the constitutional owner and sole Mandatory Foundations declaration.
2. Complete its declared foundation loading and application through `Orchestration.md`, which owns parent accountability and source boundaries.
3. Governance Agent routes additional applicable governance-only authorities through `agents-manifest.yaml`; profiles do not make foundations conditional.
4. Role-bounded agents read applicable deeper sources as permitted by `Orchestration.md`; owner-declared duties and optionality remain controlling.

When vendored as `.governance/` in a target repo, use `.governance/AGENTS.md`, `.governance/Orchestration.md`, and `.governance/agents-manifest.yaml`.

## Project docs (this repo)

- Entry point: `docs/project/project_index.md` (goal, rules, architecture/protected behavior, data-truth, changelog, learning)
- Durable intent: `docs/project/goal/goal.md`. Project docs provide the maintained governing record for material future-decision knowledge and tracked closure records after owner promotion.
- Material knowledge, uncertain observations, attributed agent decisions, and prompt-originated records resolve through `docs/agents/governance/documentation/documentation.md` Admission to their declared owners; actual source-owned values remain with those sources.

## Repo-owned agent assets

- Canonical reusable platform assets live under `docs/agents/`.
- Current repo-owned asset classes:
  - Skills: `docs/agents/governance/skills/`
  - Settings: `docs/agents/governance/settings/`
  - MCP configs: `docs/agents/governance/mcp/`
- Runtime installation is consumer-owned; this repo does not track root runtime copies or projection mappings.

## Tool loaders and root owner

- `AGENTS.md` (constitutional owner in this source repository; loader stub in a consuming repository)
- `Orchestration.md` (loading/application and lifecycle owner reached through the AGENTS foundation declaration)
- `CLAUDE.md` (required Claude Code loader stub)

## Supporting docs

- Index: `docs/agents/agents_index.md`
- Docs root index: `docs/docs_index.md`
- Authority decisions: `docs/agents/governance/ssot/authority-decisions/authority-decisions.md`

## Repo structure

```text
.
|- AGENTS.md
|- CLAUDE.md
|- Orchestration.md
|- agents-manifest.yaml
|- docs/
|  |- docs_index.md
|  |- agents/
|  |  |- agents_index.md
|  |  |- governance/     task jurisdictions: principles, evidence, bugfix, discovery, ssot (with the authority-decisions and hand-offs sub-docs), coding, documentation, testing, security, release, prompt-authoring, governance-learning, skills, settings, mcp, hooks, dependencies
|  |  |- interfaces/     touched external layers with baseline blocks: excel, pdf, filesystem, os-processes, gui-toolkit
|  |  |- playbooks/      design choices with baseline blocks: config, run-outcomes, io-batch, gui-guidelines, design-system, packaging
|  |- project/
|     |- project_index.md
|     |- goal/ rules/ architecture/ data-truth/ changelog/ learning/
|- scripts/
|  |- check_governance_core/
|  |  |- check_governance_core_main.py
|- X-Bookmarks Import/   non-owner workspace exception (SSOT-DEC-001)
```

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

Create these files in your project root so every coding assistant/tool lands on the same governance owners. Loader body routes to `.governance/AGENTS.md`, `.governance/Orchestration.md`, and `.governance/agents-manifest.yaml`; declaration paths resolve from the governance root.

Use this shared body for each loader:

```md
# <loader title>

@.governance/AGENTS.md
@.governance/Orchestration.md

Required loader:
- The two imports above load `.governance/AGENTS.md` and `.governance/Orchestration.md` at launch; follow the Mandatory Foundations declaration in `.governance/AGENTS.md` through `.governance/Orchestration.md`.
- If `.governance/` is missing or empty in a fresh clone, run `git submodule update --init --recursive`.
- Required-source loading, application, missing-source handling, and parent accountability follow that lifecycle owner.
- Follow `.governance/Orchestration.md` for all role, plan, council, execution, review, correction, and terminal mechanics.
- Project-specific docs remain under `docs/project/`.
```

Loader titles:
- `AGENTS.md` (required): `# AGENTS.md (Loader Stub)`
- `CLAUDE.md` (required for Claude Code): `# CLAUDE.md (Loader Stub)`

**Note**:
- Keep your project docs under `docs/project/` (do not copy `docs/agents` into the project root).
- The `@` lines are Claude Code imports (plain text for other tools); without them Claude Code does not read `AGENTS.md` when a `CLAUDE.md` exists.

### Step 3: Commit

The following Git commands are setup examples. Execute repository mutations only within the authorization resolved through `AGENTS.md` FP-30 and `Orchestration.md`; examples do not authorize staging, commits, remote operations, or discarding existing work.

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
git checkout -b codex/my-change
# ... make edits ...
git add .
git commit -m "My change"
git push origin codex/my-change

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
Resolve the installed Python 3 executable before running checks. Commands below use `python3`; use `python` when that is the verified executable name. This is command normalization before execution, not retrying a failed check through another runtime.

Run checks with `-B` and process-local `PYTHONDONTWRITEBYTECODE=1` so child Python processes also preserve existing bytecode. In PowerShell, wrap the selected commands below in this environment scope:

```powershell
$previousBytecodeSetting = [Environment]::GetEnvironmentVariable('PYTHONDONTWRITEBYTECODE', 'Process')
try {
  $env:PYTHONDONTWRITEBYTECODE = '1'
  # Run the selected verification commands below.
} finally {
  [Environment]::SetEnvironmentVariable('PYTHONDONTWRITEBYTECODE', $previousBytecodeSetting, 'Process')
}
```

This repo:
- Docs SSOT checks (all repository Markdown line counts; scoped docs headers/routers): `python3 -B scripts/check_governance_core/check_governance_core_main.py --only-docs-ssot --repo-root . --governance-root .` (use `python` if `python3` is unavailable)
  - Docs-policy regression tests: `python3 -B -m unittest scripts.check_governance_core.test_docs_policy -v`
- Project docs checks (required files + README linkage): `python3 -B scripts/check_governance_core/check_governance_core_main.py --only-project-docs --repo-root . --governance-root .` (use `python` if `python3` is unavailable)
- Cross-platform governance checks (manifest, docs, project docs, repository hygiene/structure, and Python safety): `python3 -B scripts/check_governance_core/check_governance_core_main.py` (use `python` if `python3` is unavailable)
  - Coding-policy regression tests: `python3 -B -m unittest scripts.check_governance_core.test_coding_policy -v`
  - Core governance regression tests: `python3 -B -m unittest discover -s scripts/check_governance_core -p "test*.py" -v` (use `python -B -m unittest discover -s ...` if `python3` is unavailable)
  - Strict safety mode: `python3 -B scripts/check_governance_core/check_governance_core_main.py --fail-on-safety-warnings`
  - Docs handler profiling: `python3 -B -m cProfile -s cumulative scripts/check_governance_core/check_governance_core_main.py --only-docs-ssot --repo-root . --governance-root .` (profiling overhead is separate from runtime timing).

Target repo (submodule under `.governance/`):
- Docs SSOT header checks: `python3 -B .governance/scripts/check_governance_core/check_governance_core_main.py --repo-root . --only-docs-ssot` (use `python` if `python3` is unavailable)
- Project docs checks: `python3 -B .governance/scripts/check_governance_core/check_governance_core_main.py --repo-root . --only-project-docs` (use `python` if `python3` is unavailable)
- Cross-platform governance checks: `python3 -B .governance/scripts/check_governance_core/check_governance_core_main.py --repo-root .` (use `python` if `python3` is unavailable)
  - Strict safety mode: `python3 -B .governance/scripts/check_governance_core/check_governance_core_main.py --repo-root . --fail-on-safety-warnings`

When a repository `SKILL.md` changes, resolve the installed `skill-creator` bundle and run its format validator: `python3 -B "<resolved-skill-creator>/scripts/quick_validate.py" "<changed-skill-folder>"`. The paths are explicit workflow inputs, not repository defaults. Validate each changed bundle; a format pass does not replace owner/semantic review. This check requires the skill-authoring tool only and does not execute the skill's operational workflow.

## Governance-core programmatic API

`scripts.check_governance_core.check_governance_core_main` is the only supported programmatic boundary. `run_checks(request)` accepts optional `repo_root`, `governance_root`, `mode` (`full`, `docs`, or `project_docs`), and `fail_on_safety_warnings`; it returns a plain mapping with `api_version`, terminal `status`, ordered per-check records, reconciled `planned`/`eligible`/`executed`/`skipped`/`failed` check IDs, `errors`, and `warnings`. `resolve_documents(request)` accepts explicit contained, non-aliased roots and returns `AGENTS.md`, then `Orchestration.md`, then the deterministic depth-first terminal Markdown leaves reachable from `docs/agents/agents_index.md`; `agents-manifest.yaml` routes Governance Agent research and does not define the document corpus. Invalid, escaped, aliased, missing, cyclic, or duplicate topology fails explicitly with an empty document list, so consumers do not maintain shadow file lists.

The API reads repository/governance files through one cached bounded filesystem inventory and uses bounded `git ls-files -z` only for owner-declared tracked-state rules. Git stdout and stderr are captured incrementally in bounded memory with a deadline and bounded cleanup; subprocess, capture, or cleanup failures produce explicit failed outcomes. Relevant readable file families revalidate regular-file type, canonical contained identity, aliases and current size before reads, including warm family lookups. Cached source changes fail explicitly. Byte limits use the same authoritative metadata only across the readable family; cached text/path resolution remains per-run. Full mode composes all registered governance, docs, repository-structure, and Python-safety checks; docs mode inventories all repository Markdown for the owner-declared line limit while headers/routers stay scoped to `docs/`; project-doc mode retains its narrower project-doc scope. Neither narrow mode reads unrelated Python content. Strict mode promotes safety warnings to failures. Generic `Popen` use remains a warning; Python safety keeps one explicit inventory-owner exception whose lifecycle is verified directly by failure-path tests. The API creates no temporary files and does not edit repository-owned files. Invalid inputs return `FAILED_VALIDATION`; check failures return `FAILED`. Consumers must not import private modules. Add a cohesive private handler plus one registry entry to extend checks; new request fields, modes, check IDs, or output fields require an intentional public-contract change with regression coverage.
