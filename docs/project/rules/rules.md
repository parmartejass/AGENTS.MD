---
doc_type: policy
ssot_owner: docs/project/rules/rules.md
update_trigger: governance rules change OR new recurring maintenance pitfalls emerge
---

# Rules (Do / Don't)

## Boundary
- This root doc owns project-local do/don't constraints that supplement reusable governance.
- It does not own reusable policy, architecture, data truth, operational learnings, or task status.
- Follow `AGENTS.md`; duplicating its rules here is Prohibited.

## Do
- Repository checks MUST remain deterministic and dependency-minimal.
- Reusable source-asset placement MUST follow `docs/agents/governance/ssot/authority-decisions/authority-decisions.md`.
- Workspace exceptions remain non-owner locations.
- Repo-owned skill content and packaging MUST follow `docs/agents/governance/skills/skills.md`.
- Cross-jurisdiction relations between `docs/agents/` owners MUST live only in the ssot jurisdiction (`docs/agents/governance/ssot/`); every other owner doc names another jurisdiction by its noun.

## Don't
- Generated artifacts (bytecode, caches, local outputs) MUST NOT be tracked.
- Owner docs under `docs/agents/` outside the ssot jurisdiction MUST NOT carry route or applies lines or cross-jurisdiction paths to other owner docs; numeric prefixes in folder names or titles are Prohibited.
- Retired tracked root runtime copies, repo-owned projection helpers, and runnable reference-application templates MUST NOT be reintroduced.
- External-service setup and local runtime configuration MUST remain with their consumer/source owner under `docs/agents/governance/settings/settings.md`.

## Current Summary
- Current rules remain short routing constraints for this governance-pack repo.

## Branch-local owner subdocs
- None currently declared.
- Create a rules subdoc when a durable project-specific constraint needs its own intent, boundary, invariant, change rule, and verification.
- Creating rules subdocs for reusable governance already owned by `AGENTS.md` or supporting docs is Prohibited.
