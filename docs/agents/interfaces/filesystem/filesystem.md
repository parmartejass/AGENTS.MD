---
doc_type: policy
ssot_owner: docs/agents/interfaces/filesystem/filesystem.md
update_trigger: filesystem interface baseline or write-safety platform facts change
---

# Filesystem

Jurisdiction: direct filesystem operations, destination safety, and write durability.

## Baseline
```yaml
baseline:
  interface: direct filesystem operations with validated paths and atomic replace
  pattern: "a destination holds the complete prior or complete new content at every instant, durably; per-item terminal outcome"
  reason: "rename atomicity and write durability are separate guarantees from separate calls; wrappers hide one of the two"
  exception: platform APIs only for a recorded capability gap
```

## Writes
- Validation MUST complete without side effects before the first write.
- Promotion MUST NOT follow or replace a symlink or reparse point, or replace a directory.
- Cross-volume promotion is non-atomic.
- On Windows, a replace can fail transiently with a sharing violation while another process holds the file.
- A production artifact MUST be updated at its authoritative path, never a copy.
- A failed or interrupted commit MUST leave the original destination intact.
