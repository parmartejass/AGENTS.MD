---
doc_type: policy
ssot_owner: docs/agents/settings/00-settings-standards/settings-standards.md
update_trigger: shared settings owners or local-override rules change
---

# Settings Standards (SSOT)

## Definition
- Repo-owned shared platform settings live under `docs/agents/settings/`.
- Canonical settings files must be direct source files, not embedded payloads in docs or scripts.
- Runtime installation is consumer-owned; this repo no longer tracks root runtime copies or projection mappings.

## Invariants
- Only project-scoped, non-secret, intentionally shared settings may be repo-owned.
- Shared settings payloads are source assets only.
- Machine-local override files remain user-owned and unmanaged.
- Shared settings content must remain machine-parseable when the file format supports deterministic parsing.

## Supported shared settings
- Cursor project CLI permissions source: `docs/agents/settings/cursor/cli.json`
- Claude shared project settings source: `docs/agents/settings/claude-code/settings.json`
- Codex shared project config source: `docs/agents/settings/codex/config.toml`

## Local-only boundary
- `.claude/settings.local.json` is machine-local and must never be repo-linked or tracked.
- User-home config files remain outside repo ownership unless a future verified contract explicitly adopts them.

## Editing rule
- Edit canonical settings under `docs/agents/settings/**`.
- Do not treat consumer runtime settings files as repo-owned authorities.
- If a platform settings source contract changes, update this file and the affected source payload branch together.
