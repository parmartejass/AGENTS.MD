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

## Don't
- Don't add repo-generated artifacts to git (bytecode, caches, template outputs).
- Don't expand docs into a second SSOT; reference owners by path/identifier instead.
