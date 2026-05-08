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
- Repo-owned reusable assets: `docs/agents/skills/`, `docs/agents/settings/`, `docs/agents/mcp/`
- Runtime projection mapping: `docs/agents/platforms/runtime-projections.json`
- Runtime config and local-secret boundary: `docs/agents/settings/00-settings-standards/settings-standards.md`
- Reference implementation (dual-entry template): `templates/python-dual-entry/`

## Authority graph (owners -> dependents)
- `AGENTS.md` -> `docs/agents/*`, `docs/project/*`, `scripts/check_*.ps1`, `scripts/check_folder_architecture/check_folder_architecture_main.py`, `scripts/check_python_safety/check_python_safety_main.py`
- `agents-manifest.yaml` -> context injection procedure in `AGENTS.md` and supporting retrieval guidance
- `docs/agents/25-docs-ssot-policy/docs-ssot-policy.md` -> `scripts/check_docs_ssot.ps1`, `scripts/check_governance_core/_manifest_and_docs.py`
- `docs/agents/35-authority-bounded-modules/authority-bounded-modules.md` -> `scripts/check_folder_architecture/check_folder_architecture_main.py` and template runtime-contract examples
- `scripts/entrypoint_contracts.json` -> docs router/primary-leaf derivation in `scripts/check_docs_ssot.ps1`, `scripts/check_project_docs.ps1`, `scripts/check_docs_router_contract/check_docs_router_contract_main.py`, `scripts/check_governance_core/_manifest_and_docs.py`, and runtime public-entrypoint derivation in `scripts/check_folder_architecture/check_folder_architecture_main.py`
- `docs/agents/schemas/change-record.schema.json` -> `scripts/check_change_records.ps1`
- `scripts/check_folder_architecture/scope.json` -> declared Python roots/exceptions enforced by `scripts/check_folder_architecture/check_folder_architecture_main.py`
- `docs/agents/platforms/runtime-projections.json` -> `docs/agents/link_repo_assets.ps1`, `scripts/setup_repo_platform_assets.ps1`, `.cursor/**`, `.claude/**`, `.codex/**`, `.agents/**`, and `.mcp.json` projected runtime surfaces
- `docs/agents/skills/` -> reusable skill bundles and projected skill runtime assets
- `docs/agents/settings/` -> shared settings examples and local-secret boundary
- `docs/agents/mcp/` -> canonical non-secret MCP payloads
- `docs/agents/22-ssot-authority-decisions/ssot-authority-decisions.md` -> allows `X-Bookmarks Import/` as a non-owner workspace exception; `scripts/check_folder_architecture/scope.json` records that exception for checker scope without making it a canonical governance root

## Outputs
- A vendored governance pack under `.governance/` in downstream repos, with project docs under `docs/project/` and governance docs under `.governance/docs/agents/`.
- Repo-owned source assets under `docs/agents/skills/`, `docs/agents/settings/`, and `docs/agents/mcp/`; runtime dotpaths are projections, not canonical owners.
