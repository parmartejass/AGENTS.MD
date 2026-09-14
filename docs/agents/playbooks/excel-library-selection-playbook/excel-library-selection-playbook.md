---
doc_type: playbook
ssot_owner: AGENTS.md
update_trigger: Excel selection evidence or capability-discovery contract changes
---

# Playbook — Excel Library Selection

This playbook owns Excel-specific selection evidence. `AGENTS.md` FP-02, FP-03, FP-17 through FP-23, and FP-34 govern selection constraints; the project's declared config/runtime-path owner owns the selected implementation. `Orchestration.md` governs approval and execution.

## Selection record

Before selecting or changing an Excel backend, record:

- Required workbook operations and preservation criteria: formats, formulas, calculation fidelity, macros, refresh, formatting, and other input-declared features.
- Supported operating systems, dependency versions, deployment environment, and authorized interfaces.
- Candidate capabilities verified from current authoritative library/platform contracts; source, version, and unresolved limitations for each candidate.
- Workload bounds and measured timing or explicit I/O/complexity evidence.
- Safety, reliability, cleanup, and failure-path witnesses for each viable candidate.
- Selected owner/config entry, selection rationale against every requirement, affected consumers, and superseded selection removed.

Capability examples identify questions to verify; they are not a closed library list or a default-backend policy. Unknown or unsupported capabilities follow `AGENTS.md` FP-20 and FP-27. A candidate that fails a requirement is not made viable by a speed advantage.

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

The selection owner records whether one library satisfies the contract or separate ingestion, transformation, and output stages are required. A multi-library design requires stage contracts, plain-data boundaries, and evidence that each stage covers a distinct requirement under `docs/agents/35-coding-principles/coding-principles.md`.

COM selection requires verified Excel-engine or interface requirements and the lifecycle evidence owned by `docs/agents/50-excel-com-lifecycle/excel-com-lifecycle.md`. Selection occurs before execution; runtime failures follow `AGENTS.md` No Fallback or Legacy Runtime Paths.

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
