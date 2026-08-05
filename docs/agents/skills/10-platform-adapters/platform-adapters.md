---
doc_type: reference
ssot_owner: docs/agents/skills/00-skill-standards/skill-standards.md
update_trigger: platform adapter guidance changes OR new platform is added
---

# Platform Adapters (Skills)

## Purpose
- Map the skill standards into platform-specific implementations without duplicating core policy.
- Keep this doc referential. Target projects own runtime installation choices; this repo owns reusable source bundles only.

## Adapter expectations
- Start from `docs/agents/skills/00-skill-standards/skill-standards.md` and keep core rules referenced, not redefined.
- Document platform-specific file locations and installation/update steps.
- Describe tool capability constraints (available tools, sandbox limits, permissions).
- Include verification or smoke-check steps when applicable.

## Adapter model
- Codex, Claude Code, Cursor, and other tools have different runtime conventions.
- This repo keeps reusable bundles under `docs/agents/skills/<skill-name>/`.
- If a platform contract changes the reusable source-bundle guidance, update this file and the affected skill bundle guidance together.

## Codex CLI
- Source-preserved example archive: `docs/agents/skills/platform-adapters/Codex CLI/llmjunky-last-30-days/evidence.md`
- Keep the archive non-authoritative; `docs/agents/skills/00-skill-standards/skill-standards.md` remains the SSOT for adapter rules.

## Scaling note
- At high skill counts (approximately 160+), flat skill directories can exhaust the runtime context budget (see `docs/agents/skills/00-skill-standards/skill-standards.md` "Context Budget Constraint"). Hierarchical two-tier routing (e.g., skill-tree pattern) can reduce token overhead by up to 88%.
- If a project exceeds the budget, evaluate per-platform clustering before adding more skills. Reference: skill-tree (github.com/danielbrodie/skill-tree).

## Current runtime stance
- Skills in this pack are canonical source bundles.
- Runtime installation evidence can be recorded by the consuming project, not as a parallel governance-owned projection surface here.
