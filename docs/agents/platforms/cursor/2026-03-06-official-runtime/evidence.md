---
doc_type: reference
ssot_owner: docs/agents/platforms/runtime-projections.json
update_trigger: Cursor runtime docs, rule paths, or MCP/config rules change
---

# Cursor Runtime Contract (Retrieved 2026-03-06, repo decision re-verified 2026-05-08)

## Sources

- https://docs.cursor.com/en/context/rules
- https://docs.cursor.com/en/context/mcp
- https://docs.cursor.com/en/cli/reference/configuration
- https://docs.cursor.com/cli/mcp

## Repo-relevant facts

- Cursor project rules live under `.cursor/rules`.
- `.cursorrules` is still supported, but Cursor documents it as legacy/deprecated in favor of project rules.
- Cursor project MCP config lives at `.cursor/mcp.json`.
- Cursor CLI uses the same MCP config as the editor.
- Cursor project CLI permissions can live at `<project>/.cursor/cli.json`; other CLI settings stay global.
- No verified official repo-owned Cursor `skills` directory or `.cursor/agents` directory is currently documented in the fetched official docs.

## Repo decision

- Do not keep root `.cursorrules` as a repo-owned loader stub; repo loader stubs are `AGENTS.md` and `CLAUDE.md`.
- Treat repo-owned `.cursor/rules/` adapters as compatibility-only projections; generate them only when compatibility bootstrap is explicitly requested.
- Keep `.cursor/mcp.json` repo-owned through the canonical MCP config.
- Keep shared repo-owned Cursor CLI permissions in `.cursor/cli.json` when the repo intentionally defines a non-secret shared policy.
- Treat `.cursor/skills`, `.cursor/agents`, and `.cursor/rules` as outside the default bootstrap path unless a future verified runtime contract adopts them.
