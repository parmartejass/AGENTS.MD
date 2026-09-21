---
doc_type: policy
ssot_owner: docs/agents/governance/settings/settings.md
update_trigger: shared settings owners or local-override rules change
---

# Settings

Jurisdiction: repo-owned shared platform settings placement, source boundaries, and local-override limits.

## Baseline
```yaml
baseline:
  interface: "each platform's native project settings file, read directly by that platform: .claude/settings.json, .codex/config.toml, .cursor/cli.json"
  pattern: "one canonical source payload per platform under this jurisdiction, byte-identical to the file the platform reads at its discovery path, installed by the consumer; secrets by environment reference only"
  reason: "the platform reads its own file with no generation step; a transformed payload is a wrapper that drifts from what actually applies"
  exception: none
```

## Definition
- Repo-owned shared platform settings MUST live under `docs/agents/governance/settings/`.
- Canonical settings MUST be direct source files, not payloads embedded in docs or scripts.

## Invariants
- Shared settings payloads are source assets only.
- Instruction-bearing settings MUST route policy to its owner and MUST NOT copy or redefine it.
- Shared settings content MUST stay machine-parseable when the format supports deterministic parsing.
- Every key in a committed platform payload MUST exist at that scope in the platform's current published configuration reference.
- A control that must apply before the consumer trusts the folder MUST be expressed as `deny` or `ask`; `allow` entries apply only after trust.

## Current shared source routes
- Cursor project CLI permissions: `docs/agents/governance/settings/cursor/cli.json`
- Claude shared project settings: `docs/agents/governance/settings/claude-code/settings.json`
- Codex shared project config: `docs/agents/governance/settings/codex/config.toml`

## Local-only boundary
- `.claude/settings.local.json` is machine-local; repo-linking or tracking it is Prohibited.
- User-home config files stay outside repo ownership absent a future verified adopting contract.

## Editing rule
- Edit canonical settings under `docs/agents/governance/settings/**`.
- Consumer runtime settings files MUST NOT be treated as repo-owned authorities.
- A platform settings source contract change MUST update this owner and the affected payload branch together.
