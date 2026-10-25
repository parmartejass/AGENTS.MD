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
- MUST use the standard library, not a new dependency, for functionality it provides.
- A new direct dependency MUST record the baseline it supersedes, the capability gap, its license class and the owner that consumes it.
- A new direct dependency MUST be checked for name confusion against the intended project before first install.
- Every runtime import MUST resolve to a package in the lockfile.

## Lockfile
- Every runtime and development dependency MUST appear in the committed lockfile with per-artifact hashes.
- Installs in checks, builds and releases MUST be frozen against the lockfile.
- Prohibited: resolving at install time.
- The lockfile MUST be regenerated in the same change as any dependency edit, including removal.
- A drifted lockfile MUST fail a repository check.

## Upgrade and scan
- A dependency upgrade MUST observe the declared cooldown window.
- A fix for a known vulnerability bypasses the window, with its advisory identifier recorded.
- The malicious-package control MUST be a separate provenance check, not the vulnerability scanner.
- Record that provenance check.
