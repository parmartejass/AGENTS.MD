---
doc_type: reference
ssot_owner: docs/project/learning/changelog.md
update_trigger: durable project authority records are added, superseded, or retired
---

# Changelog

## Entries

### CH-20260531-004 - PR comment fixes for current-work and runtime projection setup
- Date: 2026-05-31
- Status: accepted
- Change type: current-work/runtime-projection
- Changed owners/files: `README.md`, `docs/agents/20-sources-of-truth-map/sources-of-truth-map.md`, `docs/agents/22-ssot-authority-decisions/ssot-authority-decisions.md`, `docs/agents/25-docs-ssot-policy/docs-ssot-policy.md`, `docs/agents/link_repo_assets.ps1`, `docs/agents/playbooks/project-docs-template/project-docs-template.md`, `docs/agents/settings/link_settings.ps1`, `docs/project/architecture/architecture.md`, `docs/project/goal/current-work.md`, `docs/project/goal/goal.md`, `docs/project/learning/changelog.md`, `scripts/check_governance_core/_current_work_authority.py`, `scripts/check_governance_core/test_project_current_work_pr_comments.py`, `scripts/check_governance_core/test_runtime_projection_setup_edges.py`, `scripts/check_governance_core/test_wrappers.py`, `scripts/setup_repo_platform_assets.ps1`
- Current work: `CW-20260531-007`
- Context: PR `#43` received review comments on current-work validation, plus merged local review findings for ready-to-clear handoff semantics and runtime projection setup repair paths.
- Decision/change: Current-work validation now reads top-level metadata fields separately from fenced prompt text, scans every current-work section for no-active residue, and rejects `committed:<sha>` as a `ready-to-clear` handoff. The lower docs now route repeated active-work field inventories back to the docs policy owner and distinguish active committed state from ready-to-clear pushed/PR/no-push closure. Runtime projection setup now validates the manifest contract before writes, the setup wrapper forwards `-RepairPlainDirectoryStubs`, and the settings helper forwards `-PythonExe`.
- Consequences/tradeoffs: Greptile's suggestion to ignore untracked files was not adopted because the current owner contract requires the tracked artifact witness to match actual `git status --short` cleanliness. Setup performs more side-effect-free validation up front, so malformed manifests fail earlier instead of partially writing projections.
- Validation: `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/setup_repo_platform_assets.ps1 -Force -PythonExe /opt/homebrew/bin/python3.12`; `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/check_docs_ssot.ps1 -PythonExe /opt/homebrew/bin/python3.12`; `/opt/homebrew/bin/python3.12 scripts/check_docs_router_contract/check_docs_router_contract_main.py`; `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/check_agents_manifest.ps1`; `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/check_project_docs.ps1 -PythonExe /opt/homebrew/bin/python3.12`; `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/check_repo_hygiene.ps1 -PythonExe /opt/homebrew/bin/python3.12`; `/opt/homebrew/bin/python3.12 scripts/check_folder_architecture/check_folder_architecture_main.py`; `/opt/homebrew/bin/python3.12 -m unittest -v scripts/check_folder_architecture/test_main.py`; `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/check_change_records.ps1 -PythonExe /opt/homebrew/bin/python3.12`; `/opt/homebrew/bin/python3.12 scripts/check_governance_core/check_governance_core_main.py --fail-on-safety-warnings`; `/opt/homebrew/bin/python3.12 -m unittest discover -s scripts/check_governance_core -p "test*.py" -v`; `/opt/homebrew/bin/python3.12 scripts/check_python_safety/check_python_safety_main.py --fail-on-warnings`; `cd templates/python-dual-entry && /opt/homebrew/bin/python3.12 -m unittest -v tests.test_logging_contract`; `git diff --check`.
- Evidence/version: `docs/project/goal/current-work.md` work item `CW-20260531-007`; PR `#43` head `c515373c83d743bda98a917293340706429438b4` before these fixes.
- Commit/push state: PR:https://github.com/parmartejass/AGENTS.MD/pull/43
- Supersedes: N/A
- Superseded by: N/A
- Follow-up required: None for the accepted PR comments after this change is pushed to PR `#43`.

