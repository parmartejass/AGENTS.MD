---
doc_type: reference
ssot_owner: docs/agents/platforms/runtime-projections.json
update_trigger: Claude Code runtime docs, command/agent paths, or settings/MCP rules change
---

# Claude Code Runtime Contract (Retrieved 2026-03-06, repo decision re-verified 2026-05-08)

## Sources

- https://docs.anthropic.com/en/docs/claude-code/common-workflows
- https://docs.anthropic.com/en/docs/claude-code/settings
- https://docs.anthropic.com/en/docs/claude-code/slash-commands
- https://docs.anthropic.com/en/docs/claude-code/sub-agents
- https://docs.anthropic.com/en/docs/claude-code/mcp

## Repo-relevant facts

- Shared project settings live in `.claude/settings.json`; local machine overrides belong in `.claude/settings.local.json`.
- Project subagents live under `.claude/agents`.
- Claude project MCP config lives at `.mcp.json`.
- Claude now documents official project skills at `.claude/skills/<skill-name>/SKILL.md`.
- Existing `.claude/commands/*.md` files still work, but the current docs say skills are the recommended surface.
- Claude Code auto mode uses built-in classifiers to make per-action permission decisions instead of prompting the user or skipping permissions entirely; repo settings may define allow/deny lists that auto mode respects.

## Repo decision

- Canonical repo-owned skill bundles remain under `docs/agents/skills/`.
- Auto-project official project-local Claude skills into `.claude/skills/`.
- Historical note: older repo decisions kept generated `.claude/commands/` adapters for command-file environments. Current runtime mapping is owned by `docs/agents/platforms/runtime-projections.json`, which no longer projects generated command adapters.
- Do not auto-project Claude project subagents; canonical agent instructions remain in `AGENTS.md` and context routing remains in `agents-manifest.yaml`.
- `.mcp.json` remains repo-owned through the canonical MCP config.
- Keep shared non-secret Claude settings repo-owned in `.claude/settings.json`, while `.claude/settings.local.json` remains local-only.
