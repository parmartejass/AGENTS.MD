---
doc_type: policy
ssot_owner: docs/agents/interfaces/filesystem/filesystem.md
update_trigger: file handling, path validation, or write-commit constraints change
---

# Filesystem

Jurisdiction: direct filesystem operations, path and destination validation, and the write state machine with two-phase commit.

## Baseline
```yaml
baseline:
  interface: direct filesystem operations with validated paths and atomic replace
  pattern: "two-phase commit: side-effect-free validation, temp file in the destination directory, flush and fsync before promotion, same-volume atomic replace, bounded retry on transient sharing violation, cleanup in finally, per-item terminal outcome"
  reason: "rename atomicity and write durability are separate guarantees from separate calls; every write effect stays visible to the two-phase commit, and wrappers hide one of the two"
  exception: platform APIs only for a recorded capability gap
```

## File handling rules
- Paths MUST be validated early.
- Overwrite and move workflows MUST validate the destination as a regular file or absent, never a directory, symlink, or reparse point, at the full promotion path length including the temp suffix.
- Promotion MUST write to a temporary location and replace the destination atomically.
- Cross-volume promotion is non-atomic and MUST be Recorded with its own completion witness.
- Each promoted item MUST Return its own terminal outcome.
- A production artifact MUST be updated at its declared authoritative path; a copy is a verification input only and MUST NOT be the update destination.

## Implementation Write State Machine + Two-Phase Commit
- Scope: transactional implementation and write safety when repository or external writes occur.
- Required phases: INIT, VALIDATED, COMMIT_READY, COMMITTING, CLEANING, DONE.
- Failure phases: FAILED_VALIDATION, FAILED_COMMIT, FAILED_CLEANUP.
- Validation MUST be side-effect free; writes before VALIDATED are prohibited.
- On any failure after writes begin, Record FAILED_COMMIT, log what was written, and attempt bounded cleanup in `finally`.

## Recovery
- Recovery MUST be preserved until the owner-declared commit witness passes.
- A failed or interrupted commit MUST leave the original destination recoverable and Record the explicit commit failure.
- Temporary artifacts MUST be removed in `finally`; a removal failure is recorded as `FAILED_CLEANUP`.
