---
doc_type: reference
ssot_owner: docs/agents/platforms/runtime-projections.json
update_trigger: official platform docs, repo runtime projections, or local connection checks change
---

# Platform Runtime Status

Verified on: 2026-05-08

## Scope

- This doc records local connection status for Cursor, Claude Code, and Codex in this repo.
- Runtime mapping SSOT stays in `docs/agents/platforms/runtime-projections.json`.
- Dated external evidence lives under `docs/agents/platforms/`.

## Official source set

- Cursor:
  - Official docs: `https://docs.cursor.com/en/context/rules`, `https://docs.cursor.com/en/context/mcp`, `https://docs.cursor.com/en/cli/reference/configuration`, `https://docs.cursor.com/cli/mcp`
  - Local evidence note: `docs/agents/platforms/cursor/2026-03-06-official-runtime/evidence.md`
- Claude Code:
  - Official docs: `https://docs.anthropic.com/en/docs/claude-code/settings`, `https://docs.anthropic.com/en/docs/claude-code/slash-commands`, `https://docs.anthropic.com/en/docs/claude-code/sub-agents`, `https://docs.anthropic.com/en/docs/claude-code/mcp`
  - Local evidence note: `docs/agents/platforms/claude-code/2026-03-06-official-runtime/evidence.md`
- Codex:
  - Official docs: `https://developers.openai.com/codex/skills`, `https://developers.openai.com/codex/mcp`, `https://developers.openai.com/codex/cli`
  - Local evidence note: `docs/agents/platforms/codex/2026-03-06-official-runtime/evidence.md`
- Other verified references:
  - MCP: `docs/agents/platforms/mcp/2026-03-06-official-runtime/evidence.md`

## Current repo status

### Cursor

- Status: connected and aligned with current official docs.
- Verified surfaces:
  - No Cursor-specific repo loader stub is required; repo loader stubs are `AGENTS.md` and `CLAUDE.md`.
  - `.cursor/agents/` is not a repo-owned runtime projection target.
  - `.cursor/rules/` is compatibility-only and is not projected by the default bootstrap path.
  - `.cursor/mcp.json` is managed by the Cursor MCP runtime projection defined in `docs/agents/platforms/runtime-projections.json`.
  - `.cursor/cli.json` is managed by the shared settings projection from `docs/agents/settings/cursor/cli.json`.
- Migration note:
  - `.cursorrules` is legacy in the official docs and is not a repo-owned loader stub. `.cursor/agents/` and `.cursor/rules/` stay out of the default bootstrap path.
  - Existing tracked `.cursor/agents/` files are unchanged by this retirement; this cleanup only removes the former `docs/agents/subagents/` projection source.

### Claude Code

- Status: connected and migrated to the current official skill surface.
- Verified surfaces:
  - `CLAUDE.md` loader stub is present and routes back to `AGENTS.md`.
  - `.claude/skills/` exists and projects the canonical bundles directly.
  - `.claude/agents/` is not a repo-owned runtime projection target.
  - `.claude/settings.json` is managed by the shared settings projection from `docs/agents/settings/claude-code/settings.json`.
  - `.mcp.json` is the managed target path for the shared MCP config when no conflicting local non-link file is present.
  - `.claude/settings.local.json` is unmanaged and may be present locally.
- Migration note:
  - `.claude/commands/` is now compatibility-only in this repo and is no longer part of the default projection path.
  - If `.claude/agents/` remains from older checkouts, remove it manually; setup no longer projects or cleans this retired subagent surface.

### Codex

- Status: connected and aligned with current official docs.
- Verified surfaces:
  - `.agents/skills/` exists with projected skill bundles from `docs/agents/skills/`.
  - `.codex/config.toml` is the managed project-local settings projection from `docs/agents/settings/codex/config.toml`.
- Migration note:
  - Current official user-scope skills live in `$HOME/.agents/skills`. This repo keeps user-home Codex skill paths manual and project-local `.agents/skills` remains the default.
  - Codex subagent role adapters are not repo-owned runtime projections; canonical agent instructions remain in `AGENTS.md`.
  - If `.codex/agents/` remains from older checkouts, treat it as local runtime state and not as a canonical source.

## Verification method

- Official docs were re-checked on 2026-03-08 against vendor documentation.
- Local runtime checks used:
  - hash match for repo-owned settings and MCP files
  - existence/absence checks for default runtime surfaces and compatibility-only directories
  - unmanaged-local-file awareness for `.claude/settings.local.json` as a local-only ignored override

## Residual migration watch items

- Cursor: keep `.cursor/agents/` plus `.cursor/rules/` out of the default bootstrap path.
- Claude Code: `.claude/commands/` remains compatibility-only for older setups.
- Codex: do not treat `~/.codex/skills` as the current official user-scope contract.
