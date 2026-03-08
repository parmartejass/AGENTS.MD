# AGENTS.MD (Repo) - Canonical Governance Pack

This repository maintains a reusable, repo-agnostic governance pack for autonomous coding agents.

## Canonical SSOT

- Canonical policy: `AGENTS.md`
- Context injection manifest: `agents-manifest.yaml`

## Read Order (Top-Down)

1. `AGENTS.md` (authoritative rules and hard gates)
2. `agents-manifest.yaml` (context injection and profile routing)
3. `docs/agents/index.md` (supporting branch map and when-to-read guidance)
4. Task-specific supporting docs/playbooks under `docs/agents/`
5. Project docs entrypoint: `docs/project/index.md`

When vendored as `.governance/` in a target repo, use `.governance/AGENTS.md` and `.governance/agents-manifest.yaml`.

## Project docs (this repo)

- Entry point: `docs/project/index.md` (goal/rules/architecture/learning)
- Generated analyses: `docs/generated/` (non-authoritative, reproducible outputs)

## Repo-owned agent assets

- Canonical reusable platform assets live under `docs/agents/`.
- Current repo-owned asset classes:
  - Skills: `docs/agents/skills/`
  - Settings: `docs/agents/settings/`
  - Subagents: `docs/agents/subagents/`
  - MCP configs: `docs/agents/mcp/`
  - ACP placeholders: `docs/agents/acp/`
- Platform runtime policy lives in `docs/agents/platforms/00-platform-runtime-standards.md`.
- Concrete runtime path/support-level facts live in `docs/agents/platforms/runtime-projections.json`.
- Dated platform/runtime evidence lives in `docs/agents/platforms/index.md`.
- Integration notes for context/memory tools live in `docs/agents/integrations/index.md`.
- Runtime projection sources resolve from the governance root; runtime targets resolve from the project root (or `{HOME}` when explicitly declared).
- Use `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/setup_repo_platform_assets.ps1 -Force` to project supported assets into runtime locations for this repo.
- Default setup preserves an existing `.cursor/agents/` compatibility surface for this repo, but does not create `.cursor/rules/`.
- Use `-IncludeCompatibility` only when you explicitly want legacy or unverified compatibility projections.
- Conflicting user-owned runtime files such as a non-link `.mcp.json` can cause setup to stop with an explicit error until you rename or remove the conflicting path.
- When vendored as `.governance/`, the linker auto-targets the parent project root and also accepts `-RepoRoot` for an explicit override.
- If the repo moves to a new filesystem path, rerun `scripts/setup_repo_platform_assets.ps1 -Force` so projections and generated adapters are rebuilt.

## Nia in this repo

- Nia is already connected for this repo through the projected Codex skill at `.agents/skills/nia`; the canonical bundle remains under `docs/agents/skills/nia/`.
- For repository, documentation, package, and local-folder discovery tasks that match the Nia skill, use Nia before generic web fetch/search.
- Do not treat a missing process `NIA_API_KEY` as proof that Nia is unavailable; this repo may keep the key in `.env`, and direct API verification is valid when shell wrappers are unavailable.
- On Windows, Git Bash may exist outside `PATH`, and the bundled Nia shell scripts also require `jq`.

## Tool loader stubs

- Cursor: `.cursorrules` (forces loading `AGENTS.md`)
- Claude Code: `CLAUDE.md` (forces loading `AGENTS.md`)
- GitHub Copilot: `.github/copilot-instructions.md` (forces loading `AGENTS.md`)

## Supporting docs (non-authoritative)

- Index: `docs/agents/index.md`
- Docs are supporting material only; facts and behavior must stay in code/SSOT (see `docs/agents/25-docs-ssot-policy.md`).

## Templates (reference implementations)

