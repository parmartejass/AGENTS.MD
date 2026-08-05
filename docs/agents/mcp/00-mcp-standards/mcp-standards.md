---
doc_type: policy
ssot_owner: docs/agents/mcp/00-mcp-standards/mcp-standards.md
update_trigger: MCP source assets, supported platforms, or config-shape rules change
---

# MCP Standards (SSOT)

## Definition
- Non-secret MCP configuration owned by this repo lives under `docs/agents/mcp/`.
- Shared MCP JSON can live under `docs/agents/mcp/shared/mcp.json`.
- Platform-specific overrides can live under `docs/agents/mcp/<platform>/mcp.json`.

## Invariants
- Store only non-secret server definitions here; inject secrets at runtime through environment variables or platform-local secret stores.
- Validate MCP JSON before consuming it as a source asset.
- Use one canonical repo source file for shared MCP payloads; do not maintain parallel tracked copies under project dot-folders.
- Unsupported platforms must be skipped explicitly.
- Repo-owned MCP server definitions must not grant implicit tool-execution permissions; each tool's permission scope is enforced by the consuming client runtime, not by the server definition.
- Runtime installation is consumer-owned; this repo no longer tracks root runtime copies or projection mappings.

## Supported source assets
- Shared MCP config source: `docs/agents/mcp/shared/mcp.json`
- Platform-specific MCP config sources may live under `docs/agents/mcp/<platform>/mcp.json` when the platform branch owns a distinct non-secret payload.
- Codex shared project config, including any intentionally shared MCP settings, is owned through `docs/agents/settings/codex/config.toml`.
- User-local or secret Codex state remains outside repo-owned MCP authority.
