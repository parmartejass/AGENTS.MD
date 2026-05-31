---
doc_type: decision
ssot_owner: AGENTS.md
update_trigger: cross-project SSOT authority decisions change OR migration contracts are added or updated
---

# 22 - SSOT Authority Decisions

## Purpose
- Record governance-level authority decisions that apply across repos using this pack.
- Use this doc when `docs/agents/20-sources-of-truth-map/sources-of-truth-map.md` is too abstract and project docs are too local.
- Keep this doc limited to decision records and migration contracts. Do not restate policy already owned by `AGENTS.md`, `docs/agents/20-sources-of-truth-map/sources-of-truth-map.md`, or `docs/agents/25-docs-ssot-policy/docs-ssot-policy.md`.

## Scope
- Cross-project authority choices for reusable governance concepts.
- Allowed non-owner locations, forbidden duplicates, and coordinated migration or update sets.
- Explicit boundaries for mixed-domain areas where a single folder contains multiple asset classes.

## Out of Scope
- Project-local architecture choices; keep those in `docs/project/architecture/architecture.md`.
- Repeating repo-wide SSOT policy; keep that in `AGENTS.md`.
- Repeating concept -> owner routing; keep that in `docs/agents/20-sources-of-truth-map/sources-of-truth-map.md`.

## Entry Contract
Each active decision record must include:
- Decision ID
- Status
- Scope
- Canonical owner
- Allowed non-owner locations
- Forbidden duplicates
- Coordinated update set
- Verification witness
- Review trigger

## Guardrails
- Reusable governance assets must not use secret-bearing, generated-data, or machine-local roots as canonical SSOT parents.
- Mixed broader domains may contain non-owner workspace roots only when this registry records a canonical owner, the allowed non-owner paths, and the forbidden duplicates. This is hierarchical authority, not parallel authority.
- If a decision changes a canonical owner, update the coordinated set in one change. Do not migrate docs first and tooling later.

## Active Decisions

### SSOT-DEC-001 - Reusable X skill authority vs X workspace
- Status: active
- Scope: reusable X API skill guidance as the canonical authority, plus adjacent X research, data, and import workspace content as a separate non-owner workspace zone
- Canonical owner: `docs/agents/skills/x-api-data-access/`
- Allowed non-owner locations:
  - `X-Bookmarks Import/` may contain bookmark exports, research notes, import or fetch scripts, and local workspace-only experiments.
  - Workspace-local X skill experiments under `X-Bookmarks Import/` are not canonical repo-owned skills until they are migrated into `docs/agents/skills/<skill-name>/` and linked through the standard skill owners and tooling.
  - Secret-bearing files such as `.x_token.json` must remain untracked and must not define canonical guidance.
- Forbidden duplicates:
  - No tracked second `x-api-data-access/SKILL.md` outside `docs/agents/skills/x-api-data-access/`.
  - Do not point docs or runtime projection tooling at `X-Bookmarks Import/` as the canonical root for reusable skill bundles.
- Coordinated update set:
  - `docs/agents/skills/00-skill-standards/skill-standards.md`
  - `docs/agents/skills/10-platform-adapters/platform-adapters.md`
  - `docs/agents/agents_index.md`
  - `README.md`
  - `agents-manifest.yaml`
  - `scripts/check_governance_core/check_governance_core_main.py`
- Verification witness:
  - `python3 scripts/check_governance_core/check_governance_core_main.py` passes.
  - `docs/agents/agents_index.md` and `README.md` reference `docs/agents/skills/` as the canonical reusable skill root.
  - The tracked canonical X API skill bundle exists under `docs/agents/skills/x-api-data-access/`.
- Review trigger:
  - Any proposal to move canonical X skill ownership away from `docs/agents/skills/`.
  - Any proposal to treat `X-Bookmarks Import/` as a tracked governance asset root rather than a non-authority workspace.

### SSOT-DEC-002 - Runtime projection authority vs projected runtime targets
- Status: active
- Scope: repo-owned agent assets projected into project-local or explicitly declared user-home runtime paths
- Canonical owner:
  - Concrete runtime target mapping: `docs/agents/platforms/runtime-projections.json`
  - Canonical source asset roots: `docs/agents/skills/`, `docs/agents/settings/`, `docs/agents/mcp/`
