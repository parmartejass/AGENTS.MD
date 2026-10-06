# AGENTS.MD (Repo) - Canonical Governance Pack

This repository maintains a reusable, repo-agnostic governance pack for autonomous coding agents.

## Canonical SSOT

- Fundamental Principles, constitutional policy, and conflict precedence: `AGENTS.md`
- Agent roles and finite workflow: `Orchestration.md`
- Governance Agent authority-routing manifest: `agents-manifest.yaml`
- Cross-project authority decisions: `docs/agents/governance/ssot/authority-decisions/authority-decisions.md`
- Governance-core public API, docs router contract, repository structure, and Python-safety checks: the `scripts/check_governance_core/` package (public members in `__init__.py`, command-line launcher `__main__.py`)

## Read Order (Top-Down)

Start with `AGENTS.md` Mandatory Foundations and follow `Orchestration.md` for loading, application, source boundaries, and additional Governance Agent routing. When vendored as `.governance/` in a target repo, use `.governance/AGENTS.md`, `.governance/Orchestration.md`, and `.governance/agents-manifest.yaml`.

## Project docs (this repo)

- Entry point: `docs/project/project_index.md` (goal, rules, architecture, data-truth, changelog, learning); durable intent: `docs/project/goal/goal.md`.
- Material knowledge, uncertain observations, attributed agent decisions, and prompt-originated records resolve through `docs/agents/governance/documentation/documentation.md` Admission to their declared owners.

## Repo-owned agent assets

- Skills: `docs/agents/governance/skills/`; settings: `docs/agents/governance/settings/`; MCP configs: `docs/agents/governance/mcp/`.

## Tool loaders and root owner

- `AGENTS.md` (constitutional owner in this source repository; loader stub in a consuming repository)
- `Orchestration.md` (loading/application and lifecycle owner reached through the AGENTS foundation declaration)
- `CLAUDE.md` (required Claude Code loader stub)

## Supporting docs

- Index: `docs/agents/agents_index.md`; docs root index: `docs/docs_index.md`

## Repo structure

```text
.
|- AGENTS.md
|- CLAUDE.md
|- Orchestration.md
|- agents-manifest.yaml
|- docs/
|  |- docs_index.md
|  |- agents/            agents_index.md plus the governance/, interfaces/, playbooks/ layers
|  |- project/           project_index.md plus goal/ rules/ architecture/ data-truth/ changelog/ learning/
|- scripts/              declared Python source root: contains packages only
|  |- check_governance_core/   __init__.py public API (`__all__`), __main__.py launcher
|- X-Bookmarks Import/   non-owner workspace exception (SSOT-DEC-001)
```

## Use in other repos (submodule)

Add the pack, then create loader stubs at the project root so every coding assistant lands on the same owners:

```powershell
git submodule add -b main https://github.com/parmartejass/AGENTS.MD.git .governance
```

Loader body for both `AGENTS.md` (required) and `CLAUDE.md` (required for Claude Code; the `@` lines are Claude Code imports and plain text for other tools):

```md
# <loader title>

@.governance/AGENTS.md
@.governance/Orchestration.md

If `.governance/` is missing or empty, run `git submodule update --init --recursive`.
```

Governance-root declarations resolve inside `.governance/`; project docs stay under `docs/project/` at the project root (do not copy `docs/agents` there). Edits to `.governance/` are committed in the pack repo (`AGENTS.md` Submodule Workflow Rules); the parent then updates only the pointer:

```powershell
git -C .governance pull --ff-only origin main   # update the pack
git add .governance; git commit -m "Update governance pack"  # commit the pointer
git clone --recurse-submodules <repo-url>       # clone with the pack
git submodule update --init --recursive         # initialize after a plain clone
```

Setup commands are examples; repository mutations stay within the authorization resolved through `AGENTS.md` and `Orchestration.md`.

## Checks

Python 3.11+. Commands use `python3`; use `python` when that is the verified executable name (command normalization, not a retry through another runtime). Run with `-B` and process-local `PYTHONDONTWRITEBYTECODE=1` so child Python processes preserve existing bytecode.

