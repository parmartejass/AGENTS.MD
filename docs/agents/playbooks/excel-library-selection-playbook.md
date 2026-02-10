---
doc_type: playbook
ssot_owner: AGENTS.md
update_trigger: Excel library selection policy, capability matrix, or validation witnesses change
---

# Playbook — Excel Library Selection (Cross-Platform + COM Escalation)

Use when:
- Task includes Excel read/write/transform/automation and library choice affects speed, reliability, or safety.
- Task may run on macOS/Linux/Windows and should avoid Windows lock-in unless Excel-engine features are required.

## Selection policy (deterministic)

1. Classify required capabilities first (no library choice before this):
   - file I/O and transforms only
   - formatting/report generation
   - Excel-engine features (VBA/macro run, pivot/external-link refresh, workbook calc fidelity)
2. Default to a cross-platform path if it satisfies all required capabilities.
3. Escalate to COM (`win32com` or `xlwings`) only for Excel-engine-dependent capabilities.
4. If multiple valid paths remain, choose in this order:
   - speed (measured timing, or explicit complexity/I/O model when timing is unavailable)
   - reliability (deterministic behavior, lower dependency on GUI/process state)
   - safety (bounded timeouts, explicit failures, cleanup guarantees)

## Library tiers

Core:
- `openpyxl`
- `pandas`
- `XlsxWriter`
- `pyxlsb`
- `xlwings`
- `win32com`

Expanded cross-platform options (use when justified by workload):
- `python-calamine`
- `pyexcelerate`
- `polars` connectors/pipelines (typically via pandas-compatible Excel I/O boundaries)

## Capability matrix (default path + COM trigger)

| Capability | Default cross-platform path | COM escalation trigger | Recommended stack |
|---|---|---|---|
| File I/O only (no Excel engine) | `pandas` + `openpyxl`/`XlsxWriter` | None | `pandas -> openpyxl` (edits) or `pandas -> XlsxWriter` (new report files) |
| Formatting/report generation | `XlsxWriter` for write-only reports; `openpyxl` for in-place workbook edits | Native Excel rendering parity is contractually required | `pandas -> XlsxWriter` or `openpyxl` |
| Macro/VBA execution | Not supported cross-platform without Excel engine | Always | `xlwings` or `win32com` (Windows) |
| Pivot/external-link refresh | Not reliably available in pure file libraries | Always | `win32com`/`xlwings` |
| Formula recalculation fidelity (Excel engine exactness) | Precompute values or accept stored formula results | Workbook must be recalculated by Excel engine before delivery | cross-platform prep + COM finalization |
| `.xlsb` ingestion | `pyxlsb` or `python-calamine` | Only if downstream step requires Excel engine | `pyxlsb/python-calamine -> pandas/polars` |
| Large-volume writes | `pyexcelerate` (cell-heavy output), `XlsxWriter` (report-style output) | Native Excel engine behavior required post-write | `pandas/polars -> pyexcelerate/XlsxWriter`, optional COM post-step |

## Single-library vs multi-library rules

Use a single library when:
- one library covers all capabilities without fallback logic, and
- performance is acceptable for expected data size.

Use multi-library pipelines when:
- ingestion, transform, and output needs differ materially, or
- Excel-engine features are required only in a terminal step.

Required multi-library patterns (minimum):
1. Ingest-heavy, cross-platform:
   - `pyxlsb` or `python-calamine` -> `pandas`/`polars` -> `XlsxWriter`
2. Transform-heavy analytics:
   - `python-calamine`/`openpyxl` -> `polars` -> `openpyxl`/`XlsxWriter`
3. Excel-engine-required finalization:
   - cross-platform prep (`pandas`/`openpyxl`) -> COM step (`xlwings`/`win32com`) only for macro/refresh/recalc

## Speed practices (without weakening safety)

- Avoid per-cell loops whenever bulk range/table operations exist.
- Minimize COM round-trips by batching read/write and state changes.
- Determine worksheet/table bounds once; avoid repeated scans.
- Use chunked processing for large sheets to bound memory.
- Prefer write-then-atomic-replace patterns for output files when overwriting.
- Reuse parsed headers/mappings within a run; define invalidation on sheet/schema change.

## Reliability and safety practices

- Follow `docs/agents/50-excel-com-lifecycle.md` for all COM workflows (PID-scoped quit verification + bounded kill fallback in `finally`).
- Enforce bounded timeouts for open/read/write/refresh/quit operations.
- Treat retries as idempotent: retry only side-effect-safe steps unless transactional safeguards exist.
- Record explicit terminal outcomes (`EXECUTED`/`SKIPPED`/`FAILED`) with reason for each processed item.
- Never swallow exceptions; use explicit domain errors and contextual logs.
- For lock/contention failures, record deterministic reason codes and avoid partial overwrite.

## Validation protocol (invariants + witnesses)

### Invariants
- Data: row counts/key IDs preserved unless spec says otherwise.
- Ordering: required processing/order constraints are stable across runs.
- Atomicity: no partial final outputs after a failed write.
- Idempotency: rerun with identical inputs yields identical outputs/outcomes.
- Lifecycle: external resources/processes are cleaned up after terminal state.
- Observability: each run and item has terminal outcomes with reasons.

### Witness table

| Invariant | Witness signal | Where recorded | Pass criteria |
|---|---|---|---|
| Data | input/output row count + key-ID set diff | run summary + item evidence | counts/keys match spec |
| Ordering | deterministic phase sequence | phase transition logs | expected sequence only |
| Atomicity | temporary file promotion events | write-effect log fields | no final overwrite before validation |
| Idempotency | output hash/path + outcome parity across rerun | run_end summary | identical for identical inputs |
| Lifecycle | Excel PID before/after (COM path) | lifecycle log fields | no orphan process |
| Observability | terminal outcome per item | item-level records | 100% item terminalization |

## Failure-path checks (deterministic)

Non-COM path checks:
1. Missing sheet/header:
   - Expect `FAILED_VALIDATION` with explicit reason; no writes.
2. Locked output file:
   - Expect `FAILED_COMMIT` with lock reason; original file unchanged.
3. Invalid data shape:
   - Expect `FAILED_VALIDATION`; no partial artifacts.

COM path checks:
1. Excel startup/open failure:
   - Expect explicit COM error and terminal run failure with cleanup attempt.
2. Quit failure:
   - Expect bounded verify/kill fallback per PID-scoped lifecycle policy.
3. Refresh/recalc timeout:
   - Expect timeout failure code and bounded cleanup; no silent continuation.

## Anti-patterns (forbidden)

- Choosing COM by default when cross-platform path satisfies requirements.
- Per-cell COM loops for large datasets without explicit justification.
- Killing all Excel processes instead of validated PID-scoped cleanup.
- Infinite waits during open/refresh/quit.
- Silent exception handlers (`except ...: pass`) in workflow paths.
- Duplicating library-selection rules in multiple docs instead of referencing this playbook.
