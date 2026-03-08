# Nia Setup for Claude Code, Cursor, and Codex

Saved and re-verified: 2026-03-08

This guide records the current official user/global Nia setup paths for personal client installs.
It is not the SSOT for this repo's managed runtime projections.

## Repo authority boundary

- Repo-managed runtime paths and support levels are owned by `docs/agents/platforms/runtime-projections.json`.
- This repo intentionally keeps its canonical reusable assets under `docs/agents/` and projects supported repo-scoped runtime views from there.
- User/global Nia setup is optional personal baseline setup. It does not replace the repo-scoped projection model for tracked shared assets.

## Recommended baseline

- Prefer Nia Remote MCP over the local server. Nia's official docs still recommend the remote server path.
- Keep secrets out of tracked repo files.
- Treat the commands and filenames below as a verified snapshot as of 2026-03-08. Re-check the linked official docs before changing the repo SSOT.

## Claude Code

Official docs: https://docs.trynia.ai/integrations/installation/mcp

User/global remote MCP install:

```bash
claude mcp add --transport http --header "Authorization: Bearer YOUR_API_KEY" --scope user nia "https://apigcp.trynia.ai/mcp"
```

Notes:
- Nia documents `--scope user` as the all-projects option.
- Repo-scoped Claude assets in this repo remain governed by `docs/agents/platforms/runtime-projections.json` and `scripts/setup_repo_platform_assets.ps1`.

## Cursor

Official docs: https://docs.trynia.ai/integrations/installation/mcp

User/global MCP config paths:
- Windows: `%APPDATA%\\Cursor\\mcp.json`
- macOS: `~/.cursor/mcp.json`
- Linux: `~/.config/cursor/mcp.json`

Example user/global entry:

```json
{
  "mcpServers": {
    "nia": {
      "url": "https://apigcp.trynia.ai/mcp",
      "headers": {
        "Authorization": "Bearer YOUR_API_KEY"
      }
    }
  }
}
```

Notes:
- Keep this secret in user-owned config only.
- Repo-scoped Cursor assets in this repo remain governed by `docs/agents/platforms/runtime-projections.json`.

## Codex

Official docs:
- https://developers.openai.com/codex/mcp
- https://docs.trynia.ai/integrations/installation/mcp

User/global config path:
- `~/.codex/config.toml`

Preferred env-backed config:

```toml
[mcp_servers.nia]
url = "https://apigcp.trynia.ai/mcp"
bearer_token_env_var = "NIA_API_KEY"
```

Notes:
- OpenAI documents shared CLI/IDE config in `~/.codex/config.toml`.
- OpenAI also documents env-backed bearer-token support for HTTP MCP servers.
- This repo still uses project-scoped repo-owned `docs/agents/` assets for shared runtime projections when they are intentionally managed.

## Make Nia more automatic

Official docs: https://docs.trynia.ai/example-workflows/agent-rules

Nia's official guide still describes user/runtime rule or prompt installs such as:
- Claude: `.claude/agents/nia-oracle.md`
- Codex: `.codex/prompts/nia-oracle.md`
- Cursor: `.cursor/rules/nia-oracle.mdc`

Treat those as personal runtime artifacts, not repo-owned authorities.

## Cross-device reality check

Remote MCP remains the lowest-maintenance setup, but it is not zero setup on a new device. You still need:
- the client installed
- the user/global MCP config added where you want personal reuse
- the API key available to that client
- any user-level Nia rule/prompt files copied if you want more automatic behavior

Repo-managed shared runtime projections are still rebuilt from `docs/agents/` with `scripts/setup_repo_platform_assets.ps1`.