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
- Local witness: repo loader stubs are governed by `AGENTS.md`/`CLAUDE.md`; runtime target mapping and retired/local-only projection decisions are routed to `docs/agents/platforms/runtime-projections.json` and the dated Cursor evidence note.
- Migration note: existing tracked Cursor agent files are runtime guidance records, not runtime projection owners.

### Claude Code

- Status: connected and migrated to the current official skill surface.
- Local witness: `CLAUDE.md` routes back to `AGENTS.md`; runtime target mapping and retired/local-only projection decisions are routed to `docs/agents/platforms/runtime-projections.json` and the dated Claude Code evidence note.
- Migration note: local retired runtime surfaces, if present from older checkouts, are not canonical source roots.

### Codex

- Status: connected and aligned with current official docs.
- Local witness: runtime target mapping, source-root decisions, and user-home/project-local projection scope are routed to `docs/agents/platforms/runtime-projections.json` and the dated Codex evidence note.
- Migration note: Codex subagent role adapters are not canonical source roots; canonical agent instructions remain in `AGENTS.md`.

## Verification method

- Official docs were re-checked on 2026-03-08 against vendor documentation.
- Local runtime checks used:
  - hash match for repo-owned settings and MCP files
  - existence/absence checks for runtime surfaces declared by the runtime projection owner
  - unmanaged-local-file awareness for `.claude/settings.local.json` as a local-only ignored override

## Residual migration watch items

- Re-check dated external evidence before changing runtime projection support levels or target mappings.
- Keep local status/witness records here; route concrete projection facts to `docs/agents/platforms/runtime-projections.json`.
