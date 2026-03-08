---
doc_type: policy
ssot_owner: docs/agents/mcp/00-mcp-standards.md
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
- Exact client/runtime mappings and support levels live in `docs/agents/platforms/runtime-projections.json`.

## Supported mappings
- Cursor project MCP config: `docs/agents/mcp/{cursor|shared}/mcp.json` -> `.cursor/mcp.json`
- Claude Code project MCP config: `docs/agents/mcp/{claude|shared}/mcp.json` -> `.mcp.json`
- Codex MCP setup remains manual because the official surface is a mixed `config.toml` file rather than a pure repo-owned MCP JSON target.