- Automation loop (nightly review + implement): `templates/automation-loop/`
- PR control-plane loop (risk gate + review state + evidence + remediation): `templates/pr-control-plane/`
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
|- CLAUDE.md
|- .cursorrules
|- .github/
|  |- copilot-instructions.md
|- docs/
|  |- project/
|  |  |- index.md
|  |  |- goal.md
|  |  |- rules.md
|  |  |- architecture.md
|  |  |- learning.md
|  |- generated/
|  |- agents/
|  |  |- index.md
|  |  |- 00-principles.md
|  |  |- 05-context-retrieval.md
|  |  |- 10-repo-discovery.md
|  |  |- 15-stuck-in-loop-generate-fresh-restart-prompt.md
|  |  |- 20-sources-of-truth-map.md
|  |  |- 25-docs-ssot-policy.md
|  |  |- 30-logging-errors.md
|  |  |- 35-authority-bounded-modules.md
|  |  |- 40-config-constants.md
|  |  |- 50-excel-com-lifecycle.md
|  |  |- 60-gui-threading.md
|  |  |- 70-io-data-integrity.md
|  |  |- 80-testing-real-files.md
|  |  |- 85-dual-entry-template.md
|  |  |- 90-release-checklist.md
|  |  |- workflow-registry.md
|  |  |- automation/
|  |  |  |- overview.md
|  |  |  |- nightly-compound-loop.md
|  |  |- acp/
|  |  |  |- 00-acp-standards.md
|  |  |- link_repo_assets.ps1
|  |  |- mcp/
|  |  |  |- 00-mcp-standards.md
|  |  |  |- link_mcp.ps1
|  |  |  |- shared/
|  |  |     |- mcp.json
|  |  |- settings/
|  |  |  |- 00-settings-standards.md
|  |  |  |- link_settings.ps1
|  |  |  |- claude-code/
|  |  |  |  |- settings.json
|  |  |  |- codex/
|  |  |  |  |- config.toml
|  |  |  |- cursor/
|  |  |     |- cli.json
|  |  |- integrations/
|  |  |  |- index.md
|  |  |- skills/
|  |  |  |- 00-skill-standards.md
|  |  |  |- 10-platform-adapters.md
|  |  |  |- link_skills.ps1
|  |  |  |- platform-adapters/
|  |  |  |  |- Codex CLI/
|  |  |  |     |- llmjunky-last-30-days.md
|  |  |  |- x-api-data-access/
|  |  |     |- SKILL.md
|  |  |     |- references/
|  |  |- subagents/
|  |  |  |- 00-subagent-standards.md
|  |  |  |- link_subagents.ps1
|  |  |  |- shared/
|  |  |- platforms/
|  |  |  |- 00-platform-runtime-standards.md
|  |  |  |- index.md
|  |  |  |- runtime-projections.json
|  |  |- schemas/
|  |  |  |- change-record.schema.json
|  |  |- playbooks/
|  |     |- ai-coding-prompt-template.md
|  |     |- bugfix-template.md
|  |     |- design-principles-checklist.md
|  |     |- excel-task-template.md
|  |     |- governance-learnings-template.md
|  |     |- gui-task-template.md
|  |     |- io-batch-task-template.md
|  |     |- pdf-task-template.md
|  |     |- perf-hotspots-template.md
|  |     |- project-docs-template.md
|  |     |- rca-methods-template.md
|- scripts/
|  |- _governance_paths.ps1
|  |- check_docs_ssot.ps1
|  |- check_agents_manifest.ps1
|  |- check_project_docs.ps1
|  |- check_repo_hygiene.ps1
|  |- check_change_records.ps1
|  |- check_governance_core.py
|  |- check_python_safety.py
|  |- setup_repo_platform_assets.ps1
|  |- sync-governance.ps1
|- templates/
|  |- automation-loop/
|  |- python-dual-entry/
|- .editorconfig
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

Create these files in your project root so every coding assistant/tool lands on the same governance SSOT.

**AGENTS.md** (required):

```md
# AGENTS.md (Loader Stub)

Hard gate:
- Before doing any work, open and follow `.governance/AGENTS.md`.
- If `.governance/` is missing or empty in a fresh clone, run `git submodule update --init --recursive`.
- If you cannot access repository files, request that the user paste `.governance/AGENTS.md`.
- Do not implement changes unless `AGENTS.md` is in-context.

Context injection (REQUIRED):
- After reading `.governance/AGENTS.md`, follow its "Context Injection Procedure (Hard Gate)" section
  (consult `.governance/agents-manifest.yaml`, load injected docs/playbooks from
  `.governance/docs/agents/`, and use `fallback_inject` if no profile matches).

Governance SSOT:
- All governance docs live in `.governance/` submodule (AGENTS.md, agents-manifest.yaml, docs/agents/*)
- Project-specific docs live in `docs/project/`

If any conflict exists, `.governance/AGENTS.md` is authoritative.
```

**CLAUDE.md** (optional, for Claude Code):
```md
# CLAUDE.md (Loader Stub)

Hard gate:
- Before doing any work, open and follow `.governance/AGENTS.md`.
- If `.governance/` is missing or empty in a fresh clone, run `git submodule update --init --recursive`.
- If you cannot access repository files, request that the user paste `.governance/AGENTS.md`.
- Do not implement changes unless `AGENTS.md` is in-context.

Context injection (REQUIRED):
- After reading `.governance/AGENTS.md`, follow its "Context Injection Procedure (Hard Gate)" section
  (consult `.governance/agents-manifest.yaml`, load injected docs/playbooks from
  `.governance/docs/agents/`, and use `fallback_inject` if no profile matches).

Governance SSOT:
- All governance docs live in `.governance/` submodule (AGENTS.md, agents-manifest.yaml, docs/agents/*)
- Project-specific docs live in `docs/project/`

If any conflict exists, `.governance/AGENTS.md` is authoritative.
```