### CH-20260531-003 - Current-work authority owns source-derived plan and closure
- Date: 2026-05-31
- Status: accepted
- Change type: current-work
- Changed owners/files: `.claude/settings.json`, `.claude/skills/x-api-data-access`, `.codex/config.toml`, `.cursor/cli.json`, `.cursor/mcp.json`, `.gitignore`, `AGENTS.md`, `README.md`, `docs/agents/20-sources-of-truth-map/sources-of-truth-map.md`, `docs/agents/22-ssot-authority-decisions/ssot-authority-decisions.md`, `docs/agents/25-docs-ssot-policy/docs-ssot-policy.md`, `docs/agents/link_repo_assets.ps1`, `docs/agents/playbooks/project-docs-template/project-docs-template.md`, `docs/project/architecture/architecture.md`, `docs/project/goal/goal.md`, `docs/project/goal/current-work.md`, `docs/project/learning/changelog.md`, `scripts/setup_repo_platform_assets.ps1`, `scripts/check_governance_core/_current_work_authority.py`, `scripts/check_governance_core/_project_authority_docs.py`, `scripts/check_governance_core/test_project_current_work.py`, `scripts/check_governance_core/test_project_current_work_ready.py`, `scripts/check_governance_core/test_project_current_work_closure.py`, `scripts/check_governance_core/test_project_current_work_security.py`, `scripts/check_governance_core/test_wrappers.py`, `templates/python-dual-entry/docs/project/goal/current-work.md`, `templates/python-dual-entry/docs/project/goal/goal.md`
- Current work: `CW-20260531-004`
- Context: The user clarified that docs-first authority must preserve the prompt, full intent, source-derived plan, implementation facts, review facts, and final change declaration so agents can continue through review, planning, and implementation without hallucinating missing goals or boundaries.
- Decision/change: Kept the canonical path `docs/project/goal/current-work.md` and clarified its title as `Current Work Authority`; made it the single active-work authority for prompt safety, prompt equality witness, derived work-item goal, source-derived plan, implementation records, stale/rejected prompt and plan reconciliation, review evidence, truth-layer witnesses, closure handoff, and next safe action. Added validator coverage for active plan shape, prompt-safety evidence, ready-to-clear plan closure, changelog/current-work linkage, clean git-status witness, common token-prefix prompt leaks, and no-active-work residue. Repaired runtime projection drift by converting tracked/shared runtime targets back to declared links and aligning setup TOML validation with the shared Python 3.11+ resolver.
- Consequences/tradeoffs: No separate `plan.md` or `.cursor/plans` authority was created, reducing path churn and duplicate ownership. Exact prompt equality remains a manual or harness witness when no expected prompt artifact/hash is supplied, but `current-work.md` must now record that witness explicitly.
- Validation: README Checks passed with `/opt/homebrew/bin/python3.12` and setup `-PythonExe /opt/homebrew/bin/python3.12`: platform asset setup smoke, project docs, docs SSOT, agents manifest, docs router contract, governance core strict mode, governance-core unit discovery, folder architecture, folder architecture unit tests, change records, Python safety strict mode, template logging contract, and `git diff --check`.
- Evidence/version: `docs/project/goal/current-work.md` work item `CW-20260531-004`
- Commit/push state: pushed:origin/codex/docs-first-authority
- Supersedes: `CH-20260531-001`, `CH-20260531-002`
- Superseded by: N/A
- Follow-up required: None for `CW-20260531-004`; active work was cleared after the implementation commit was pushed.

