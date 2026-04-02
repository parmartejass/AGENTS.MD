---
doc_type: runbook
ssot_owner: AGENTS.md
update_trigger: remediation scope, sequencing, or verification evidence changes
---

# Master To-Do

## Scope
- Track the staged remediation for the 2026-03-29 SSOT review.
- This doc owns execution status and sequencing only.
- Governance rules remain owned by `AGENTS.md`.
- Context-injection routing remains owned by `agents-manifest.yaml`.
- Platform/runtime facts remain owned by `docs/agents/platforms/runtime-projections.json` and `docs/agents/link_repo_assets.ps1`.

## Acceptance criteria
- One owner for Codex project config and MCP/runtime references.
- One effective checker rule set for council summaries, manifest checks, and project-doc checks.
- README "Checks" remains the single verification-command SSOT.
- Context injection and discovery guidance are internally consistent.
- Project and template docs reference owners instead of restating literals or check lists.

## Stages

### Stage 0 - Master to-do and evidence setup
- Status: completed
- Create and index this remediation tracker.
- Add a governance change record for the remediation work.

### Stage 1 - Platform/runtime authority fixes
- Status: completed
- Resolve `.codex/config.toml` ownership across:
  - `docs/agents/mcp/00-mcp-standards/mcp-standards.md`
  - `docs/agents/settings/00-settings-standards/settings-standards.md`
  - `docs/agents/platforms/runtime-projections.json`
  - `docs/agents/link_repo_assets.ps1`
  - `docs/project/platform-runtime-status/platform-runtime-status.md`
- Fix the `preserve_existing_when_disabled` behavior so enabled-mode linking matches fail-closed policy.
- If mixed-owner runtime paths remain allowed, record the decision in `docs/agents/22-ssot-authority-decisions/ssot-authority-decisions.md`.

### Stage 2 - Checker authority consolidation
- Status: completed
- Align `scripts/check_governance_core/main.py` with `scripts/check_change_records.ps1` for governance council-summary validation, including `intent_coverage`.
- Remove drift between Python and PowerShell enforcement for:
  - manifest rules
  - project-doc README-reference rules
- Preserve a single effective owner for each repeated requirement.

### Stage 3 - Injection and docs de-duplication
- Status: completed
- Reconcile `agents-manifest.yaml`, `AGENTS.md`, and `docs/agents/index.md` for discovery and bugfix routing.
- Replace parallel checks lists with references to `README.md` "Checks".
- Remove duplicated literals from:
  - `docs/project/rules/rules.md`
  - `templates/pr-control-plane/README.md`
  - `docs/agents/automation/nightly-compound-loop/nightly-compound-loop.md`

### Stage 4 - Verification and closure
- Status: completed
- Run the repo checks from `README.md` "Checks".
- Run a deterministic failure-path witness for the runtime-linker conflict path in a disposable setup.
- Finalize the change record with council summaries, findings, witnesses, and verification evidence.
- Release gate:
  - Cleared by `docs/project/change-records/2026-03-29-x-bookmarks-hold-remediation.json` after the strict safety baseline returned green.
- Completed witnesses:
  - Disposable `skills` projection runs now create POSIX-relative links such as `../../docs/agents/skills/x-api-data-access`.
  - Disposable `subagents` projection runs now reach the intended fail-closed `.cursor/agents` conflict path and stop with `Refusing to replace non-link path`.
- Deferred follow-up:
  - `docs/agents/link_repo_assets.ps1` still uses content equality as a hard-link proxy for files and should be tightened in a separate change.

### Stage 5 - Strict-safety hold remediation
- Status: completed
- Create a shared X-bookmarks runtime helper for env loading, HTTP error handling, logging/output routing, and atomic token writes.
- Rewire:
  - `X-Bookmarks Import/fetch_bookmarks.py`
  - `X-Bookmarks Import/skills/x-research/scripts/x_search.py`
  - `X-Bookmarks Import/skills/governance-autoresearch/scripts/governance_research.py`
- Fix linked high-risk failure paths:
  - OAuth callback state validation
  - explicit rate-limit/auth failure behavior
  - tokenless `--help` / `--list` modes where safe
  - controlled CLI integer parsing errors
- Verification outcome:
  - `python3 scripts/check_python_safety/main.py` now reports `0 error(s), 0 warning(s)`
  - `python3 scripts/check_governance_core/main.py --fail-on-safety-warnings` now passes

## Council checkpoints
- Use the `AGENTS.md` "Subagent Council (Hard Gate)" section as the governing procedure for each stage.
- Record the pre-change and post-change council summaries in the remediation change record before final closure.
