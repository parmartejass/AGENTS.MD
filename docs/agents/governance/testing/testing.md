---
doc_type: runbook
ssot_owner: docs/agents/governance/testing/testing.md
update_trigger: real-file verification minimums, fixture and coverage rules, or the test-runner baseline change
---

# Testing

Jurisdiction: real-file verification minimums, fixture and coverage rules, failure-path and guard checks, and the test-runner baseline; these minimums add to the verification floors and replace none.

## Real-file verification

- Applies when changes affect I/O or file processing, whose acceptance criteria are I/O driven.
- Tests MUST include representative real inputs when feasible.
- When real inputs are infeasible, Record why plus a deterministic surrogate fixture and an explicit failure-path witness in the final response or run report.
- Minimum 1: one happy-path run on a representative real input.
- Minimum 2: one failure-path run covering at least one I/O failure mode (missing file, missing required header/sheet, permission denied). This run satisfies the failure-path check for I/O changes.
- Minimum 3: confirm logs contain key stages, run outcomes/report exist, and no owned external process is left running.
- Minimum 3 confirmation MUST use only the existing repo logging and reporting locations.
- Minimum 4: use copies of real inputs and leave the source files unchanged. Record fixture paths and clean up outputs.
- Minimum 5: when performance is an acceptance criterion, capture timing on a representative input and Record where it is stored.
- Disconfirming tests MUST include one property or randomized case where feasible.
- I/O changes MUST include one real-file replay case.

## Fixtures and coverage

- Fixtures MUST be deterministic and sanitized of secrets, PII, and licensed data.
- Golden-file comparison MUST normalize only generator-introduced nondeterministic fields and compare the full remaining payload.
- Regenerating a golden file in the same change that made it fail MUST have a recorded intent.
- Fixtures derived from production records MUST be labeled masked (not synthetic), and their origin MUST be recorded.
- Bugfix: a regression fixture stored in the repo is Required.
- New feature: a representative fixture is Required where feasible. Record why when it is infeasible.
- Meet the existing coverage thresholds on the changed lines as well as on the repository total.
- Coverage thresholds MUST stay at or above their current values.
- Without coverage thresholds, the fixture rules above are the coverage floor.

## Failure-path and guard checks

- Bugfix, performance, and behavior-change work MUST end with one guard run of the full suite or the declared smoke suite.
- Record the guard command and its result. Without a guard run, the change stays unverified.
- The declared smoke suite MUST run the shipped public entry point exactly as a user does: one call, no interactive confirmation.
- The smoke suite MUST own no logic, paths or expected values.

## Baseline

```yaml
baseline:
  interface: the repeatable commands in the repository README Checks section
  pattern: copied real input happy path, one failure path, one guard run, deterministic seeded fixtures, runner version pinned in the lockfile
  reason: "one runner behind README Checks keeps every witness reproducible; it avoids ad hoc scripts and invented commands"
  exception: none
```
