---
doc_type: playbook
ssot_owner: AGENTS.md
update_trigger: I/O performance, integrity, or run-outcome expectations change
---

# Playbook — High I/O / Batch Processing Task

Use when:
- Task matches profile `io_batch` in `agents-manifest.yaml`.

## Change classification (required)
- task type (feature|bugfix|refactor):
- blast radius (datasets/workflows/users):
- if bugfix/regression: fill `docs/agents/playbooks/bugfix-template.md` and satisfy `AGENTS.md` "Bias-Resistant Debugging (Hard Gate)".
- if behavior change/new feature: satisfy `AGENTS.md` "Verification Floors (Hard Gate)" shift-left baseline.
- if refactor/behavior-neutral change: satisfy `AGENTS.md` "Verification Floors (Hard Gate)" behavior-neutral minimums.
- if new logic is introduced: apply `AGENTS.md` Non-Negotiable 11 "Mandatory Modularity + SOLID/DI (Authority Bloat Prevention)".

## Inputs
- input formats (csv/json/jsonl/parquet/etc):
- input locations (paths/globs):
- expected size (files, rows, bytes):
- ordering/dedup requirements:

## Outputs
- output artifacts:
- overwrite policy (append/replace/transactional):
- run report location:

## SSOT mapping (fill with exact repo locations)
- constants owner:
- config owner:
- rules/validators owner:
- workflow/runner owner:
- run outcomes/report owner:

## Data integrity plan
- Follow `docs/agents/70-io-data-integrity.md` (transactional writes, validate paths early, run outcomes).
- Overwrite/replace strategy (temp + atomic replace; backups if required):
- Idempotency strategy (what happens on re-run):
- Failure behavior (partial outputs, cleanup, logged reason):

## Performance & throughput plan (when relevant)
- Follow `AGENTS.md` "Performance & Speed (When Relevant)" (no safety/correctness trade-offs).
- Bottleneck hypothesis (disk/network/parse/serialize/CPU):
- Safe levers (pick the minimal set that applies):
  - Stream/chunk processing with bounded memory.
  - Avoid repeated directory scans and full-file re-reads; cache parsed metadata/lookups and define invalidation.
  - Batch small writes (buffered I/O); avoid per-record filesystem operations.
  - Prefer linear-time data structures (hash maps/sets) over nested loops for joins/dedup.
  - Concurrency only when safe: bounded workers, deterministic output rules, and cancellation-aware cleanup.
- Evidence plan (how timing/complexity is verified deterministically):

## Proof obligations (first principles)
- preconditions (required input paths, permissions, schemas/headers):
- postconditions (artifacts produced, no partial corruption, cleanup complete):
- failure modes (what fails, how it is logged, what is left on disk):

## Acceptance checks
- run outcomes recorded (EXECUTED/SKIPPED + reason):
- logs present with paths + counts:
- at least one failure-path check executed (e.g., missing input, invalid schema):
- verification commands come from README.md "Checks":
