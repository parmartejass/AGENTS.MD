---
doc_type: playbook
ssot_owner: AGENTS.md
update_trigger: project docs prompt conventions or SSOT reference rules change
---

# Project Docs Prompt Template

Use this template to request project-specific docs without duplicating code-owned facts. Reference SSOT owners by identifier (module/config/workflow) instead of repeating literals or rules.

## Prompt

```
Goal:
- <one-sentence intent for the doc>

Doc type:
- <goal|rules|architecture|learning|runbook|adr>

Scope:
- <directory or module names in scope>

SSOT owners to reference (by identifier):
- <module/path or registry that owns constants/config/rules/workflows>

Required references:
- <entrypoints, config keys, or rule function names to link to>

Non-goals (avoid duplication):
- Do not restate constants, defaults, or validation rules.
- Do not inline code blocks that mirror production logic.

Acceptance criteria:
- Doc has required header (doc_type, ssot_owner, update_trigger).
- Doc references SSOT owners by identifier only.
- Doc links to the relevant doc index (no orphan docs).
```

## Notes

- If a doc would duplicate a rule or constant, replace the content with a reference to the SSOT owner.
- Keep the doc minimal and intent-focused; prefer linking to entrypoints over re-explaining behavior.
