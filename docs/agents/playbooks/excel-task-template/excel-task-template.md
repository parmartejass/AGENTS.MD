---
doc_type: playbook
ssot_owner: AGENTS.md
update_trigger: Excel lifecycle, library-selection, performance, or reporting expectations change
---

# Playbook — Excel Automation Task

Use when:
- Task matches profile `excel_automation` in `agents-manifest.yaml`.
- If using Excel COM automation (`win32com`/`xlwings`), profile `excel_com` also applies and injects `docs/agents/50-excel-com-lifecycle/excel-com-lifecycle.md`.

## Library selection authority (required)
- Use `docs/agents/playbooks/excel-library-selection-playbook/excel-library-selection-playbook.md` as the single owner for:
  - cross-platform default vs COM escalation rules
  - capability-to-library matrix
  - single-library vs multi-library pipeline decisions
  - speed/reliability/safety selection order
- Do not duplicate library-selection rules in task docs; reference the canonical playbook and record your chosen path.

## Change classification (required)
- task type (feature|bugfix|refactor):
- blast radius (modules/workflows/users):
- if bugfix/regression: fill `docs/agents/playbooks/bugfix-template/bugfix-template.md`.
- if feature/behavior change: satisfy `AGENTS.md` "Verification Floors (Hard Gate)" behavior-change/new-feature minimums (including shift-left baseline).
- if refactor/behavior-neutral: satisfy `AGENTS.md` "Verification Floors (Hard Gate)" behavior-neutral minimums.
- if new logic is introduced: apply `docs/agents/35-coding-principles/coding-principles.md` under the `AGENTS.md` coding hard gate.

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
- If using Excel COM: follow `docs/agents/50-excel-com-lifecycle/excel-com-lifecycle.md` (PID-tracked quit + bounded PID-scoped forced termination after verified graceful-quit failure, all in `finally`).
- start/open method:
- PID tracking:
- quit + verify:
- forced termination cleanup (PID-validated + bounded timeout, after verified graceful-quit failure):

## Performance & throughput plan (when relevant)
- Never trade away safety/data integrity for speed.
- Data size model (workbooks/sheets, rows/cols, formulas, expected runtime):
- Bottleneck hypothesis (COM round-trips vs file I/O vs calculation):
- Safe levers (pick the minimal set that applies):
  - Bulk read/write (avoid per-cell COM loops; minimize round-trips).
  - Determine bounds once (prefer table/ListObject bounds; otherwise compute last used row/col with validation so no trailing data is missed).
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
