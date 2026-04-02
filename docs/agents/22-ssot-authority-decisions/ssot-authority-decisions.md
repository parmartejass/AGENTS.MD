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
  - `docs/agents/platforms/runtime-projections.json`
  - `docs/agents/link_repo_assets.ps1`
  - `docs/agents/index.md`
  - `README.md`
  - `agents-manifest.yaml`
  - `scripts/check_governance_core/main.py`
- Verification witness:
  - `python3 scripts/check_governance_core/main.py` passes.
  - `docs/agents/index.md`, `README.md`, and runtime projection tooling all reference `docs/agents/skills/` as the canonical reusable skill root.
  - The tracked canonical X API skill bundle exists under `docs/agents/skills/x-api-data-access/`.
- Review trigger:
  - Any proposal to move canonical X skill ownership away from `docs/agents/skills/`.
  - Any proposal to treat `X-Bookmarks Import/` as a tracked governance asset root rather than a non-authority workspace.

### SSOT-DEC-002 - Runtime projection authority vs projected runtime targets
- Status: active
- Scope: repo-owned agent assets projected into project-local or explicitly declared user-home runtime paths
- Canonical owner:
  - Concrete runtime target mapping: `docs/agents/platforms/runtime-projections.json`
  - Canonical source asset roots: `docs/agents/skills/`, `docs/agents/settings/`, `docs/agents/subagents/`, `docs/agents/mcp/`, `docs/agents/acp/`
- Allowed non-owner locations:
  - Runtime targets declared in `docs/agents/platforms/runtime-projections.json`, including project dotpaths such as `.agents/skills/`, `.codex/config.toml`, `.codex/agents/`, `.claude/agents/`, `.claude/settings.json`, `.cursor/mcp.json`, `.cursor/cli.json`, and `.mcp.json`
  - Explicit user-home targets declared in `docs/agents/platforms/runtime-projections.json`, such as `{HOME}/.agents/skills`
  - Generated or linked runtime projections created by `docs/agents/link_repo_assets.ps1` or `scripts/setup_repo_platform_assets.ps1`
- Forbidden duplicates:
  - Do not treat projected runtime files or folders as canonical owners for platform settings, MCP definitions, skills, subagents, or ACP assets
  - Do not restate concrete runtime mapping facts in `README.md` or `docs/project/platform-runtime-status/platform-runtime-status.md` as parallel authorities
  - Do not create second canonical asset roots outside the `docs/agents/` source owners listed above
- Coordinated update set:
  - `docs/agents/platforms/runtime-projections.json`
  - `docs/agents/platforms/00-platform-runtime-standards/platform-runtime-standards.md`
  - `docs/agents/mcp/00-mcp-standards/mcp-standards.md`
  - `docs/agents/settings/00-settings-standards/settings-standards.md`
  - `docs/agents/subagents/00-subagent-standards/subagent-standards.md`
  - `docs/agents/link_repo_assets.ps1`
  - `scripts/setup_repo_platform_assets.ps1`
  - `docs/project/platform-runtime-status/platform-runtime-status.md`
  - `docs/project/architecture/architecture.md`
  - `README.md`
- Verification witness:
  - `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/setup_repo_platform_assets.ps1 -Force` completes for supported defaults
  - `docs/project/platform-runtime-status/platform-runtime-status.md` references runtime projections and source owners rather than restating concrete mapping facts as SSOT
  - Projected runtime paths continue to resolve from the source owners declared in `docs/agents/platforms/runtime-projections.json`
- Review trigger:
  - Any proposal to add or remove a projected runtime target
  - Any proposal to move a runtime surface between project-local, user-home, compatibility, manual, or official support levels
  - Any proposal to treat a projected runtime path as a canonical owner rather than a non-owner projection

### SSOT-DEC-003 - Docs router authority vs canonical narrative leaf docs
- Status: active
- Scope: documentation folders under `docs/` that carry narrative governance or project content
- Canonical owner:
  - Folder routing contract: `<folder>/index.md`
  - Canonical narrative content: exactly one descriptive non-`index.md` markdown file inside the same folder
- Allowed non-owner locations:
  - Legacy content-bearing `index.md` files in folders not yet migrated to the router-plus-leaf pattern during the staged rollout
  - Router indexes may remain the only markdown contract in artifact-first folders that only catalog payload children such as JSON, TOML, generated outputs, or dated evidence subfolders
- Forbidden duplicates:
  - Do not keep the same narrative content both in `index.md` and the canonical leaf doc after a folder is migrated
  - Do not treat router indexes as the authority for narrative content when a canonical leaf doc exists
  - Do not create multiple competing narrative leaf docs in the same migrated folder
- Coordinated update set:
  - `AGENTS.md`
  - `docs/agents/25-docs-ssot-policy/docs-ssot-policy.md`
  - `docs/agents/playbooks/project-docs-template/project-docs-template.md`
  - `docs/project/goal/`
  - `docs/project/rules/`
  - `docs/project/architecture/`
  - `docs/project/learning/`
  - `agents-manifest.yaml`
  - `README.md`
  - `scripts/migrated_router_leaves.json`
  - `scripts/check_docs_ssot.ps1`
  - `scripts/check_project_docs.ps1`
  - `scripts/check_agents_manifest.ps1`
  - `scripts/check_governance_core/_manifest_and_docs.py`
  - `scripts/check_governance_core/_repo_and_governance.py`
- Verification witness:
  - `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/check_docs_ssot.ps1` passes
  - `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/check_project_docs.ps1` passes
  - `scripts/migrated_router_leaves.json` maps every migrated narrative folder that uses an explicit canonical leaf filename
  - `python3 scripts/check_governance_core/main.py` passes
  - `python3 scripts/check_docs_router_contract/main.py` passes, including the negative case where a router points to a missing canonical leaf doc
- Review trigger:
  - Any proposal to put canonical narrative content back into `index.md`
  - Any proposal to remove `index.md` from a `docs/` directory
  - Any proposal to add multiple narrative leaf docs to a migrated folder