### CH-20260531-002 - Prompt-first current-work gate before planning and review
- Date: 2026-05-31
- Status: accepted
- Change type: current-work
- Changed owners/files: `AGENTS.md`, `docs/agents/25-docs-ssot-policy/docs-ssot-policy.md`, `docs/agents/playbooks/ai-coding-prompt-template/ai-coding-prompt-template.md`, `docs/agents/playbooks/governance-learnings-template/governance-learnings-template.md`, `docs/agents/15-stuck-in-loop-generate-fresh-restart-prompt/stuck-in-loop-generate-fresh-restart-prompt.md`, `scripts/check_governance_core/_project_authority_docs.py`, `scripts/check_governance_core/_project_authority_records.py`, `scripts/check_governance_core/test_project_current_work.py`, `scripts/check_governance_core/test_project_current_work_ready.py`, `scripts/check_governance_core/test_governance_learning_playbook.py`
- Current work: `CW-20260531-003`
- Context: Review of the user-provided Codex sessions showed the prior lifecycle contract preserved active prompt/goal evidence before implementation or mutation, but allowed non-trivial plans, reviews, and council outputs to become the first place intent was interpreted.
- Decision/change: The current-work session gate now runs after loader/context injection and before any non-trivial plan, review, council prompt or summary, implementation, or repo mutation. The docs policy and reusable prompt scaffolds route future work through that gate, and validators now reject placeholder active prompt/goal witnesses plus generic `ready-to-clear` evidence.
- Consequences/tradeoffs: Exact prompt equality remains a review or harness witness unless a tool supplies an expected prompt artifact or hash; secret, PII, customer-data, or oversized prompt content still requires a redacted substitute before writing tracked docs.
- Validation: `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/check_docs_ssot.ps1 -PythonExe /opt/homebrew/bin/python3.12`; `/opt/homebrew/bin/python3.12 scripts/check_docs_router_contract/check_docs_router_contract_main.py`; `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/check_agents_manifest.ps1`; `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/check_project_docs.ps1 -PythonExe /opt/homebrew/bin/python3.12`; `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/check_repo_hygiene.ps1 -PythonExe /opt/homebrew/bin/python3.12`; `/opt/homebrew/bin/python3.12 scripts/check_folder_architecture/check_folder_architecture_main.py`; `/opt/homebrew/bin/python3.12 -m unittest -v scripts/check_folder_architecture/test_main.py`; `/opt/homebrew/bin/python3.12 scripts/check_governance_core/check_governance_core_main.py --fail-on-safety-warnings`; `/opt/homebrew/bin/python3.12 -m unittest discover -s scripts/check_governance_core -p "test*.py" -v`; `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/check_change_records.ps1 -PythonExe /opt/homebrew/bin/python3.12`; `/opt/homebrew/bin/python3.12 scripts/check_python_safety/check_python_safety_main.py --fail-on-warnings`; `git diff --check`.
- Evidence/version: `docs/project/goal/current-work.md` work item `CW-20260531-003`
- Commit/push state: not-required + reason: historical entry predates the explicit closure-handoff contract
- Supersedes: N/A
- Superseded by: N/A
- Follow-up required: Reset `docs/project/goal/current-work.md` to `Status: no-active-work` only after the user-visible closure is complete and this changelog entry plus owner docs preserve the durable outcome.

### CH-20260531-001 - Mandatory current-work and session lifecycle contract
- Date: 2026-05-31
- Status: accepted
- Change type: current-work
- Changed owners/files: `AGENTS.md`, `docs/agents/25-docs-ssot-policy/docs-ssot-policy.md`, `docs/agents/20-sources-of-truth-map/sources-of-truth-map.md`, `docs/agents/22-ssot-authority-decisions/ssot-authority-decisions.md`, `docs/agents/playbooks/project-docs-template/project-docs-template.md`, `docs/project/goal/goal.md`, `docs/project/goal/current-work.md`, `scripts/check_governance_core/_project_authority_docs.py`
- Current work: `CW-20260531-002`
- Context: `docs/project/goal/current-work.md` is now mandatory and the user requested a docs-first session lifecycle where the exact prompt and work goal are recorded before work and closure requires SSOT-layer plus review fulfillment witnesses.
- Decision/change: Current work records now require bounded prompt/goal witnesses for active work, Runtime/Semantic/Recorded truth witnesses, review confirmation, status-aware reset semantics, and validator coverage for missing or incomplete current-work records.
- Consequences/tradeoffs: Exact prompt storage is allowed only as bounded active-work input evidence and must stop before writing if the prompt contains secrets, credentials, PII, customer data, or oversized pasted artifacts.
- Validation: Project-doc checks, docs SSOT checks, governance-core checks, and governance-core unit tests passed with `/opt/homebrew/bin/python3.12`.
- Evidence/version: `docs/project/goal/current-work.md` work item `CW-20260531-002`
- Commit/push state: not-required + reason: historical entry predates the explicit closure-handoff contract
- Supersedes: N/A
- Superseded by: N/A
- Follow-up required: Reset `docs/project/goal/current-work.md` to `Status: no-active-work` after the user-visible closure is complete and durable outcomes remain in owner docs.
