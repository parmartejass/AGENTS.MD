---
doc_type: reference
ssot_owner: docs/agents/skills/00-skill-standards.md
update_trigger: platform adapter guidance changes OR new platform is added
---

# Platform Adapters (Skills)

## Purpose
- Map the skill standards into platform-specific implementations without duplicating core policy.

## Adapter expectations
- Start from `docs/agents/skills/00-skill-standards.md` and keep core rules referenced, not redefined.
- Document platform-specific file locations and installation/update steps.
- Describe tool capability constraints (available tools, sandbox limits, permissions).
- Include verification or smoke-check steps when applicable.

## Platform sections (when added)
- Label each section by platform (Cursor, Codex, Claude, etc.).
- Keep platform details here and link from `docs/agents/index.md` if new docs are created.
- Update `agents-manifest.yaml` profiles if a new skills doc should be injected by default for that platform.

## Cursor
- Use the Task tool to run the council in parallel; keep council agents review-only and edits in the main agent.
