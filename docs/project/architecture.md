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
- Reference implementation (dual-entry template): `templates/python-dual-entry/`

## Outputs
- A copied governance pack in downstream repos, with project docs under `docs/project/` and governance docs under `docs/agents/`.
