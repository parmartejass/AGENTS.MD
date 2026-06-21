---
doc_type: playbook
ssot_owner: AGENTS.md
update_trigger: log schema fields or reason code taxonomy changes
---

# Standard Log Schema (Required when logs are emitted)

- Logging policy in "Logging + Explicit Failure" (AGENTS.md Non-Negotiable #4) still applies (no print, module logger, explicit failures).
- The log schema follows `AGENTS.md` Non-Negotiable #1 "SSOT jurisdiction and duplication pruning rule"; do not fork schemas.

## Run-level record (run_start, run_end)
- ts (ISO8601)
- event (run_start | run_end)
- run_id
- app, version, mode
- inputs, outputs (objects)
- result (SUCCESS | PARTIAL_SUCCESS | FAILURE)
- summary (object): by_outcome {executed, skipped, failed}; failed_by_phase {validation, commit, cleanup}; work_counts {planned, eligible, executed, skipped, failed}
- timings_ms (object)
- errors (array of {type, message, where, fatal})
- resources (optional, when applicable): pids_before/after, handles_closed, quit_called, pid_forced_termination_used

When the item universe is knowable, `work_counts.planned == work_counts.executed + work_counts.skipped + work_counts.failed`.
Unknown item universe must fail validation with `UNKNOWN_ITEM_UNIVERSE` or an equivalent reason unless the workflow contract explicitly allows that uncertainty.
All-zero `SUCCESS` summaries are invalid; a valid no-op must terminalize as skipped with `VALID_NOOP` or equivalent explicit reason.

## Phase transition record
- ts, event (phase_transition), run_id, phase, phase_seq, notes (optional)

## Item-level record (row_event or file_event)
Emitted once per item at terminal state:
- ts, event, run_id, phase
- item_id (row id or file path)
- outcome (EXECUTED | SKIPPED | FAILED)
- final_phase (VALIDATED | COMMITTED | FAILED_VALIDATION | FAILED_COMMIT | FAILED_CLEANUP)
- reason_code, reason_detail
- evidence (object)
- write_effects (object)
- duration_ms

## Reason codes
- Maintain a single enum owner (module or config). Extend there only.
- Example codes: MISSING_REQUIRED_HEADER, DUPLICATE_HEADER, MISSING_INPUT_FILE, INVALID_IDENTIFIER_FORMAT,
  DUPLICATE_KEY_IN_INPUT, COM_WRITE_FAILED, SAVE_FAILED, EXCEL_QUIT_FAILED, PID_VALIDATION_FAILED,
  UNKNOWN_ITEM_UNIVERSE, VALID_NOOP.
