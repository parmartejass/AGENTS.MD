---
doc_type: reference
ssot_owner: docs/agents/skills/00-skill-standards/skill-standards.md
update_trigger: platform adapter guidance changes OR new platform is added
---

# Platform Adapters (Skills)

## Purpose
- Map the skill standards into platform-specific implementations without duplicating core policy.
- Keep this doc referential. Repo-owned runtime projection choices are declared in `docs/agents/platforms/runtime-projections.json`; target projects own any runtime installation choices outside that manifest.

## Adapter expectations
- Start from `docs/agents/skills/00-skill-standards/skill-standards.md` and keep core rules referenced, not redefined.
- Document platform-specific file locations and installation/update steps.
- Describe tool capability constraints (available tools, sandbox limits, permissions).
- Include verification or smoke-check steps when applicable.

## Adapter model
- Codex, Claude Code, Cursor, and other tools have different runtime conventions.
- This repo keeps the reusable bundle under `docs/agents/skills/<skill-name>/` and declares supported repo-owned projections in `docs/agents/platforms/runtime-projections.json`.
- If a platform contract changes, update this file, the affected skill bundle guidance, and the runtime projection manifest together.

## Codex CLI
- Source-preserved example archive: `docs/agents/skills/platform-adapters/Codex CLI/llmjunky-last-30-days/evidence.md`
- Keep the archive non-authoritative; `docs/agents/skills/00-skill-standards/skill-standards.md` remains the SSOT for adapter rules.

## Scaling note
- At high skill counts (approximately 160+), flat skill directories can exhaust the runtime context budget (see `docs/agents/skills/00-skill-standards/skill-standards.md` "Context Budget Constraint"). Hierarchical two-tier routing (e.g., skill-tree pattern) can reduce token overhead by up to 88%.
- If a project exceeds the budget, evaluate per-platform clustering before adding more skills. Reference: skill-tree (github.com/danielbrodie/skill-tree).

## Current runtime stance
- Skills in this pack are canonical source bundles.
- Repo-owned runtime projections are active only where declared in `docs/agents/platforms/runtime-projections.json`.
- Runtime installation evidence outside declared projections can be recorded by the consuming project, not as a parallel governance-owned projection surface here.
