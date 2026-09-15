---
doc_type: playbook
ssot_owner: AGENTS.md
update_trigger: Excel selection evidence or capability-discovery contract changes
---

# Playbook - Excel Backend Selection

This playbook owns Excel-specific selection evidence. `AGENTS.md` FP-02, FP-03, FP-17 through FP-23, and FP-34 govern selection constraints; the project's declared config/runtime-path owner owns the selected implementation. `Orchestration.md` governs approval and execution.

## Excel backend-selection policy

For Excel workbook creation and update tasks, direct OOXML package-part authoring or surgical mutation is the required first candidate. Select it when the requested operation can be expressed through validated workbook package parts and relationships while delivering or preserving required data, formulas, required calculated values, formatting, macros, relationships, external links, workbook metadata, and declared compatibility.

General workbook-model libraries are not eligible backends for creation or updates. ZIP/XML tools may implement direct package operations without introducing a workbook-model backend. Performance, convenience, dependency availability, or familiar API shape does not change this selection.

Direct OOXML creation and updates must be limited to validated package parts and relationships. Updates must preserve unowned parts byte-for-byte where feasible, or provide an explicit equivalence witness when package canonicalization is unavoidable. Safety evidence must include side-effect-free validation before write, bounded promotion through the I/O owner, created/changed-part identities, package completeness, unchanged-part preservation or equivalence where applicable, and explicit unsupported outcomes for unresolved workbook features.

COM is selected only when authoritative capability discovery shows that required Excel engine, UI, refresh, rendering, calculation, macro execution, or other native Excel-interface behavior is unavailable through direct OOXML package operations. When selected, COM must also satisfy the COM lifecycle owner before execution. If neither permitted path satisfies the complete contract, return an explicit unsupported outcome.

Creation and update performance evidence follows `AGENTS.md` FP-03 through `docs/agents/00-principles/evidence/evidence.md` Performance & Speed and the workbook-specific witnesses below.

## Selection record

Before selecting or changing an Excel backend, record:

- Required workbook operations and preservation criteria: formats, formulas, calculation fidelity, macros, refresh, formatting, and other input-declared features.
- Backend decision against the policy above: direct OOXML package parts selected, or recorded native-capability gap requiring COM; completeness and preservation or equivalence witnesses.
- Supported operating systems, dependency versions, deployment environment, and authorized interfaces.
- Permitted candidate capabilities verified from current authoritative format/platform contracts; source, version, and unresolved limitations for each candidate.
- Workload bounds and measured timing or explicit I/O/complexity evidence.
- Safety, reliability, cleanup, and failure-path witnesses for each viable candidate.
- Selected owner/config entry, selection rationale against every requirement, affected consumers, and superseded selection removed.

Capability examples identify questions to verify; they are not a closed library list and do not override the backend-selection policy. Unknown or unsupported capabilities follow `AGENTS.md` FP-20 and FP-27. A candidate that fails a requirement is not made viable by a speed advantage.

## Operation-driven examples (verification prompts)

These examples identify requirements to resolve, not a library recommendation or capability assertion:

| Requested operation | Question for the selected candidate contract | Representative witness |
|---|---|---|
| Formula delivery | Must formulas merely survive, or must calculated values match the Excel engine? | Formula text and calculated-result comparison on the declared workbook fixture |
| Macro/VBA work | Is preservation of VBA sufficient, or is execution required in the authorized environment? | Macro-bearing fixture and the requested preservation/execution result |
| Pivot or external-link refresh | Is refresh required, and which connection/engine contract provides it? | Input connection state and refreshed output evidence |
| Native rendering | Which layout/print/PDF characteristics must match the source? | Rendered-page comparison against the accepted fidelity criteria |
| Binary workbook ingestion or large output | Which formats and bulk operations are required at the measured workload? | Representative format, row/key parity, memory and I/O measurements |

## Pipeline composition

The selection owner records whether one backend satisfies the contract or separate ingestion, transformation, and output stages are required. A multi-backend design requires stage contracts, plain-data boundaries, and evidence that each stage covers a distinct requirement under `docs/agents/35-coding-principles/coding-principles.md`.

COM selection follows the backend-selection policy above; selected COM execution also requires the lifecycle evidence owned by `docs/agents/50-excel-com-lifecycle/excel-com-lifecycle.md`. Selection occurs before execution; runtime failures follow `AGENTS.md` No Fallback or Legacy Runtime Paths.

Illustrative stage compositions include binary-workbook ingestion into a plain-data transform followed by report output, analytics over validated table data followed by workbook formatting, or file preparation followed by an explicitly required engine finalization. Each stage belongs to its selected owner; these examples do not select a backend or permit a substitute path after failure.

For COM choices, assess bulk-call evidence under Performance evidence rather than assuming per-cell automation meets the workload. PID-scoped cleanup, prohibited broad process termination, bounded waits, and exception reporting resolve through the COM lifecycle owner, `AGENTS.md` Resource Safety, and `docs/agents/30-logging-errors/logging-errors.md`.

## Performance evidence

Record the chosen operations and their witnesses:

- Bulk ranges/tables: required bounds source, row/column counts, and round-trip count.
- Cached headers/mappings/properties: validated source, key, scope, maximum size, and invalidation trigger.
- Chunked reads/writes: batch size, memory bound, ordering, and cancellation behavior.
- Output promotion: destination/recovery contract from `docs/agents/70-io-data-integrity/io-data-integrity.md`.

These are candidate techniques, not permission to alter required data or workbook behavior. Selection and evidence follow the governing performance contract.

## Validation witnesses

| Concern | Witness | Pass criterion source |
|---|---|---|
| Data preservation | Input/output row counts and key sets | Declared transformation contract |
| Ordering | Ordered input/output identities | Declared ordering rule |
| Atomicity | Validation and promotion events | I/O owner commit contract |
| Idempotency | Output/content and outcome parity | Declared equivalence contract |
| COM lifecycle | Owned PID, workbook, reference, and cleanup records | COM lifecycle owner |
| Range/cache correctness | Bounds, counts, keys, and invalidation | Source/schema/config owner |

## Failure-path evidence

Select applicable fixtures through `AGENTS.md` Verification Floors and `docs/agents/80-testing-real-files/testing-real-files.md`:

- Missing sheet/header or invalid data shape: validation failure and no writes.
- Locked output: explicit commit failure and preserved original file.
- COM startup/open failure: recorded error and lifecycle cleanup result.
- COM quit failure: owner-validated PID cleanup witness.
- Refresh/recalculation deadline: explicit failure and bounded cleanup under the selected lifecycle contract.

Record the README Checks command or deterministic manual steps, actual outcome, and residual limitations for each applicable witness.
