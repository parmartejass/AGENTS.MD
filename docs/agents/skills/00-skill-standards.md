---
doc_type: policy
ssot_owner: docs/agents/skills/00-skill-standards.md
update_trigger: skill standards change OR new platform support requirements emerge
---

# Skill Standards (SSOT)

## Definition
- A skill is a platform-specific adapter that operationalizes governance guidance in a given tool environment.

## Invariants (must hold)
- No policy duplication: reference `AGENTS.md` and core docs; do not restate hard gates or rules.
- Scope clarity: each skill states platform, scope, and installation location.
- Compatibility: declare required tool versions/constraints when relevant; avoid silent breaking changes.
- Deterministic operations: include verification or smoke-check steps when applicable.

## Versioning + compatibility
- Prefer additive updates; document any breaking change and the migration path.
- Keep compatibility notes short and update only when behavior changes.

## Codification targets
- Cross-platform principles → `docs/agents/*.md`
- Copy/paste templates → `docs/agents/playbooks/*.md`
- Platform-specific adapters → `docs/agents/skills/*.md`
