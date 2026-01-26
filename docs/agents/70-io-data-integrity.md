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

## Run outcomes
Every processed item should record:
- identifier
- outcome (`EXECUTED` / `SKIPPED` / `FAILED`)
- reason (when skipped or failed)
- produced artifacts/paths (if any)
