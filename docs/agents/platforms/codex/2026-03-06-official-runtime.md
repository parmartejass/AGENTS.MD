---
doc_type: reference
ssot_owner: docs/agents/platforms/runtime-projections.json
update_trigger: Codex runtime docs, skill paths, or config rules change
---

# Codex Runtime Contract (Retrieved 2026-03-06, re-verified 2026-03-08)

## Sources

- https://developers.openai.com/codex/skills
- https://developers.openai.com/codex/mcp
- https://developers.openai.com/codex/cli

## Repo-relevant facts

- Codex scans repository skills from `.agents/skills` between the current working directory and repo root, plus user `$HOME/.agents/skills` and admin `/etc/codex/skills`.
- The current repo should prefer the official project-local skills path because it is portable with the repo and does not leak repo-specific skills into unrelated projects.
- Codex stores shared CLI/IDE configuration in `config.toml`; default user path is `~/.codex/config.toml`, and trusted projects can use `.codex/config.toml`.
- Codex supports multi-agent role declarations in `config.toml` via `[agents]` and `[agents.<role>]` tables, and each role can load developer instructions from a relative `config_file` path.
- Codex MCP HTTP servers support `bearer_token_env_var` and `env_http_headers`, which makes env-backed secret handling the preferred remote-MCP pattern.
- `AGENTS.md` remains the repo-owned instruction authority; Codex runtime surfaces are adapters, not competing policy stores.

## Repo decision

- Auto-project official project-local Codex skills into `.agents/skills/`.
- Auto-project a repo-owned project `.codex/config.toml` only for explicitly shared, non-secret project settings.
- Auto-project official project-local Codex subagent TOML role adapters from `docs/agents/subagents/codex/` into `.codex/agents/`, with `multi_agent` enabled in project config.
- Do not auto-project user-home Codex skills by default; current official docs use `$HOME/.agents/skills` for user-scoped skills, but this repo keeps user-home paths manual.
