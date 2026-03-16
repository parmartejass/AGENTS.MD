---
doc_type: reference
ssot_owner: docs/agents/platforms/runtime-projections.json
update_trigger: official platform docs, repo runtime projections, or local connection checks change
---

# Platform Runtime Status

Verified on: 2026-03-08

## Scope

- This doc records local connection status for Cursor, Claude Code, and Codex in this repo.
- Runtime mapping SSOT stays in `docs/agents/platforms/runtime-projections.json`.
- Dated external evidence lives under `docs/agents/platforms/`.

## Official source set

- Cursor:
  - Official docs: `https://docs.cursor.com/en/context/rules`, `https://docs.cursor.com/en/context/mcp`, `https://docs.cursor.com/en/cli/reference/configuration`, `https://docs.cursor.com/cli/mcp`
  - Local evidence note: `docs/agents/platforms/cursor/2026-03-06-official-runtime.md`
- Claude Code:
  - Official docs: `https://docs.anthropic.com/en/docs/claude-code/settings`, `https://docs.anthropic.com/en/docs/claude-code/slash-commands`, `https://docs.anthropic.com/en/docs/claude-code/sub-agents`, `https://docs.anthropic.com/en/docs/claude-code/mcp`
  - Local evidence note: `docs/agents/platforms/claude-code/2026-03-06-official-runtime.md`
- Codex:
  - Official docs: `https://developers.openai.com/codex/skills`, `https://developers.openai.com/codex/mcp`, `https://developers.openai.com/codex/cli`
  - Local evidence note: `docs/agents/platforms/codex/2026-03-06-official-runtime.md`
- Other verified references:
  - MCP: `docs/agents/platforms/mcp/2026-03-06-official-runtime.md`

## Current repo status

### Cursor

- Status: connected and aligned with current official docs.
- Verified surfaces:
  - `.cursorrules` loader stub is present and routes back to `AGENTS.md`.
  - Existing `.cursor/agents/` content is retained by the default bootstrap path for this repo's compatibility workflow.
  - `.cursor/rules/` is compatibility-only and is not projected by the default bootstrap path.
  - `.cursor/mcp.json` content matches `docs/agents/mcp/shared/mcp.json`.
  - `.cursor/cli.json` content matches `docs/agents/settings/cursor/cli.json`.
- Migration note:
  - `.cursorrules` is legacy in the official docs, but this repo keeps it as the default clean loader surface. Existing `.cursor/agents/` content is preserved when present, while `.cursor/rules/` remains compatibility-only and stays out of the default bootstrap path.

### Claude Code

- Status: connected and migrated to the current official skill surface.
- Verified surfaces:
  - `CLAUDE.md` loader stub is present and routes back to `AGENTS.md`.
  - `.claude/skills/` exists and projects the canonical bundles directly.
  - `.claude/agents/` points to `docs/agents/subagents/shared`.
  - `.claude/settings.json` content matches `docs/agents/settings/claude-code/settings.json`.
  - `.mcp.json` is the managed target path for the shared MCP config when no conflicting local non-link file is present.
  - `.claude/settings.local.json` is unmanaged and may be present locally.
- Migration note:
  - `.claude/commands/` is now compatibility-only in this repo and is no longer part of the default projection path.

### Codex

- Status: connected and aligned with current official docs.
- Verified surfaces:
  - `.agents/skills/` exists with projected skill bundles from `docs/agents/skills/`.
  - `.codex/agents/` points to `docs/agents/subagents/codex/`.
  - `.codex/config.toml` content matches `docs/agents/settings/codex/config.toml`, including `[features].multi_agent = true` and role-level `config_file` entries under `[agents.<role>]`.
- Migration note:
  - Current official user-scope skills live in `$HOME/.agents/skills`. This repo keeps user-home Codex skill paths manual and project-local `.agents/skills` remains the default.
  - Codex subagent role adapters are platform-specific TOML projections; shared prompt intent remains canonical in `docs/agents/subagents/shared/`.

## Verification method

- Official docs were re-checked on 2026-03-08 against vendor documentation.
- Local runtime checks used:
  - hash match for repo-owned settings and MCP files
  - existence/absence checks for default runtime surfaces and compatibility-only directories
  - retention check for an existing `.cursor/agents/` compatibility surface
  - link-target check for `.claude/agents`
  - unmanaged-local-file awareness for `.claude/settings.local.json` as a local-only ignored override

## Residual migration watch items

- Cursor: keep `.cursorrules` as a loader stub only, preserve existing `.cursor/agents/` when present, and keep `.cursor/rules/` out of the default bootstrap path.
- Claude Code: `.claude/commands/` remains compatibility-only for older setups.
- Codex: do not treat `~/.codex/skills` as the current official user-scope contract.
