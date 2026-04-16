---
doc_type: reference
ssot_owner: AGENTS.md
update_trigger: repo layout, injection profiles, or validation scripts change
---

# Architecture

## Entrypoints
- Governance SSOT: `AGENTS.md`
- Context injection manifest: `agents-manifest.yaml`
- Docs branch entrypoint: `docs/docs_index.md`
- Supporting governance docs: `docs/agents/agents_index.md`
- Validation scripts: `scripts/`

## SSOT pointers (concept -> owner)
- Governance rules: `AGENTS.md`
- Context injection routing: `agents-manifest.yaml`
- Docs policy and headers: `docs/agents/25-docs-ssot-policy/docs-ssot-policy.md`
- Folder-owned public contract filename registry: `scripts/entrypoint_contracts.json`
- Change record artifact schema: `docs/agents/schemas/change-record.schema.json`
- Change record artifact location: `docs/project/change-records/*.json`
- Folder-architecture Python scope registry: `scripts/check_folder_architecture/scope.json`
- Reusable cross-agent platform assets: `docs/agents/skills/`, `docs/agents/settings/`, `docs/agents/subagents/`, `docs/agents/mcp/`, `docs/agents/acp/`
- Concrete runtime mapping facts: `docs/agents/platforms/runtime-projections.json`
- Dated external platform evidence: `docs/agents/platforms/`, `docs/agents/integrations/`
- Reference implementation (dual-entry template): `templates/python-dual-entry/`
- Reference implementation (PR control-plane template): `templates/pr-control-plane/`

## Authority graph (owners -> dependents)
- `AGENTS.md` -> `docs/agents/*`, `docs/project/*`, `scripts/check_*.ps1`, `scripts/check_folder_architecture/check_folder_architecture_main.py`, `scripts/check_python_safety/check_python_safety_main.py`
- `agents-manifest.yaml` -> context injection procedure in `AGENTS.md` and supporting retrieval guidance
- `docs/agents/25-docs-ssot-policy/docs-ssot-policy.md` -> `scripts/check_docs_ssot.ps1`, `scripts/check_governance_core/_manifest_and_docs.py`
- `docs/agents/35-authority-bounded-modules/authority-bounded-modules.md` -> `scripts/check_folder_architecture/check_folder_architecture_main.py` and template runtime-contract examples
- `scripts/entrypoint_contracts.json` -> docs router/primary-leaf derivation in `scripts/check_docs_ssot.ps1`, `scripts/check_project_docs.ps1`, `scripts/check_docs_router_contract/check_docs_router_contract_main.py`, `scripts/check_governance_core/_manifest_and_docs.py`, and runtime public-entrypoint derivation in `scripts/check_folder_architecture/check_folder_architecture_main.py`
- `docs/agents/schemas/change-record.schema.json` -> `scripts/check_change_records.ps1`
- `scripts/check_folder_architecture/scope.json` -> declared Python roots/exceptions enforced by `scripts/check_folder_architecture/check_folder_architecture_main.py`
- `docs/agents/platforms/runtime-projections.json` -> `docs/agents/link_repo_assets.ps1`, `scripts/setup_repo_platform_assets.ps1`, README/runtime docs summaries
- Relative canonical source paths resolve from the governance root; runtime targets resolve from the project root or `{HOME}`.
- `docs/agents/link_repo_assets.ps1` -> runtime projections for `skills`, `subagents`, `mcp`, `settings`, and future supported asset classes
- `docs/agents/skills/` -> official/compatibility surfaces defined in `docs/agents/platforms/runtime-projections.json`
- `docs/agents/settings/` -> official/manual shared settings surfaces defined in `docs/agents/platforms/runtime-projections.json`
- `docs/agents/subagents/` -> official/compatibility surfaces defined in `docs/agents/platforms/runtime-projections.json`
- `docs/agents/mcp/` -> official/compatibility surfaces defined in `docs/agents/platforms/runtime-projections.json`
- `docs/agents/acp/` -> future verified ACP runtime mappings only
- `templates/pr-control-plane/control-plane.contract.json` -> template workflows + policy/evidence scripts in `templates/pr-control-plane/scripts/`
- `docs/agents/22-ssot-authority-decisions/ssot-authority-decisions.md` -> allows `X-Bookmarks Import/` as a non-owner workspace exception; `scripts/check_folder_architecture/scope.json` records that exception for checker scope without making it a canonical governance root

## Outputs
- A vendored governance pack under `.governance/` in downstream repos, with project docs under `docs/project/` and governance docs under `.governance/docs/agents/`.
- Project-owned reusable platform assets under `docs/agents/`, with runtime discovery paths or generated adapters recreated by `scripts/setup_repo_platform_assets.ps1`.
