---
doc_type: policy
ssot_owner: AGENTS.md
update_trigger: data integrity constraints change
---

# 70 — I/O & Data Integrity

## First principle
Automation must not “fix” data unless the spec explicitly requires it.

## Excel data rules
- Preserve zeros (0 is data).
- Avoid row-drop heuristics that treat formulas/zeros as “empty”.
- Prefer header-based table detection over hardcoded ranges when possible.

## File handling rules
- Validate paths early.
- Time-bound subprocess calls.
- Prefer transactional file operations (verify destination before deleting originals).

## Bounded processing rules
- Read and cache only validated required data ranges/lookups; record bounds, counts, cache scope, and invalidation trigger when caching affects correctness.
- Batch/chunk/queue processing must declare memory bounds, concurrency limits, deterministic output ordering, timeout/cancellation behavior, and cleanup behavior.
- Do not optimize by dropping validation, skipping real-data/domain checks, or hardcoding ranges that should come from input/schema/config authorities.

## Aggregation / merge integrity (when workflows combine artifacts)
- Retries must be **idempotent** for identical inputs; witness drift across attempts implies corruption.
- Select one **most deterministic backend** from the current SSOT before execution; explicit error or integrity failure must produce a terminal failed/skipped outcome rather than switching to another backend.
- Size checks on optimized formats must allow **tolerance** (ratio-based, repo-configurable) and must be paired with content-based witnesses (counts/IDs) where feasible.
- For PDF-specific guidance: `docs/agents/playbooks/pdf-task-template/pdf-task-template.md` (inject via manifest profile `pdf_task`).

## Run outcomes
Every processed item should record:
- identifier
- outcome (`EXECUTED` / `SKIPPED` / `FAILED`)
- reason (when skipped or failed)
- produced artifacts/paths (if any)
- reconciliation counts (`planned`, `eligible`, `executed`, `skipped`, `failed`) when the item universe is knowable
- zero eligible/no-op state as `SKIPPED + reason` or `FAILED` unless the workflow contract declares a valid no-op

## References
- `docs/agents/80-testing-real-files/testing-real-files.md` (companion: I/O testing guidance for changes affecting file processing)
