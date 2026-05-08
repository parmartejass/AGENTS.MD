---
doc_type: policy
ssot_owner: AGENTS.md
update_trigger: governance rules change OR new recurring maintenance pitfalls emerge
---

# Rules (Do / Don't)

## Governance (authoritative)
- Follow `AGENTS.md` (do not duplicate its rules here).

## Do
- Keep templates as reference implementations (patterns, not specs).
- Keep checks deterministic and dependency-minimal.
- Keep reusable source assets under `docs/agents/`.
- For repo-owned skills, keep operational guidance in the skill bundle under `docs/agents/skills/<skill-name>/SKILL.md` instead of restating it in project docs.

## Don't
- Don't add repo-generated artifacts to git (bytecode, caches, template outputs).
- Don't expand docs into a second SSOT; reference owners by path/identifier instead.
- Don't treat project docs or shared repo config as the authority for external service setup.
- Don't treat local tool runtime paths or user-home config as canonical governance owners.
