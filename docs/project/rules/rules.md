---
doc_type: policy
ssot_owner: docs/project/rules/rules.md
update_trigger: governance rules change OR new recurring maintenance pitfalls emerge
---

# Rules (Do / Don't)

## Boundary
- This root doc owns project-local do/don't constraints that supplement reusable governance.
- It does not own reusable policy, architecture, data truth, operational learnings, or task status.

## Do
- Repository checks MUST remain deterministic and dependency-minimal.
- Reusable source-asset placement MUST follow `docs/agents/governance/ssot/authority-decisions/authority-decisions.md`.
- Workspace exceptions remain non-owner locations.
- Repo-owned skill content and packaging MUST follow `docs/agents/governance/skills/skills.md`.

## Don't
- Generated artifacts (bytecode, caches, local outputs) MUST stay untracked.
- Folder names and titles MUST stay free of numeric prefixes.
- External-service setup and local runtime configuration MUST remain with their consumer/source owner under `docs/agents/governance/settings/settings.md`.
