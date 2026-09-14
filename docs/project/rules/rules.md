---
doc_type: policy
ssot_owner: docs/project/rules/rules.md
update_trigger: governance rules change OR new recurring maintenance pitfalls emerge
---

# Rules (Do / Don't)

## Governance (authoritative)
- Follow `AGENTS.md` (do not duplicate its rules here).

## Boundary
- This root doc owns project-local do/don't constraints that supplement reusable governance.
- It does not own reusable policy, architecture, data truth, operational learnings, or task status.

## When to create a branch-local owner subdoc
- Create a rules subdoc when a durable project-specific constraint needs its own intent, boundary, invariant, change rule, and verification.
- Do not create rules subdocs for reusable governance rules already owned by `AGENTS.md` or supporting docs.

## Current Summary
- Current rules remain short routing constraints for this governance-pack repo.
- No branch-local rules subdocs are declared.

## Branch-local owner subdocs
- None currently declared.

## Do
- Repository checks MUST remain deterministic and dependency-minimal.
- Reusable source-asset placement follows `docs/agents/22-ssot-authority-decisions/ssot-authority-decisions.md`; workspace exceptions remain non-owner locations.
- Repo-owned skill content and packaging MUST follow `docs/agents/skills/00-skill-standards/skill-standards.md`.

## Don't
- Generated artifacts (bytecode, caches, local outputs) MUST NOT be tracked.
- Retired tracked root runtime copies, repo-owned projection helpers, and runnable reference-application templates MUST NOT be reintroduced.
- External-service setup and local runtime configuration MUST remain with their consumer/source owner under `docs/agents/settings/00-settings-standards/settings-standards.md`.