- Allowed non-owner locations:
  - Runtime targets declared in `docs/agents/platforms/runtime-projections.json`, including project dotpaths such as `.agents/skills/`, `.codex/config.toml`, `.claude/settings.json`, `.cursor/mcp.json`, `.cursor/cli.json`, and `.mcp.json`
  - Explicit user-home targets declared in `docs/agents/platforms/runtime-projections.json`, such as `{HOME}/.agents/skills`
  - Generated or linked runtime projections created by `docs/agents/link_repo_assets.ps1` or `scripts/setup_repo_platform_assets.ps1`
  - Legacy local subagent runtime paths such as `.claude/agents/` and `.codex/agents/` may exist only as non-authoritative local/platform surfaces; they are not repo-owned projections and stale copies must be removed or managed outside this runtime-projection authority.
  - `.cursor/plans/` may contain tracked Cursor planning records for this governance source repo; it is not a runtime projection target, is not governed by `runtime-projections.json`, and is not an active-work plan authority unless selected facts are promoted into `docs/project/goal/current-work.md`.
- Retired scope:
  - ACP placeholders, automation runbooks, integration note branches, generated analyses, and PR-control-plane templates are retired in this cleanup and may appear in change records only with `retired:`.
  - Repo-owned subagent source docs and runtime adapters under `docs/agents/subagents/` are retired; canonical agent instructions remain in `AGENTS.md` and context routing remains in `agents-manifest.yaml`.
- Forbidden duplicates:
  - Do not treat projected runtime files or folders as canonical owners for platform settings, MCP definitions, or skills.
  - Do not restate concrete runtime mapping facts in `README.md` or `docs/project/platform-runtime-status/platform-runtime-status.md` as parallel authorities.
  - Do not create second canonical asset roots outside the `docs/agents/` source owners listed above.
- Coordinated update set:
  - `README.md`
  - `agents-manifest.yaml`
  - `docs/agents/agents_index.md`
  - `docs/agents/20-sources-of-truth-map/sources-of-truth-map.md`
  - `docs/agents/skills/00-skill-standards/skill-standards.md`
  - `docs/agents/platforms/runtime-projections.json`
  - `docs/agents/platforms/00-platform-runtime-standards/platform-runtime-standards.md`
  - `docs/agents/mcp/00-mcp-standards/mcp-standards.md`
  - `docs/agents/settings/00-settings-standards/settings-standards.md`
  - `docs/agents/settings/codex/config.toml`
  - `docs/agents/link_repo_assets.ps1`
  - `scripts/setup_repo_platform_assets.ps1`
  - `docs/project/platform-runtime-status/platform-runtime-status.md`
  - `docs/project/architecture/architecture.md`
  - `scripts/check_repo_hygiene.ps1`
  - `scripts/check_governance_core/check_governance_core_main.py`
- Verification witness:
  - `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/setup_repo_platform_assets.ps1 -Force` completes for supported defaults.
  - `docs/project/platform-runtime-status/platform-runtime-status.md` references runtime projections and source owners rather than restating concrete mapping facts as SSOT.
  - Projected runtime paths continue to resolve from the source owners declared in `docs/agents/platforms/runtime-projections.json`.
  - Retired `.claude/agents/` and `.codex/agents/` runtime paths are documented as local-only legacy surfaces, not canonical source roots or projection targets.
- Review trigger:
  - Any proposal to add or remove a projected runtime target.
  - Any proposal to move a runtime surface between project-local, user-home, compatibility, manual, or official support levels.
  - Any proposal to treat a projected runtime path as a canonical owner rather than a non-owner projection.

### SSOT-DEC-003 - Docs router authority vs canonical narrative leaf docs
- Status: active
- Scope: folder-owned public contract naming for runtime code and docs, with docs-specific router and public-leaf behavior under `docs/`
- Canonical owner:
  - Human-readable policy owner for docs-family behavior: `docs/agents/25-docs-ssot-policy/docs-ssot-policy.md`
  - Human-readable policy owner for runtime-code family behavior: `docs/agents/35-authority-bounded-modules/authority-bounded-modules.md`
  - Machine-readable filename registry for contract families: `scripts/entrypoint_contracts.json`
- Allowed non-owner locations:
  - Router-linked public leaf markdown docs inside the same docs folder authority
  - Router-only docs folders that are artifact-first and only catalog payload children such as JSON, TOML, generated outputs, or dated evidence subfolders
  - Deeper runtime identity contracts such as `SKILL.md` and `mcp.json`, which remain owned by their existing authorities and are out of scope for this naming contract
- Forbidden duplicates:
  - Do not reintroduce `index.md` as the universal docs router contract after the registry-backed cutover
  - Do not keep `scripts/migrated_router_leaves.json` or any replacement leaf-name registry once filename derivation is handled by `scripts/entrypoint_contracts.json`
  - Do not hardcode runtime or docs contract filenames independently in validators, README guidance, templates, or policy docs
  - Do not create competing public contract files inside one folder authority unless an explicit contract-family exception already owns them
