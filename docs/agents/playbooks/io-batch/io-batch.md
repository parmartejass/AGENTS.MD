---
doc_type: playbook
ssot_owner: docs/agents/playbooks/io-batch/io-batch.md
update_trigger: transformation authorization, bounded processing, or aggregation and merge integrity rules change
---

# I/O Batch Processing

Jurisdiction: transformation authorization evidence, bounded processing, aggregation and merge integrity, and the batch task scaffold.

```yaml
baseline:
  interface: streaming or chunked processing over validated bounded inputs with keyed lookups
  pattern: "validate first, bounded chunks, deterministic idempotency key per unit of work, durable checkpoint, deterministic output order on a declared total-order key, per-item terminal outcome, reconciled counts"
  reason: bounded memory and deterministic order keep large runs verifiable; unbounded loads and ad hoc merges hide corruption
  exception: "a full in-memory load only when the input bound is validated as small and enforced before the read, recorded as one supersession"
```

## Transformation authorization evidence
- Record the declared transformation contract before mutation, repair, normalization, or row/field removal.
- Record affected source identities, authorized value changes, and the preservation witness.
- Unresolved values and unknown inputs MUST retain their originals.
- Route resolution and its explicit outcome through the owning input, schema, config, or rule contract.
- An apparent data defect is not transformation authorization.

## Bounded processing rules
- Read and cache only validated required data ranges and lookups.
- Record bounds, counts, cache scope, and invalidation trigger when caching affects correctness.
- Batch, chunk, and queue processing MUST declare memory bounds, concurrency limits, deterministic output ordering, timeout/cancellation behavior, and cleanup behavior; a queue bound reached MUST block or Record an explicit drop.
- Prohibited: optimizing by dropping validation, skipping real-data or domain checks, or hardcoding ranges owned by input/schema/config authorities.

## Aggregation and merge integrity
- Each unit of work MUST carry a deterministic idempotency key derived from its input identity, never from wall-clock time, iteration index, or randomness; a retry re-applies by that key.
- A resume MUST revalidate the input identity against the checkpoint and Return `FAILED_VALIDATION` when the input changed.
- Witness drift across attempts MUST be treated as corruption.
- One most-deterministic backend MUST be selected from the current SSOT before execution.
- An explicit error or integrity failure MUST Return a terminal failed or skipped outcome, never a backend switch.
- Size checks on optimized formats MUST allow a repo-configurable tolerance ratio.
- Size checks MUST be paired with content-based witnesses (counts, IDs) where feasible.

## Batch task scaffold
```
- input formats (csv/json/jsonl/parquet/etc):
- input locations (paths/globs):
- expected size (files, rows, bytes):
- ordering/dedup requirements:
- output artifacts:
- overwrite policy (append/replace/transactional):
- run report location:
- constants owner:
- config owner:
- rules/validators owner:
- workflow/runner owner (runtime coordinator only):
- run outcomes/report owner:
- overwrite/replace strategy (temp + atomic replace, backups if required):
- idempotency key derivation (input identity fields) and resume behavior:
- checkpoint store location and commit point:
- queue bound and behavior at bound (block or recorded drop):
- failure behavior (partial outputs, cleanup, logged reason):
- bottleneck hypothesis (disk/network/parse/serialize/CPU):
- levers (minimal set that applies): streaming or chunking with bounded memory; cached lookups with declared invalidation; buffered writes; keyed join or dedup; bounded queue with backpressure:
- evidence plan (deterministic timing or complexity verification):
- preconditions (input paths, permissions, schemas/headers):
- postconditions (artifacts produced, no partial corruption, cleanup complete):
- failure modes (what fails, how logged, what is left on disk):
- acceptance: run outcomes, reconciled counts, and user-facing summary recorded per the run-outcomes contract:
- acceptance: failure-path check executed (missing input, invalid schema):
```
