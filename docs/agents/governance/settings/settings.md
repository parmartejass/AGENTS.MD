---
doc_type: policy
ssot_owner: docs/agents/governance/settings/settings.md
update_trigger: shared platform settings baseline or platform settings facts change
---

# Settings

Jurisdiction: repo-owned shared platform settings payloads.

## Baseline
```yaml
baseline:
  interface: "each platform's native project settings file, read directly by that platform: .claude/settings.json, .codex/config.toml, .cursor/cli.json"
  pattern: "one canonical source payload per platform under this jurisdiction, byte-identical to the file the platform reads at its discovery path, installed by the consumer"
  reason: "the platform reads its own file with no generation step; a transformed payload is a wrapper that drifts from what actually applies"
  exception: none
```

## Payloads
- Compaction or summary instructions MUST preserve controlling user intent.
- Every key in a committed payload MUST exist at that scope in the platform's current published configuration reference.
- A control that must apply before the folder is trusted MUST be `deny` or `ask`; `allow` applies only after trust.
- Runtime copies of settings are not authorities.
