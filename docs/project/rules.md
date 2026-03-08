---
doc_type: policy
ssot_owner: AGENTS.md
update_trigger: governance rules change OR new recurring maintenance pitfalls emerge
---

# Rules (Do / Don't)

## Governance (authoritative)
- Follow `AGENTS.md` (do not duplicate its rules here).

## Do
- Keep templates as reference implementations (patterns, not specs).
- Keep checks deterministic and dependency-minimal.
- Keep reusable agent assets under `docs/agents/` and regenerate external discovery paths from that authority.
- For repository, documentation, package, Slack, or research-discovery tasks covered by the Nia skill, prefer `docs/agents/skills/nia/SKILL.md` before generic web search.
- When a repo-integrated skill such as Nia is relevant, verify repo-local credential sources before declaring the integration unavailable in the current shell.

## Don't
- Don't add repo-generated artifacts to git (bytecode, caches, template outputs).
- Don't expand docs into a second SSOT; reference owners by path/identifier instead.
- Don't treat a missing process environment variable alone as proof that Nia is not configured for this repo.
- Don't silently fall back from Nia to generic web/search flows without stating why the Nia path was unavailable.
- Don't edit runtime projection paths like `.agents/skills/*`, `.cursor/rules/*`, `.cursor/skills/*`, `.cursor/agents/*`, `.cursor/mcp.json`, `.cursor/cli.json`, `.claude/commands/*`, `.claude/skills/*`, `.claude/agents/*`, `.claude/settings.json`, `.codex/agents/*`, `.codex/config.toml`, or `.mcp.json` as standalone copies when they are repo-linked or generated views of `docs/agents/`.
