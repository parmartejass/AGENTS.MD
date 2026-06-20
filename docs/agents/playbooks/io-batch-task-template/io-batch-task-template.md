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
- if bugfix/regression: fill `docs/agents/playbooks/bugfix-template/bugfix-template.md`.
- if feature/behavior change: satisfy `AGENTS.md` "Verification Floors (Hard Gate)" behavior-change/new-feature minimums (including shift-left baseline).
- if refactor/behavior-neutral: satisfy `AGENTS.md` "Verification Floors (Hard Gate)" behavior-neutral minimums.
- if new logic is introduced: apply `docs/agents/35-coding-principles/coding-principles.md` under the `AGENTS.md` coding hard gate.

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
- rules/validators owner (business rules and checkbox/config predicates):
- workflow/runner owner (runtime coordinator only):
- run outcomes/report owner:

## Data integrity plan
- Follow `docs/agents/70-io-data-integrity/io-data-integrity.md` (transactional writes, validate paths early, run outcomes).
- Overwrite/replace strategy (temp + atomic replace; backups if required):
- Idempotency strategy (what happens on re-run):
- Failure behavior (partial outputs, cleanup, logged reason):

## Performance & throughput plan (when relevant)
- No safety/correctness trade-offs.
- Bottleneck hypothesis (disk/network/parse/serialize/CPU):
- Safe levers (pick the minimal set that applies):
  - Stream/chunk processing with bounded memory.
  - Avoid repeated directory scans and full-file re-reads; cache parsed metadata/lookups with cache key/scope, max size, and invalidation.
  - Batch small writes (buffered I/O); avoid per-record filesystem operations.
  - Prefer linear-time data structures (hash maps/sets) over nested loops for joins/dedup.
  - Queue/batch work with backpressure/coalescing when needed; concurrency only when safe: bounded workers, deterministic output rules, and cancellation-aware cleanup.
- Evidence plan (how timing/complexity is verified deterministically):

## Proof obligations (first principles)
- preconditions (required input paths, permissions, schemas/headers):
- postconditions (artifacts produced, no partial corruption, cleanup complete):
- failure modes (what fails, how it is logged, what is left on disk):

## Acceptance checks
- run outcomes recorded (EXECUTED/SKIPPED + reason):
- known work counts reconcile planned/eligible/executed/skipped/failed:
- logs present with paths + counts:
- user-facing summary includes input/scope, progress/current phase for long work, terminal result, output path, reason/action, and log/report pointer:
- at least one failure-path check executed (e.g., missing input, invalid schema):
- verification commands come from README.md "Checks":
