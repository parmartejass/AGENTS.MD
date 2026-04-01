---
doc_type: policy
ssot_owner: docs/agents/mcp/00-mcp-standards/mcp-standards.md
update_trigger: MCP runtime paths, supported platforms, or config-shape rules change
---

# MCP Standards (SSOT)

## Definition
- Non-secret MCP configuration owned by this repo lives under `docs/agents/mcp/`.
- Shared MCP JSON can live under `docs/agents/mcp/shared/mcp.json`.
- Platform-specific overrides can live under `docs/agents/mcp/<platform>/mcp.json`.

## Invariants
- Store only non-secret server definitions here; inject secrets at runtime through environment variables or platform-local secret stores.
- Validate MCP JSON before linking it into runtime locations.
- Use one canonical repo file per runtime target; do not maintain parallel copies under project dot-folders.
- Unsupported platforms must be skipped explicitly.
- Repo-owned MCP server definitions must not grant implicit tool-execution permissions; each tool's permission scope is enforced by the consuming client runtime, not by the server definition.
- Exact client/runtime mappings and support levels live in `docs/agents/platforms/runtime-projections.json`.

## Supported mappings
- Cursor project MCP config: `docs/agents/mcp/{cursor|shared}/mcp.json` -> `.cursor/mcp.json`
- Claude Code project MCP config: `docs/agents/mcp/{claude|shared}/mcp.json` -> `.mcp.json`
- Codex does not use a separate repo-owned MCP JSON target in this asset class.
- Shared project-local Codex config, including any intentionally shared MCP settings, is owned through `docs/agents/settings/codex/config.toml` -> `.codex/config.toml`.
- User-local or secret Codex state remains outside repo-owned MCP authority.
