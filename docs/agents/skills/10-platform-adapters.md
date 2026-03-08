---
doc_type: reference
ssot_owner: docs/agents/skills/00-skill-standards.md
update_trigger: platform adapter guidance changes OR new platform is added
---

# Platform Adapters (Skills)

## Purpose
- Map the skill standards into platform-specific implementations without duplicating core policy.
- Keep exact runtime-path/support-level facts in `docs/agents/platforms/runtime-projections.json`.
- Keep dated official evidence in `docs/agents/platforms/index.md`.

## Adapter expectations
- Start from `docs/agents/skills/00-skill-standards.md` and keep core rules referenced, not redefined.
- Document platform-specific file locations and installation/update steps.
- Describe tool capability constraints (available tools, sandbox limits, permissions).
- Include verification or smoke-check steps when applicable.

## Adapter model
- Codex has an official project skill surface, so skill bundles can be linked directly into the official runtime path.
- Claude Code now has an official project skill surface under `.claude/skills/<skill-name>/SKILL.md`; legacy `.claude/commands/*.md` adapters remain compatibility-only.
- Cursor does not currently have a verified official repo-owned skill folder contract; use official rules and direct canonical skill references instead of pretending Cursor skills are first-class.
- If a platform contract changes, update this file, `docs/agents/platforms/runtime-projections.json`, the dated platform note, and `docs/agents/link_repo_assets.ps1` together.

## Codex CLI
- Source-preserved example archive: `docs/agents/skills/platform-adapters/Codex CLI/llmjunky-last-30-days.md`
- Keep the archive non-authoritative; `docs/agents/skills/00-skill-standards.md` remains the SSOT for adapter rules.

## Current verified runtime stance
- Codex official skill path: see `docs/agents/platforms/codex/2026-03-06-official-runtime.md`
- Claude Code official skill/agent surfaces: see `docs/agents/platforms/claude-code/2026-03-06-official-runtime.md`
- Cursor official rule surface: see `docs/agents/platforms/cursor/2026-03-06-official-runtime.md`
- Compatibility-only paths must stay opt-in and explicitly labeled as compatibility in the runtime projection manifest.