- Coordinated update set:
  - `AGENTS.md`
  - `docs/agents/25-docs-ssot-policy/docs-ssot-policy.md`
  - `docs/agents/35-authority-bounded-modules/authority-bounded-modules.md`
  - `docs/agents/playbooks/project-docs-template/project-docs-template.md`
  - `docs/agents/playbooks/design-principles-checklist/design-principles-checklist.md`
  - `docs/agents/workflow-registry/workflow-registry.md`
  - `docs/project/architecture/architecture.md`
  - `agents-manifest.yaml`
  - `README.md`
  - `scripts/entrypoint_contracts.json`
  - `scripts/check_docs_ssot.ps1`
  - `scripts/check_project_docs.ps1`
  - `scripts/check_docs_router_contract/check_docs_router_contract_main.py`
  - `scripts/check_governance_core/_manifest_and_docs.py`
  - `scripts/check_folder_architecture/check_folder_architecture_main.py`
  - `templates/python-dual-entry/README.md`
- Verification witness:
  - `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/check_docs_ssot.ps1` passes
  - `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/check_project_docs.ps1` passes
  - `python3 scripts/check_folder_architecture/check_folder_architecture_main.py` passes
  - `python3 scripts/check_governance_core/check_governance_core_main.py` passes
  - `python3 scripts/check_docs_router_contract/check_docs_router_contract_main.py` passes, including the negative cases where a router points to a missing primary leaf doc or contains non-routing content
- Review trigger:
  - Any proposal to change a contract-family filename pattern without updating `scripts/entrypoint_contracts.json`
  - Any proposal to reintroduce `index.md` as the universal docs router contract
  - Any proposal to rename or repurpose `SKILL.md` or `mcp.json` under this contract family

### SSOT-DEC-004 - Mandatory current-work project-doc contract
- Status: active
- Scope: project-doc goal branch ownership for repos using this governance pack
- Canonical owner:
  - Governing required-doc contract: `AGENTS.md`
  - Placement and lifecycle policy: `docs/agents/25-docs-ssot-policy/docs-ssot-policy.md`
  - Scaffold shape: `docs/agents/playbooks/project-docs-template/project-docs-template.md`
- Allowed non-owner locations:
  - `docs/project/goal/goal.md` owns durable project intent, objective, acceptance criteria, non-goals, and verification intent.
  - `docs/project/goal/current-work.md` is mandatory and owns the active-work authority record: live work status, bounded exact-prompt witness, prompt-safety decision, derived work-item goal statement, source-derived plan, handoff/checkpoint state, blockers, implementation records, stale/rejected prompt and plan reconciliation, truth-layer witnesses, review confirmation, closure handoff, next safe action, and no-active-work reset state.
  - Template/example project-doc instances may show the same shape under their own example project roots, but they do not define policy.
- Forbidden duplicates:
  - Do not let `current-work.md` restate or redefine durable project intent, objective, acceptance criteria, or non-goals owned by `goal.md`.
  - Do not model `current-work.md` as optional, triggered, deletable, or replaceable by absence.
  - Do not store secrets, credentials, PII, customer data, or oversized pasted prompt artifacts in `current-work.md`.
  - Do not create a separate project-doc `plan.md` or treat `.cursor/plans/`, chat plans, or tool UI plans as active-work authority outside `current-work.md`.
  - Do not create a parallel project memory/session/transcript tree for active work state.
- Coordinated update set:
  - `AGENTS.md`
  - `README.md`
  - `docs/agents/20-sources-of-truth-map/sources-of-truth-map.md`
  - `docs/agents/25-docs-ssot-policy/docs-ssot-policy.md`
  - `docs/agents/playbooks/project-docs-template/project-docs-template.md`
  - `docs/project/project_index.md`
  - `docs/project/architecture/architecture.md`
  - `docs/project/goal/goal_index.md`
  - `docs/project/goal/goal.md`
  - `docs/project/goal/current-work.md`
  - `scripts/check_governance_core/_project_authority_docs.py`
  - `scripts/check_governance_core/test_project_authority_routes.py`
  - `templates/python-dual-entry/docs/project/`
- Verification witness:
  - `scripts/check_governance_core/_project_authority_docs.py` requires `docs/project/goal/current-work.md`.
  - Project-doc checks fail when the mandatory current-work file or route is absent.
  - A canonical no-active-work state passes validation.
  - Active current-work records require prompt-safety, prompt, work-goal, derived-plan, implementation-record, reconciliation, truth-layer, review-confirmation, and closure-handoff witnesses.
- Review trigger:
  - Any proposal to make `current-work.md` optional, remove the no-active-work reset state, move durable project intent out of `goal.md`, or move active-work planning authority to another path.
