# AGENTS.MD (Repo) — Canonical Governance Pack

This repository maintains a reusable, repo-agnostic instruction pack for autonomous coding agents.

## Canonical SSOT

- Canonical policy: `AGENTS.md`
- Context injection manifest: `agents-manifest.yaml`

## Changelog

- See `CHANGELOG.md`

## Tool loader stubs

- Cursor: `.cursorrules` (forces loading `AGENTS.md`)
- Claude Code: `CLAUDE.md` (forces loading `AGENTS.md`)
- GitHub Copilot: `.github/copilot-instructions.md` (forces loading `AGENTS.md`)

## Supporting docs (non-authoritative)

- Index: `docs/agents/index.md`
- Docs are supporting material only; facts and behavior must stay in code/SSOT (see `docs/agents/25-docs-ssot-policy.md`).

## Templates (reference implementations)

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
│  └─ agents/
│     ├─ index.md
│     ├─ 00-principles.md
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
│     ├─ 90-release-checklist.md
│     ├─ workflow-registry.md
│     └─ playbooks/
│        ├─ ai-coding-prompt-template.md
│        ├─ bugfix-template.md
│        ├─ excel-task-template.md
│        └─ gui-task-template.md
├─ scripts/
│  ├─ check_docs_ssot.ps1
│  └─ check_agents_manifest.ps1
└─ .editorconfig
```

## Use in other repos

Copy the governance pack into the root of another repo:
- `AGENTS.md`, `agents-manifest.yaml`, `.cursorrules`, `CLAUDE.md`, `.github/copilot-instructions.md`, `docs/agents/`, `scripts/`, `.editorconfig`

## Checks

- Docs SSOT header checks: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/check_docs_ssot.ps1`
- Agents manifest checks: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/check_agents_manifest.ps1`
- Python safety baseline checks: `python scripts/check_python_safety.py` (add `--fail-on-warnings` to enforce warnings)
