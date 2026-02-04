# AGENTS.MD (Repo) — Canonical Governance Pack

This repository maintains a reusable, repo-agnostic instruction pack for autonomous coding agents.

## Canonical SSOT

- Canonical policy: `AGENTS.md`
- Context injection manifest: `agents-manifest.yaml`

## Project docs (this repo)

- Entry point: `docs/project/index.md` (goal/rules/architecture/learning)

## Tool loader stubs

- Cursor: `.cursorrules` (forces loading `AGENTS.md`)
- Claude Code: `CLAUDE.md` (forces loading `AGENTS.md`)
- GitHub Copilot: `.github/copilot-instructions.md` (forces loading `AGENTS.md`)

## Supporting docs (non-authoritative)

- Index: `docs/agents/index.md`
- Docs are supporting material only; facts and behavior must stay in code/SSOT (see `docs/agents/25-docs-ssot-policy.md`).

## Templates (reference implementations)

- Automation loop (nightly review + implement): `templates/automation-loop/`
- Dual-entry GUI+CLI + scenario tests (SSOT): `templates/python-dual-entry/`
  - Reference implementation only: follow `AGENTS.md` discovery/adoption rules; copy patterns, not files.
  - Run one scenario: `cd templates/python-dual-entry; python -m myapp --cli --scenario tests/scenarios/scenario_001_happy_path.json --verify`
  - Run all scenarios: `cd templates/python-dual-entry; python -m unittest -v`

## Repo structure

```
.
├─ AGENTS.md
├─ agents-manifest.yaml
├─ CLAUDE.md
├─ .cursorrules
├─ .github/
│  └─ copilot-instructions.md
├─ docs/
│  ├─ project/
│  │  ├─ index.md
│  │  ├─ goal.md
│  │  ├─ rules.md
│  │  ├─ architecture.md
│  │  └─ learning.md
│  └─ agents/
│     ├─ index.md
│     ├─ 00-principles.md
│     ├─ 05-context-retrieval.md
│     ├─ 10-repo-discovery.md
│     ├─ 15-stuck-in-loop-generate-fresh-restart-prompt.md
│     ├─ 20-sources-of-truth-map.md
│     ├─ 25-docs-ssot-policy.md
│     ├─ 30-logging-errors.md
│     ├─ 40-config-constants.md
│     ├─ 50-excel-com-lifecycle.md
│     ├─ 60-gui-threading.md
│     ├─ 70-io-data-integrity.md
│     ├─ 80-testing-real-files.md
│     ├─ 85-dual-entry-template.md
│     ├─ 90-release-checklist.md
│     ├─ workflow-registry.md
│     ├─ skills/
│     │  ├─ 00-skill-standards.md
│     │  └─ 10-platform-adapters.md
│     └─ playbooks/
│        ├─ ai-coding-prompt-template.md
│        ├─ bugfix-template.md
│        ├─ excel-task-template.md
│        ├─ governance-learnings-template.md
│        ├─ gui-task-template.md
│        ├─ io-batch-task-template.md
│        ├─ pdf-task-template.md
│        ├─ perf-hotspots-template.md
│        └─ project-docs-template.md
├─ scripts/
│  ├─ _governance_paths.ps1
│  ├─ check_docs_ssot.ps1
│  ├─ check_agents_manifest.ps1
│  ├─ check_project_docs.ps1
│  ├─ check_repo_hygiene.ps1
│  ├─ check_python_safety.py
│  └─ sync-governance.ps1
└─ .editorconfig
```

## Use in other repos (submodule)

> **IMPORTANT**: Git does NOT auto-pull submodules by default!
> 
> When cloning a repo that uses this pack, you MUST use `--recurse-submodules`:
> ```powershell
> git clone --recurse-submodules <repo-url>
> ```
> Otherwise `.governance/` will be empty. See "Cloning a repo that uses this pack" below.

### Step 1: Add the governance pack as a submodule

```powershell
cd "C:\path\to\your\project"
git submodule add -b main https://github.com/parmartejass/AGENTS.MD.git .governance
```

### Step 2: Create stub files at project root

Create these files at your project root, each pointing to `.governance/`:

**AGENTS.md** (required):
```md
# AGENTS.md

Before any work, read and follow `.governance/AGENTS.md`.
Manifest: `.governance/agents-manifest.yaml`.
```

**CLAUDE.md** (optional, for Claude):
```md
# CLAUDE.md

Before any work, read and follow `.governance/AGENTS.md`.
```

**Note**: Keep your project docs under `docs/project/` (do not copy `docs/agents` into the project root).

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

Changes to `.governance/` must be committed to the **submodule repo (AGENTS.MD)**, not the parent.

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

> **WARNING**: Do NOT commit `.governance/` changes from the parent repo directory.
> The parent only tracks a pointer (SHA) to a commit—it cannot store file changes.

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

> **Note**: If `.governance/` folder is empty, run `git submodule update --init`

### Troubleshooting

| Problem | Solution |
|---------|----------|
| `.governance/` is empty | `git submodule update --init` |
| Submodule shows "modified" but you didn't change it | `git submodule update --force .governance` |
| Accidentally edited from parent repo | Go into `.governance/`, commit there, push, then update parent |
| Changes not appearing after update | `git submodule update --remote .governance` |
| Detached HEAD in submodule | From inside `.governance/`: `git checkout main`, then `git pull origin main` |

## Checks

This repo:
- Docs SSOT header checks (all `docs/` except index pages): `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/check_docs_ssot.ps1`
- Agents manifest checks: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/check_agents_manifest.ps1`
- Project docs checks (required files + README linkage): `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/check_project_docs.ps1`
- Repo hygiene checks (no generated artifacts tracked): `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/check_repo_hygiene.ps1`
- Python safety baseline checks: `python scripts/check_python_safety.py` (add `--fail-on-warnings` to enforce warnings)

Target repo (submodule under `.governance/`):
- Docs SSOT header checks: `powershell -NoProfile -ExecutionPolicy Bypass -File .governance/scripts/check_docs_ssot.ps1 -RepoRoot .`
- Agents manifest checks: `powershell -NoProfile -ExecutionPolicy Bypass -File .governance/scripts/check_agents_manifest.ps1`
- Project docs checks: `powershell -NoProfile -ExecutionPolicy Bypass -File .governance/scripts/check_project_docs.ps1 -RepoRoot .`
- Repo hygiene checks: `powershell -NoProfile -ExecutionPolicy Bypass -File .governance/scripts/check_repo_hygiene.ps1 -RepoRoot .`
- Python safety baseline checks: `python .governance/scripts/check_python_safety.py --root .` (add `--fail-on-warnings` to enforce warnings)
