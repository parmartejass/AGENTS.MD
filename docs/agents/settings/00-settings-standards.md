---
doc_type: policy
ssot_owner: docs/agents/settings/00-settings-standards.md
update_trigger: shared settings owners, runtime paths, or local-override rules change
---

# Settings Standards (SSOT)

## Definition
- Repo-owned shared platform settings live under `docs/agents/settings/`.
- Canonical settings files must be direct source files, not embedded payloads in docs or scripts.
- Exact runtime mappings and support levels live in `docs/agents/platforms/runtime-projections.json`.

## Invariants
- Only project-scoped, non-secret, intentionally shared settings may be repo-owned.
- Runtime settings targets are linked projections of canonical repo files.
- Machine-local override files remain user-owned and unmanaged.
- Settings automation must fail closed on conflicting non-link targets.
- Shared settings content must be validated before linking when the file format is machine-parseable.

## Supported shared settings
- Cursor project CLI permissions: `docs/agents/settings/cursor/cli.json` -> `.cursor/cli.json`
- Claude shared project settings: `docs/agents/settings/claude-code/settings.json` -> `.claude/settings.json`
- Codex shared project config: `docs/agents/settings/codex/config.toml` -> `.codex/config.toml`

## Local-only boundary
- `.claude/settings.local.json` is machine-local and must never be repo-linked or tracked.
- User-home config files remain outside repo-owned projection scope unless a future verified contract explicitly adopts them.

## Editing rule
- Edit canonical settings under `docs/agents/settings/**`.
- Do not edit projected runtime settings files as standalone authorities.
- If a platform settings contract changes, update this file, `docs/agents/platforms/runtime-projections.json`, the relevant dated platform note, and `docs/agents/link_repo_assets.ps1` together.
