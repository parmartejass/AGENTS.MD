---
doc_type: policy
ssot_owner: AGENTS.md
update_trigger: docs governance rules change OR new doc categories are added
---

# 25 — Docs SSOT Policy (Prevent Drift)

Docs are permitted only if they do not become a second SSOT.

## Rule: “Code owns facts; docs own intent”

### Code SSOT (authoritative)
These belong in code (or a single config owner), not in docs:
- constants and repeated literals
- config keys/defaults/schema
- rules/conditions/validation logic
- workflow behavior details and branching

### Docs (supporting, non-authoritative)
Docs may describe:
- intent (“why”) and invariants
- contracts and interfaces (reference SSOT symbols/entrypoints)
- runbooks/playbooks (reference workflow entrypoints + config keys by identifier)
- decision records (ADR-style)

## Required header template
Every Markdown doc (`*.md`) under `docs/` (except index pages) must start with:

Index pages are exempt at any nesting level (`index.md` or `*/index.md`).

```
---
doc_type: policy|reference|runbook|playbook|decision|generated
ssot_owner: AGENTS.md | <module path> | <workflow registry location>
update_trigger: <what change requires updating this doc>
---
```

Generated docs must also use this header, set `doc_type: generated`, and live under `docs/generated/`.

## Operational asset carveouts
Operational agent assets under `docs/agents/` can coexist with governance docs when their runtime format is not the docs header schema.

- Skills:
  - Installable skill bundles under `docs/agents/skills/<skill-name>/` are operational artifacts.
  - A skill bundle directory is identified by a local `SKILL.md`.
  - `SKILL.md` frontmatter is owned by the skill runtime format, not the docs header schema.

- Subagents:
  - Runtime subagent files under `docs/agents/subagents/<platform>/` are operational artifacts.
  - Their markdown frontmatter is owned by the target platform, not the docs header schema.

- Repo checks exclude those operational asset paths from docs header enforcement.
- Governance docs that describe these asset types still live directly under `docs/agents/<category>/*.md` and must keep the standard docs header.

## “Reference by identifier” convention
When mentioning a value, prefer the SSOT identifier name, not the literal.
When describing a rule, reference the named rule function (or equivalent).

## Context injection guardrails (avoid stale-doc confidence)
Context injection should reduce bloat and prevent “random docs” from becoming implicit requirements:
- Keep `agents-manifest.yaml:default_inject` minimal; inject supporting docs via narrowly-scoped profiles.
- Treat injected docs as supporting context only; verify behavior in code/config and with deterministic tools.
- Create project-specific docs only for intent/runbooks, keep them minimal, and reference SSOT owners by identifier (do not re-encode constants/rules).
- If a doc might drift, tighten its `update_trigger` and avoid adding it to broad/always-on injection.

## Generated docs (optional)
Generated docs are allowed if:
- clearly marked `doc_type: generated`
- not edited manually
- regenerated from the code SSOT

Keep generated output in `docs/generated/` and do not accept manual edits there.