This repo (run from the repository root, which is the governance root and the package import root):
- Docs SSOT checks (all repository Markdown line counts; scoped docs headers/routers): `python3 -B -m scripts.check_governance_core --only-docs-ssot --repo-root . --governance-root .`
  - Docs-policy regression tests: `python3 -B -m unittest scripts.check_governance_core.test_docs_policy -v`
  - Docs-policy timing witness: `python3 -B -m unittest scripts.check_governance_core.test_docs_timing -v`
- Project docs checks (required files + README linkage): `python3 -B -m scripts.check_governance_core --only-project-docs --repo-root . --governance-root .`
- Cross-platform governance checks (manifest, docs, project docs, repository hygiene/structure, folder architecture, and Python safety): `python3 -B -m scripts.check_governance_core`
  - Coding-policy regression tests: `python3 -B -m unittest scripts.check_governance_core.test_coding_policy -v`
  - Folder-architecture regression tests: `python3 -B -m unittest scripts.check_governance_core.test_folder_architecture -v`
  - Launcher and README-reference regression tests: `python3 -B -m unittest scripts.check_governance_core.test_main -v`
  - Core governance regression tests: `python3 -B -m unittest discover -s scripts/check_governance_core -p "test*.py" -v`
  - Strict safety mode: `python3 -B -m scripts.check_governance_core --fail-on-safety-warnings`
  - Docs handler profiling: `python3 -B -m cProfile -s cumulative -m scripts.check_governance_core --only-docs-ssot --repo-root . --governance-root .` (profiling overhead is separate from runtime timing).
- X workspace regression tests (non-owner workspace, `SSOT-DEC-001`): `python3 -B -m unittest discover -s "X-Bookmarks Import/skills/governance-autoresearch/scripts" -p "test*.py" -v` and `python3 -B -m unittest discover -s "X-Bookmarks Import/skills/x-research/scripts" -p "test*.py" -v`

Target repo (submodule under `.governance/`; run from the `.governance/` directory so the governance root is the package import root):
- Docs SSOT header checks: `python3 -B -m scripts.check_governance_core --repo-root .. --only-docs-ssot`
- Project docs checks: `python3 -B -m scripts.check_governance_core --repo-root .. --only-project-docs`
- Cross-platform governance checks: `python3 -B -m scripts.check_governance_core --repo-root ..`
  - Strict safety mode: `python3 -B -m scripts.check_governance_core --repo-root .. --fail-on-safety-warnings`
- Packaged-folder enforcement reads the pack's root markers from `.governance/docs/project/architecture/architecture.md` and the target repo's own roots and exceptions from its `docs/project/architecture/architecture.md` (none when the target keeps no Python outside `.governance/`); the enforced and unclaimed witnesses are recorded in the pack's architecture record, Modularity witness boundary.

When a repository `SKILL.md` changes, resolve the installed `skill-creator` bundle and run its format validator: `python3 -B "<resolved-skill-creator>/scripts/quick_validate.py" "<changed-skill-folder>"`; the paths are explicit workflow inputs, a format pass is not owner/semantic review, and the skill's operational workflow is not executed.

## Governance-core programmatic API

`scripts.check_governance_core` is the only supported programmatic boundary (`__all__`: `run_checks`, `resolve_documents`, `main`; private modules are not consumer contracts). `run_checks(request)` accepts optional `repo_root`, `governance_root`, `mode` (`full`, `docs`, `project_docs`), and `fail_on_safety_warnings`; it returns a plain mapping with `api_version`, terminal `status` (`PASSED`, `FAILED`, or `FAILED_VALIDATION` for invalid input), ordered per-check records, reconciled `planned`/`eligible`/`executed`/`skipped`/`failed` check IDs, `errors`, and `warnings`. `resolve_documents(request)` accepts explicit contained, non-aliased roots and returns `AGENTS.md`, `Orchestration.md`, then the deterministic depth-first terminal Markdown leaves reachable from `docs/agents/agents_index.md`; invalid, escaped, aliased, missing, cyclic, or duplicate topology fails explicitly with an empty document list. The API is read-only, creates no temporary files, reads through one cached bounded inventory, and uses bounded `git ls-files -z` only for tracked-state rules; new request fields, modes, check IDs, or output fields are an intentional public-contract change with regression coverage.
