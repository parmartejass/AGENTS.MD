---
doc_type: policy
ssot_owner: docs/agents/mcp/00-mcp-standards/mcp-standards.md
update_trigger: MCP source assets, supported platforms, or config-shape rules change
---

# MCP Standards (SSOT)

`AGENTS.md` owns the Fundamental Principles, including interface selection, discovery, authorization, and explicit outcomes. This file owns MCP source placement and payload boundaries only.

## Definition
- Non-secret MCP configuration owned by this repo lives under `docs/agents/mcp/`.

## Invariants
- Store only non-secret server definitions here; inject secrets at runtime through environment variables or platform-local secret stores.
- Validate MCP JSON before consuming it as a source asset.
- Use one canonical repo source file for shared MCP payloads; do not maintain parallel tracked copies under project dot-folders.
- Platform resolution and unsupported outcomes MUST follow the consuming runtime's verified contract under `AGENTS.md` FP-18 and FP-20.
- Repo-owned MCP server definitions must not grant implicit tool-execution permissions; each tool's permission scope is enforced by the consuming client runtime, not by the server definition.
- Runtime installation is consumer-owned; this repo no longer tracks root runtime copies or projection mappings.

## Source routes
- Shared MCP config source: `docs/agents/mcp/shared/mcp.json`
- A platform branch owner may place a distinct non-secret payload under `docs/agents/mcp/<platform>/mcp.json` when the verified platform contract requires it; its router and parsed payload witness the source boundary.
- Codex shared project config, including any intentionally shared MCP settings, is owned through `docs/agents/settings/codex/config.toml`.
- User-local or secret Codex state remains outside repo-owned MCP authority.
