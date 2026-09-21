---
doc_type: playbook
ssot_owner: docs/agents/playbooks/run-outcomes/run-outcomes.md
update_trigger: outcome vocabulary, work reconciliation, user-facing summary content, or log schema fields change
---

# Run Outcomes

Jurisdiction: the outcome vocabulary, work reconciliation, user-facing summary content, and the log schema for every run.

```yaml
baseline:
  interface: run, phase, and item event records emitted through the standard logging facility
  pattern: "low-cardinality event name plus fields; per-item terminal outcome; run summary with reconciled work counts; user-facing summary from the same vocabulary"
  reason: one outcome vocabulary for logs, reports, and UI; a second vocabulary drifts from the recorded run
  exception: none
```

## Outcome vocabulary
- Per-item outcome: `EXECUTED`, `SKIPPED`, or `FAILED`, always paired with a reason.
- Every item MUST reach exactly one terminal outcome, recorded once at terminal state with its identifier.
- Silent skips are prohibited; record `SKIPPED + reason` in the log or run report.
- Run result: `SUCCESS`, `PARTIAL_SUCCESS`, `FAILURE`, `CANCELLED`, or `TIMEOUT`; user cancellation and a declared deadline MUST NOT be reported as `FAILURE`.
- reason-code owner: the application's declared runtime enum owner.

## Work reconciliation
- Success and partial success MUST reconcile `planned`, `eligible`, `executed`, `skipped`, `failed`.
- The reconciliation identity MUST be asserted in code at `run_end`; a mismatch is itself a recorded `FAILURE`.
- A workflow with an unknowable work universe MUST fail validation.
- An unknowable item universe MUST return `FAILED_VALIDATION` with `UNKNOWN_ITEM_UNIVERSE` or equivalent.
- Continuing with an unknown universe is allowed only when the workflow contract declares the uncertainty.
- Zero eligible work MUST return `SKIPPED + reason` or `FAILED` unless a valid no-op is declared.
- A valid no-op MUST be visible as a terminal outcome with reason, for example `SKIPPED + VALID_NOOP`.
- All-zero work MUST NOT be reported as `SUCCESS`.
- Best-effort loops MUST record a terminal per-item outcome and reason.
- Best-effort loops MUST reflect partial failure at the run level.
- Record produced artifacts and paths per item.

## User-facing summary
- User-facing surfaces MUST show input/scope confirmation.
- User-facing surfaces MUST show progress or current phase for long work.
- User-facing surfaces MUST show the terminal outcome.
- User-facing surfaces MUST show the output/artifact path when produced.
- User-facing surfaces MUST show the skip or failure reason.
- User-facing surfaces MUST show the required user action.
- User-facing surfaces MUST show the run/report/log pointer when applicable.
- User feedback MUST stay concise and actionable; deep diagnostics stay in structured logs.
- User feedback MUST NOT carry stack traces, raw payload dumps, or per-item floods.
- A degraded or unavailable log/report sink MUST be stated in user feedback.
- Degraded-sink feedback MUST preserve the workflow outcome separately.

## Log schema
- Required whenever logs are emitted.
- Machine-debuggable runs MUST use this event contract.
- `run_end` MUST be emitted from a `finally` so a run terminated by an unhandled exception still records its result.

Run-level record (`run_start`, `run_end`):
```
- ts: ISO 8601 UTC with explicit offset
- event: run_start | run_end
- run_id
- app, version, mode
- inputs, outputs: objects
- result: SUCCESS | PARTIAL_SUCCESS | FAILURE | CANCELLED | TIMEOUT
- summary: by_outcome {executed, skipped, failed}; failed_by_phase {validation, commit, cleanup}; work_counts {planned, eligible, executed, skipped, failed}
- timings_ms: object (monotonic-clock durations)
- errors: array of {type, message, where, fatal}
- resources: pids_before/after, handles_closed, quit_called, pid_forced_termination_used
```
- `resources` is selected by the lifecycle owner when external resources are in scope.
- `resources` MUST carry a cleanup witness when selected.
- Knowable universe identity: `work_counts.planned == work_counts.executed + work_counts.skipped + work_counts.failed`.

Phase transition record:
```
- ts
- event: phase_transition
- run_id
- phase
- phase_seq
- notes
```
- `notes` is included by the event owner when needed to explain the transition.
- Core fields MUST retain the transition witness.

Item-level record (`row_event` or `file_event`), emitted once per item at terminal state:
```
- ts, event, run_id, phase
- item_id: row id or file path
- outcome: EXECUTED | SKIPPED | FAILED
- final_phase: VALIDATED | COMMITTED | FAILED_VALIDATION | FAILED_COMMIT | FAILED_CLEANUP
- reason_code, reason_detail
- evidence: object
- write_effects: object
- duration_ms
```

Reason-code owner resolution; this scaffold MUST NOT create an enum owner:
```
- Runtime enum/config owner reference and public contract:
- Existing code identifier and meaning, or proposed extension:
- Owner extension entrypoint and authorized change reference:
- Affected emitters/consumers and migration or compatibility witness:
- Validation command/manual witness and result confirming the owner-defined code is emitted and interpreted consistently:
```
- Example codes only, non-normative: `MISSING_REQUIRED_HEADER`, `DUPLICATE_HEADER`, `MISSING_INPUT_FILE`, `INVALID_IDENTIFIER_FORMAT`, `DUPLICATE_KEY_IN_INPUT`, `COM_WRITE_FAILED`, `SAVE_FAILED`, `EXCEL_QUIT_FAILED`, `PID_VALIDATION_FAILED`, `UNKNOWN_ITEM_UNIVERSE`, `VALID_NOOP`.

## Witnesses
- Runtime: per-item outcome records, user-visible terminal summary, run summary with work-count reconciliation.
