---
doc_type: playbook
ssot_owner: AGENTS.md
update_trigger: Excel lifecycle, library-selection, performance, or reporting expectations change
---

# Playbook — Excel Automation Task

Use when:
- Task matches profile `excel_automation` in `agents-manifest.yaml`.
- If using Excel COM automation (`win32com`/`xlwings`), profile `excel_com` also applies and routes `docs/agents/50-excel-com-lifecycle/excel-com-lifecycle.md`.

## Library selection authority (required)
- Record capability discovery, candidate evaluation, and selected owner/config through `docs/agents/playbooks/excel-library-selection-playbook/excel-library-selection-playbook.md`.

## Governing evidence

This task scaffold applies `AGENTS.md` Fundamental Principles and Verification Floors. Record task type, blast radius, applicable owner obligations, and witnesses. Bugfix evidence uses `docs/agents/playbooks/bugfix-template/bugfix-template.md`; implementation design uses `docs/agents/35-coding-principles/coding-principles.md`. Agent lifecycle and authorization remain owned by `Orchestration.md`.

## Inputs
- workbooks involved:
- sheets/tables involved:
- required headers:
- output artifacts:
- selected library path (from canonical selection playbook):
- runtime path/backend selection owner (workflow entrypoint or config SSOT path):

## SSOT mapping (fill with exact repo locations)
- constants owner:
- config owner:
- rules/validators owner (business rules and checkbox/config predicates):
- workflow/orchestration owner (runtime coordinator only):
- selected runtime path/backend owner:
- run outcomes/report owner:

## Excel lifecycle plan
- COM evidence owner: `docs/agents/50-excel-com-lifecycle/excel-com-lifecycle.md`.
- start/open method:
- PID tracking:
- quit + verify:
- forced termination cleanup (PID-validated + bounded timeout, after verified graceful-quit failure):

## Performance & throughput evidence
- Governing performance contract and witness: `AGENTS.md` FP-03 and Performance & Speed.
- Data size model (workbooks/sheets, rows/cols, formulas, expected runtime):
- Bottleneck hypothesis (COM round-trips vs file I/O vs calculation):
- Safe levers (pick the minimal set that applies):
  - Bulk read/write (avoid per-cell COM loops; minimize round-trips).
  - Record the source/schema/config-owned table or range bounds and validation proving no trailing data is missed.
  - Cache only validated required lookups/ranges (e.g., mapping dictionaries, parsed headers/ranges); define cache key/scope, max size, and invalidation when sheet/schema/data bounds change.
  - Batch/chunk processing with bounded memory, deterministic ordering, queue/backpressure if applicable, and cancellation/timeouts.
  - If toggling Excel settings (screen updating/calculation/events): restore in `finally` and log changes.
- Evidence plan (how timing or complexity is verified deterministically):
- Range/cache witness (sheet/table/range, bounds source, rows/cols, invalidation trigger):

## Proof obligations (first principles)
- preconditions (required files/sheets/headers):
- postconditions (artifacts produced, no orphan Excel.exe):
- failure modes (how it fails + what is logged/reported):

## Acceptance checks
- run outcomes recorded (EXECUTED/SKIPPED + reason):
- known work counts reconcile planned/eligible/executed/skipped/failed:
- logs present:
- user-facing summary includes input/scope, progress/current phase for long work, terminal result, output path, reason/action, and log/report pointer:
- no orphan Excel.exe:
- range/cache witness proves no required trailing data/formula rows were missed:
- failure-path check executed:
- verification commands come from README.md "Checks":
