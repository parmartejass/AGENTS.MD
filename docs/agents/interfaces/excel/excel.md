---
doc_type: policy
ssot_owner: docs/agents/interfaces/excel/excel.md
update_trigger: Excel backend-selection, Excel data rule, or COM lifecycle evidence changes
---

# Excel

Jurisdiction: Excel backend selection, workbook evidence, Excel data rules, and COM automation lifecycle.

## Backend selection
```yaml
baseline:
  interface: direct OOXML package parts and relationships
  pattern: "validated package parts and relationships mutated surgically; unowned parts preserved byte-for-byte except declared derived parts, which are recomputed or dropped with their content-type Override and relationship; selection recorded before execution"
  reason: stable, engine-independent package format; no drift from Excel and no external-library dependency
  exception: COM only for native-engine capability the package does not express, after the COM lifecycle below is satisfied
```
- Direct OOXML package-part authoring or surgical mutation MUST be the first candidate for workbook creation and updates.
- MUST select it when the operation is expressible through validated package parts and relationships.
- That expression MUST deliver or preserve data, formulas, calculated values (engine-computed or deferred through `fullCalcOnLoad`), formatting, macros, relationships, external links, workbook metadata, and declared conformance class (Transitional or Strict).
- General workbook-model libraries are prohibited as creation or update backends.
- Permitted: ZIP/XML tools for direct package operations without introducing a workbook-model backend.
- Performance, convenience, dependency availability, or familiar API shape MUST NOT change this selection.
- Direct OOXML work MUST stay limited to validated parts and relationships.
- Updates MUST preserve unowned parts byte-for-byte, or record an explicit equivalence witness when canonicalization is unavoidable.
- Derived parts (`xl/calcChain.xml`, shared-string `count` and `uniqueCount`) MUST be recomputed or dropped together with their content-type Override and relationship, never carried forward unchanged.
- Safety evidence MUST include side-effect-free validation before write.
- Safety evidence MUST include bounded promotion under the filesystem two-phase commit.
- Safety evidence MUST include created/changed-part identities and package completeness.
- Safety evidence MUST include unchanged-part preservation or equivalence where applicable.
- Safety evidence MUST include explicit unsupported outcomes for unresolved workbook features.
- MUST select COM only when authoritative capability discovery proves a native-capability gap.
- Native-capability gap means required Excel engine, UI, refresh, rendering, calculation, or macro-execution behavior, or other native Excel-interface behavior, is unavailable through direct package operations.
- Selected COM MUST satisfy `## COM lifecycle` before execution.
- When neither permitted path satisfies the complete contract, Return an explicit unsupported outcome.

## Selection record
Record before selecting or changing an Excel backend:
- Required workbook operations and preservation criteria declared by the inputs (formats, formulas, calculation fidelity, macros, refresh, formatting, other input-declared features).
- Backend decision against the policy above, with completeness and preservation or equivalence witnesses.
- Recorded native-capability gap when COM is selected.
- Supported operating systems, dependency versions, deployment environment, and authorized interfaces.
- Candidate capabilities verified from current authoritative format/platform contracts, with source, version, and unresolved limitations.
- Workload bounds and measured timing or explicit I/O and complexity evidence.
- Safety, reliability, cleanup, and failure-path witnesses per viable candidate.
- Selected owner/config entry, rationale against every requirement, affected consumers, and superseded selection removed.
- A candidate failing a requirement MUST NOT be made viable by a speed advantage.

## Pipeline composition
- A multi-backend pipeline MUST declare stage contracts and plain-data boundaries.

## Performance evidence
- Bulk ranges and tables: Record bounds source, row/column counts, and round-trip count.
- Measured full-operation timing MUST be recorded before accepting the selected backend.
- COM choices MUST carry bulk-call evidence instead of assuming per-cell automation meets the workload.
- These levers MUST NOT alter required data or workbook behavior.

## Excel data rules
- Zeros MUST be preserved; 0 is data.
- Row-drop heuristics MUST NOT treat formulas or zeros as empty.
- Table boundaries MUST resolve from the declared input/schema/header/config owner.
- Fixed ranges require that owner's explicit contract and a representative-data witness.

## Validation witnesses

