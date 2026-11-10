---
doc_type: policy
ssot_owner: docs/project/rules/rules.md
update_trigger: governance rules change OR new recurring maintenance pitfalls emerge
---

# Rules (Do / Don't)

## Boundary
- This root doc owns project-local do/don't constraints that supplement reusable governance.
- It does not own reusable policy, architecture, data truth, operational learnings, or task status.

## Don't
- Generated artifacts (bytecode, caches, local outputs) MUST NOT be tracked.
- Owner docs under `docs/agents/` outside the ssot jurisdiction MUST NOT carry route or applies lines or cross-jurisdiction paths to other owner docs; numeric prefixes in folder names or titles are Prohibited.
- Retired tracked root runtime copies, repo-owned projection helpers, and runnable reference-application templates MUST NOT be reintroduced.