**.cursorrules** (optional, for Cursor):
```md
# .cursorrules (Loader Stub)

Hard gate:
- Before doing any work, open and follow `.governance/AGENTS.md`.
- If `.governance/` is missing or empty in a fresh clone, run `git submodule update --init --recursive`.
- If you cannot access repository files, request that the user paste `.governance/AGENTS.md`.
- Do not implement changes unless `AGENTS.md` is in-context.

Context injection (REQUIRED):
- After reading `.governance/AGENTS.md`, follow its "Context Injection Procedure (Hard Gate)" section
  (consult `.governance/agents-manifest.yaml`, load injected docs/playbooks from
  `.governance/docs/agents/`, and use `fallback_inject` if no profile matches).

Governance SSOT:
- All governance docs live in `.governance/` submodule (AGENTS.md, agents-manifest.yaml, docs/agents/*)
- Project-specific docs live in `docs/project/`

If any conflict exists, `.governance/AGENTS.md` is authoritative.
```

**.github/copilot-instructions.md** (optional, for GitHub Copilot):
```md
# copilot-instructions.md (Loader Stub)

Hard gate:
- Before doing any work, open and follow `.governance/AGENTS.md`.
- If `.governance/` is missing or empty in a fresh clone, run `git submodule update --init --recursive`.
- If you cannot access repository files, request that the user paste `.governance/AGENTS.md`.
- Do not implement changes unless `AGENTS.md` is in-context.

Context injection (REQUIRED):
- After reading `.governance/AGENTS.md`, follow its "Context Injection Procedure (Hard Gate)" section
  (consult `.governance/agents-manifest.yaml`, load injected docs/playbooks from
  `.governance/docs/agents/`, and use `fallback_inject` if no profile matches).

Governance SSOT:
- All governance docs live in `.governance/` submodule (AGENTS.md, agents-manifest.yaml, docs/agents/*)
- Project-specific docs live in `docs/project/`

If any conflict exists, `.governance/AGENTS.md` is authoritative.
```

**Note**:
- Create `.github/` first if your repo does not already have it.
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

This repo:
- Platform asset bootstrap/repair smoke (writes the repo-owned runtime projections): `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/setup_repo_platform_assets.ps1 -Force`
  - Default path witness: existing `.cursor/agents/` remains in place; `.cursor/rules/` is not created.
  - If setup stops on a conflicting non-link runtime file such as `.mcp.json`, rename or remove that path and rerun.
  - Include compatibility-only projections when explicitly needed: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/setup_repo_platform_assets.ps1 -Force -IncludeCompatibility`
- Docs SSOT header checks (all `docs/` except index pages): `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/check_docs_ssot.ps1`
- Agents manifest checks: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/check_agents_manifest.ps1`
- Project docs checks (required files + README linkage): `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/check_project_docs.ps1`
- Repo hygiene checks (no runtime/generated artifact noise tracked): `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/check_repo_hygiene.ps1`
- Cross-platform core governance checks (manifest + docs SSOT + project docs + hygiene + playbook parity + unresolved citation tokens + change records): `python3 scripts/check_governance_core.py` (use `python` if `python3` is unavailable)
  - Require change records (or honor `.required` marker): `python3 scripts/check_governance_core.py --require-records`
  - Strict safety mode: `python3 scripts/check_governance_core.py --fail-on-safety-warnings`
- Change record artifact checks (schema + required evidence fields): `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/check_change_records.ps1`
  - Enforce required records by creating `docs/project/change-records/.required` or running with `-RequireRecords`.
- Python safety baseline checks: `python3 scripts/check_python_safety.py` (add `--fail-on-warnings` to enforce warnings; use `python` if `python3` is unavailable)
- Template structured logging contract tests: `cd templates/python-dual-entry && python3 -m unittest -v tests.test_logging_contract` (use `python` if `python3` is unavailable)

Target repo (submodule under `.governance/`):
- Docs SSOT header checks: `powershell -NoProfile -ExecutionPolicy Bypass -File .governance/scripts/check_docs_ssot.ps1 -RepoRoot .`
- Agents manifest checks: `powershell -NoProfile -ExecutionPolicy Bypass -File .governance/scripts/check_agents_manifest.ps1`
- Project docs checks: `powershell -NoProfile -ExecutionPolicy Bypass -File .governance/scripts/check_project_docs.ps1 -RepoRoot .`
- Repo hygiene checks: `powershell -NoProfile -ExecutionPolicy Bypass -File .governance/scripts/check_repo_hygiene.ps1 -RepoRoot .`
- Cross-platform core governance checks: `python3 .governance/scripts/check_governance_core.py --repo-root .` (use `python` if `python3` is unavailable)
  - Require change records: `python3 .governance/scripts/check_governance_core.py --repo-root . --require-records`
  - Strict safety mode: `python3 .governance/scripts/check_governance_core.py --repo-root . --fail-on-safety-warnings`
- Change record artifact checks: `powershell -NoProfile -ExecutionPolicy Bypass -File .governance/scripts/check_change_records.ps1 -RepoRoot .`
  - Enforce required records by creating `docs/project/change-records/.required` or running with `-RequireRecords`.
- Python safety baseline checks: `python3 .governance/scripts/check_python_safety.py --root .` (add `--fail-on-warnings` to enforce warnings; use `python` if `python3` is unavailable)