| Concern | Witness | Pass criterion source |
|---|---|---|
| Data preservation | Input/output row counts and key sets | Declared transformation contract |
| Ordering | Ordered input/output identities | Declared ordering rule |
| Atomicity | Validation and promotion events | The filesystem two-phase commit |
| Idempotency | Output/content and outcome parity | Declared equivalence contract |
| COM lifecycle | Owned PID, workbook, reference, and cleanup records | `## COM lifecycle` |
| Range/cache correctness | Bounds, counts, keys, and invalidation | Source/schema/config owner |

## Failure-path evidence
- Locked output: Record explicit commit failure and preserved original file.
- COM quit failure: Record the owner-validated PID cleanup witness.

## COM lifecycle
- Applies after COM is selected, including `Excel.Application`, `win32com`, `xlwings`, `Dispatch`, `DispatchEx`, `CreateObject`, `GetObject`, `GetActiveObject`.
- Ownership model: a new workflow-owned instance created through the new-instance activation path (`DispatchEx`, not `Dispatch`) is the default whenever cleanup authority is needed.
- Attaching to a running user instance is permitted only when the task declares attach-to-user-instance behavior.
- A separate COM-created instance is an ownership boundary, not sandbox isolation.
- Instances still share user profile state, add-ins, templates, clipboard, printers, file locks, links, cached credentials, macros, and dialogs.
- COM MUST NOT be selected for unattended, non-interactive, or service-hosted execution.

### Invariants
1. Workflow-owned instances MUST be closed on workflow exit.
2. Owned workbooks and child references MUST be closed or released before application quit/release.
3. COM initialization MUST be paired with uninitialization on the same thread on all failure paths.
4. Changed Excel application settings MUST be restored in `finally`.
5. Cleanup failures MUST be recorded as `FAILED_CLEANUP` or an equivalent terminal cleanup outcome, never swallowed or reported as success.
6. A workflow-owned COM instance MUST run with `Visible=False` and `DisplayAlerts=False`.

### Lifecycle stages
- Initialize COM for the current thread when required.
- Create or attach to Excel and record whether the instance is workflow-owned.
- Capture and record the owned PID before any workflow workbook is opened.
- Record workflow-owned workbook identities before processing.
- Open only declared workflow workbooks.
- Process.
- Save or close only workflow-owned workbooks.
- Release workbook, worksheet/range, and other child references before app release.
- Restore changed Excel application settings in `finally`.
- Quit Excel gracefully when workflow-owned.
- Verify process exit for the owned PID.
- Terminate only the containment object holding only the validated owned PID within a bounded timeout after verified graceful-quit failure.
- Uninitialize COM for the current thread when the workflow initialized it.
- Log each stage and the final cleanup outcome.

### Witnesses
- `instance_ownership`: workflow-owned or explicit attach-to-user-instance.
- `workbooks_owned`: workflow-owned workbook identities.
- `workbooks_closed`: close/save result per owned workbook.
- `settings_restored`: changed Excel settings restored or failure recorded.
- `com_refs_released`: application, workbook, and child reference release outcome.
- `quit_called`: graceful quit attempted for the owned instance.

### Forbidden patterns
- Leaving workflow-owned `Excel.exe` running intentionally.
- Using `GetObject` or `GetActiveObject` as the default path when cleanup authority is needed.
- Quitting or blanket-closing workbooks in an attached instance unless ownership of that PID and every open workbook is proven and recorded.
- Swallowing COM or cleanup errors without recording and re-raising or propagating the terminal outcome.
- Reporting success when close, quit, release, uninit, or PID cleanup failed.
- COM initialization without guaranteed uninitialization on all failure paths.
- Unbounded waits during open, refresh, save, quit, verify, or cleanup.
- Allowing macro, security, or UI prompts to hang instead of failing or terminalizing with reason.

## Task scaffold
```
- workbooks, sheets/tables, and required headers involved:
- output artifacts:
- selected backend path and backend-selection decision record:
- derived-part disposition and recalculation strategy:
- unchanged-part preservation or equivalence witness:
- start/open method, PID tracking, quit + verify:
- forced termination cleanup (containment-scoped, PID-validated, bounded, after graceful-quit failure):
- Excel setting toggles (screen updating/calculation/events) restored in finally and logged:
- range/cache witness (sheet/table/range, bounds source, rows/cols, invalidation trigger):
- acceptance: no orphan Excel.exe:
```
