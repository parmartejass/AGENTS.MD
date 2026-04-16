---
name: governance discoverability and ssot routing
overview: Archived planning record for the repo-wide discoverability and governance-branch routing shift. This copy keeps only the normalized final owner map and verification references so historical planning notes do not reintroduce retired flat-path assumptions.
todos:
  - id: inventory-governed-surfaces
    content: Inventory governed surfaces and consumers before any repo-wide routing change.
    status: archived
  - id: split-discoverability-owners
    content: Keep one owner per discoverability responsibility across README, project docs, governance docs, and machine-readable routing.
    status: archived
  - id: harden-validators
    content: Update validators before moving docs so source-repo and vendored-governance roots stay aligned.
    status: archived
isProject: false
---

# Archived Discoverability Plan

## Normalized Owner Map
- Repo-wide discoverability owner: [README.md](README.md)
- Project-doc entrypoint: [docs/project/project_index.md](docs/project/project_index.md)
- Project architecture / governed-surface classification: [docs/project/architecture/architecture_index.md](docs/project/architecture/architecture_index.md)
- Governance-doc navigation owner: [docs/agents/agents_index.md](docs/agents/agents_index.md)
- Docs placement and router policy owner: [docs/agents/25-docs-ssot-policy/docs-ssot-policy_index.md](docs/agents/25-docs-ssot-policy/docs-ssot-policy_index.md)
- Platform adapter surface owner: [docs/agents/skills/10-platform-adapters/platform-adapters_index.md](docs/agents/skills/10-platform-adapters/platform-adapters_index.md)
- Machine-readable routing owner: [agents-manifest.yaml](agents-manifest.yaml)

## Archived Findings
- Hidden source-repo-only surfaces such as `.cursor/agents/` and `.cursor/plans/` require explicit discoverability ownership in the project architecture branch.
- Governance-doc discoverability must flow through registered `*_index.md` routers, not legacy flat `index.md` paths.
- Validator hardening must land before broad doc moves so source-repo and vendored `.governance/` validation remain aligned.

## Archived Verification References
- `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/check_agents_manifest.ps1`
- `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/check_docs_ssot.ps1`
- `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/check_project_docs.ps1`
- `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/check_change_records.ps1`
- `python scripts/check_governance_core/check_governance_core_main.py`

## Archive Note
- This file is retained only as historical planning context.
- Current path contracts must be taken from the normalized owner map above, not inferred from prior flat-path layouts.
