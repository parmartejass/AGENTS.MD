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
- Reference implementation (dual-entry template): `templates/python-dual-entry/`

## Authority graph (owners -> dependents)
- `AGENTS.md` -> `docs/agents/*`, `docs/project/*`, `scripts/check_*.ps1`, `scripts/check_python_safety.py`
- `agents-manifest.yaml` -> context injection procedure in `AGENTS.md` and supporting retrieval guidance
- `docs/agents/25-docs-ssot-policy.md` -> `scripts/check_docs_ssot.ps1`
- `docs/agents/schemas/change-record.schema.json` -> `scripts/check_change_records.ps1`

## Outputs
- A vendored governance pack under `.governance/` in downstream repos, with project docs under `docs/project/` and governance docs under `.governance/docs/agents/`.
