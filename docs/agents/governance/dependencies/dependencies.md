---
doc_type: policy
ssot_owner: docs/agents/governance/dependencies/dependencies.md
update_trigger: the lockfile or frozen-install rule changes
---

# Dependencies

Jurisdiction: how third-party code is pinned and installed.

```yaml
baseline:
  interface: "the committed lockfile with resolved versions and per-artifact hashes (pylock.toml where the tool supports it)"
  pattern: "declared direct dependencies; hashed lockfile; frozen install"
  reason: "the lockfile is the only artifact that fixes the exact installed tree and hashes are the only check that the bytes match the resolution; it avoids range-resolved installs that differ per machine and per day"
  exception: none
```

- MUST install only the hash-verified dependency set in the committed lockfile, updated in the same change as any dependency edit.
