---
doc_type: reference
ssot_owner: docs/agents/platforms/runtime-projections.json
update_trigger: official MCP spec or client-configuration guidance changes
---

# MCP Runtime Contract (Retrieved 2026-03-06, re-verified 2026-03-08)

## Sources

- https://modelcontextprotocol.io/docs/getting-started/intro
- https://modelcontextprotocol.io/introduction

## Repo-relevant facts

- MCP is a client/server contract, not a single config format.
- Client-specific configuration belongs to the client runtime surface, so this repo keeps canonical non-secret server definitions under `docs/agents/mcp/` and projects them into client-specific files.
- Client-specific mixed user settings must remain manual if the config file also stores unrelated local state.

## Repo decision

- Keep canonical non-secret MCP JSON in `docs/agents/mcp/`.
- Project only pure repo-scoped MCP files automatically.
- Treat mixed config files as manual/snippet-only surfaces.
