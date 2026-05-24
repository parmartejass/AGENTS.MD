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

## References
- `docs/agents/80-testing-real-files/testing-real-files.md` (companion: I/O testing guidance for changes affecting file processing)
