---
doc_type: policy
ssot_owner: docs/agents/subagents/00-subagent-standards.md
update_trigger: subagent runtime paths, supported platforms, or linker behavior change
---

# Subagent Standards (SSOT)

## Definition
- Reusable subagent definitions live under `docs/agents/subagents/`.
- The current reusable reviewer prompt set lives under `docs/agents/subagents/shared/`.
- Only non-secret, reusable instructions belong here.

## Invariants
- Keep one canonical repo copy per subagent file; runtime locations are linked projections only.
- Preserve each platform's native file format; do not force shared schemas when platform contracts differ.
- Exclude credentials, tokens, cookies, and other critical security material from subagent files.
- Unsupported or unverified runtime mappings must be skipped explicitly by the linker.
- Exact runtime mappings and support levels live in `docs/agents/platforms/runtime-projections.json`.

## Supported mappings
- Claude Code project subagents: `docs/agents/subagents/shared/` -> `.claude/agents/`
- Codex project subagents: `docs/agents/subagents/codex/` -> `.codex/agents/` (TOML role adapters; canonical prompt intent remains in `docs/agents/subagents/shared/`).
- Cursor `.cursor/agents/` is compatibility-only until a verified official Cursor subagent runtime contract is adopted.

## Operating rules
- Use `docs/agents/link_repo_assets.ps1` for install/update instead of editing runtime projection folders directly.
- Generated or linked runtime targets must fail closed when a conflicting user-owned file is already present.
- If a platform changes its subagent format or path rules, update this file and the linker together.
