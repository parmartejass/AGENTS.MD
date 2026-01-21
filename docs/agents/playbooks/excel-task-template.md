---
doc_type: playbook
ssot_owner: AGENTS.md
update_trigger: Excel lifecycle, performance, or reporting expectations change
---

# Playbook — Excel Automation Task

Use when:
- Task matches profile `excel_automation` in `agents-manifest.yaml`.
- If using Excel COM automation (`win32com`/`xlwings`), profile `excel_com` also applies and injects `docs/agents/50-excel-com-lifecycle.md`.

## Inputs
- workbooks involved:
- sheets/tables involved:
- required headers:
- output artifacts:

## SSOT mapping (fill with exact repo locations)
- constants owner:
- config owner:
- rules owner:
- workflow owner:
- run outcomes/report owner:

## Excel lifecycle plan
- If using Excel COM: follow `docs/agents/50-excel-com-lifecycle.md` (PID-tracked quit + bounded kill fallback, all in `finally`).
- start/open method:
- PID tracking:
- quit + verify:
- kill fallback (PID-validated + bounded timeout):

## Performance & throughput plan (when relevant)
- Follow `AGENTS.md` "Performance & Speed (When Relevant)" (never trade away safety/data integrity for speed).
- Data size model (workbooks/sheets, rows/cols, formulas, expected runtime):
- Bottleneck hypothesis (COM round-trips vs file I/O vs calculation):
- Safe levers (pick the minimal set that applies):
  - Bulk read/write (avoid per-cell COM loops; minimize round-trips).
  - Determine bounds once (prefer table/ListObject bounds; otherwise compute last used row/col with validation so no trailing data is missed).
  - Cache expensive lookups (e.g., mapping dictionaries, parsed headers/ranges); define invalidation when the sheet changes.
  - Batch/chunk processing with bounded memory; respect cancellation/timeouts.
  - If toggling Excel settings (screen updating/calculation/events): restore in `finally` and log changes.
- Evidence plan (how timing or complexity is verified deterministically):

## Proof obligations (first principles)
- preconditions (required files/sheets/headers):
- postconditions (artifacts produced, no orphan Excel.exe):
- failure modes (how it fails + what is logged/reported):

## Acceptance checks
- run outcomes recorded (EXECUTED/SKIPPED + reason):
- logs present:
- no orphan Excel.exe:
