---
doc_type: policy
ssot_owner: docs/agents/governance/dependencies/dependencies.md
update_trigger: dependency admission, lockfile, upgrade cooldown, or vulnerability-scan rules change
---

# Dependencies

Jurisdiction: how third-party code is admitted, pinned, installed, upgraded, and scanned.

```yaml
baseline:
  interface: "the committed lockfile with resolved versions and per-artifact hashes (pylock.toml where the tool supports it)"
  pattern: "declared direct dependencies; resolved hashed lockfile; frozen install; vulnerability scan in checks; cooldown-gated upgrade"
  reason: "the lockfile is the only artifact that fixes the exact installed tree and hashes are the only check that the bytes match the resolution; it avoids range-resolved installs that differ per machine and per day"
  exception: "a Recorded security upgrade may bypass the cooldown window"
```

## Admission
- A dependency MUST NOT be added for functionality the standard library provides; a new direct dependency MUST Record the baseline it supersedes, the capability gap, its license class, and the owner that consumes it.
- A new direct dependency MUST be checked for name confusion against the intended project before first install.
- A runtime import of a package absent from the lockfile is Prohibited.

## Lockfile
- Every runtime and development dependency MUST appear in the committed lockfile with per-artifact hashes.
- Installs in checks, builds, and releases MUST be frozen against the lockfile; resolving at install time is Prohibited.
- The lockfile MUST be regenerated in the same change as any dependency edit, including removal; a drifted lockfile MUST fail a repository check.

## Upgrade and scan
- A dependency upgrade MUST observe the declared cooldown window; a fix for a known vulnerability bypasses it with the advisory identifier Recorded.
- Prohibited: relying on a vulnerability scanner as the malicious-package control; Record the separate provenance check.
