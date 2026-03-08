---
doc_type: reference
ssot_owner: AGENTS.md
update_trigger: repo layout, injection profiles, or validation scripts change
---

# Architecture

## Entrypoints
- Governance SSOT: `AGENTS.md`
- Context injection manifest: `agents-manifest.yaml`
- Supporting governance docs: `docs/agents/index.md`
- Validation scripts: `scripts/`

## SSOT pointers (concept -> owner)
- Governance rules: `AGENTS.md`
- Context injection routing: `agents-manifest.yaml`
- Docs policy and headers: `docs/agents/25-docs-ssot-policy.md`
- Change record artifact schema: `docs/agents/schemas/change-record.schema.json`
- Change record artifact location: `docs/project/change-records/*.json`
- Reusable cross-agent platform assets: `docs/agents/skills/`, `docs/agents/settings/`, `docs/agents/subagents/`, `docs/agents/mcp/`, `docs/agents/acp/`
- Concrete runtime mapping facts: `docs/agents/platforms/runtime-projections.json`
- Dated external platform evidence: `docs/agents/platforms/`, `docs/agents/integrations/`
- Reference implementation (dual-entry template): `templates/python-dual-entry/`
- Reference implementation (PR control-plane template): `templates/pr-control-plane/`

## Authority graph (owners -> dependents)
- `AGENTS.md` -> `docs/agents/*`, `docs/project/*`, `scripts/check_*.ps1`, `scripts/check_python_safety.py`
- `agents-manifest.yaml` -> context injection procedure in `AGENTS.md` and supporting retrieval guidance
- `docs/agents/25-docs-ssot-policy.md` -> `scripts/check_docs_ssot.ps1`
- `docs/agents/schemas/change-record.schema.json` -> `scripts/check_change_records.ps1`
- `docs/agents/platforms/runtime-projections.json` -> `docs/agents/link_repo_assets.ps1`, `scripts/setup_repo_platform_assets.ps1`, README/runtime docs summaries
- Relative canonical source paths resolve from the governance root; runtime targets resolve from the project root or `{HOME}`.
- `docs/agents/link_repo_assets.ps1` -> runtime projections for `skills`, `subagents`, `mcp`, `settings`, and future supported asset classes
- `docs/agents/skills/` -> official/compatibility surfaces defined in `docs/agents/platforms/runtime-projections.json`
- `docs/agents/settings/` -> official/manual shared settings surfaces defined in `docs/agents/platforms/runtime-projections.json`
- `docs/agents/subagents/` -> official/compatibility surfaces defined in `docs/agents/platforms/runtime-projections.json`
- `docs/agents/mcp/` -> official/compatibility surfaces defined in `docs/agents/platforms/runtime-projections.json`
- `docs/agents/acp/` -> future verified ACP runtime mappings only
- `templates/pr-control-plane/control-plane.contract.json` -> template workflows + policy/evidence scripts in `templates/pr-control-plane/scripts/`

## Outputs
- A vendored governance pack under `.governance/` in downstream repos, with project docs under `docs/project/` and governance docs under `.governance/docs/agents/`.
- Project-owned reusable platform assets under `docs/agents/`, with runtime discovery paths or generated adapters recreated by `scripts/setup_repo_platform_assets.ps1`.
