---
doc_type: policy
ssot_owner: AGENTS.md
update_trigger: data integrity constraints change
---

# 70 — I/O & Data Integrity

## Authority
`AGENTS.md` FP-10, FP-20, FP-22, and FP-31 govern source authority, unknown inputs, configurable paths, and preservation. This document owns I/O-specific mechanics.

## Transformation authorization evidence
Before mutation, repair, normalization, or row/field removal, the I/O record MUST identify the declared transformation contract, affected source identities, authorized value changes, and preservation witness. Unresolved values or unknown inputs MUST retain their originals; route resolution and its explicit outcome through the owning input/schema/config/rule contract under `AGENTS.md` FP-10 and FP-20. An apparent data defect is not transformation authorization.

## Excel data rules
- Preserve zeros (0 is data).
- Row-drop heuristics MUST NOT treat formulas or zeros as empty.
- Table boundaries MUST resolve from the declared input/schema/header/config owner; fixed ranges require that owner's explicit contract and representative-data witness.

## Implementation Write State Machine + Two-Phase Commit (When repository or external writes occur)
This state machine governs transactional implementation/write safety only. It does not define agent orchestration, roles, review phases, or terminal workflow decisions; those are owned by `Orchestration.md`.
- Required phases: INIT, VALIDATED, COMMIT_READY, COMMITTING, CLEANING, DONE.
- Failure phases: FAILED_VALIDATION, FAILED_COMMIT, FAILED_CLEANUP.
- Validation must be side-effect free; no writes before VALIDATED.
- If any failure after writes begin: record FAILED_COMMIT, log what was written, attempt bounded cleanup in `finally`.

## Resource Safety
- Resource owners MUST guarantee cleanup through context managers or `finally`; waits and termination MUST follow the explicit lifecycle contract under FP-25 and FP-31.

## File handling rules
- Validate paths early.
- Time-bound subprocess calls.
- Overwrite or move workflows MUST validate the destination and preserve recovery until their owner-declared commit witness passes.

## Bounded processing rules
- Read and cache only validated required data ranges/lookups; record bounds, counts, cache scope, and invalidation trigger when caching affects correctness.
- Batch/chunk/queue processing must declare memory bounds, concurrency limits, deterministic output ordering, timeout/cancellation behavior, and cleanup behavior.
- Do not optimize by dropping validation, skipping real-data/domain checks, or hardcoding ranges that should come from input/schema/config authorities.

## Aggregation / merge integrity (when workflows combine artifacts)
- Retries must be **idempotent** for identical inputs; witness drift across attempts implies corruption.
- Select one **most deterministic backend** from the current SSOT before execution; explicit error or integrity failure must produce a terminal failed/skipped outcome rather than switching to another backend.
- Size checks on optimized formats must allow **tolerance** (ratio-based, repo-configurable) and must be paired with content-based witnesses (counts/IDs) where feasible.
- For PDF-specific guidance: `docs/agents/playbooks/pdf-task-template/pdf-task-template.md` (route through manifest profile `pdf_task`).

## Run outcomes
Every processed item MUST record:
- identifier
- outcome (`EXECUTED` / `SKIPPED` / `FAILED`)
- reason (when skipped or failed)
- produced artifacts/paths (if any)
- reconciliation counts (`planned`, `eligible`, `executed`, `skipped`, `failed`) when the item universe is knowable
- zero eligible/no-op state as `SKIPPED + reason` or `FAILED` unless the workflow contract declares a valid no-op

## References
- `docs/agents/80-testing-real-files/testing-real-files.md` (companion: I/O testing guidance for changes affecting file processing)
