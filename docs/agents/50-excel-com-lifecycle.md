---
doc_type: policy
ssot_owner: AGENTS.md
update_trigger: Excel lifecycle invariants change
---

# 50 — Excel COM Lifecycle (Hard Requirements)

Excel automation is stateful and failure-prone; correctness is defined by cleanup.

## Invariants
1) Excel must be closed on workflow exit.
2) PID must be tracked and validated.
3) Shutdown must be time-bounded (includes lifecycle/cleanup waits).
4) Kill fallback is allowed only after verified quit failure and PID validation.
5) Cleanup must be in `finally` (includes COM init/uninit pairing on all failure paths).

## Required lifecycle stages (conceptual)
- start/open Excel
- record PID
- open workbook(s)
- process
- save/close workbook(s)
- quit Excel gracefully
- verify process exit
- if still alive: kill validated PID only (bounded)
- log each stage

## Forbidden patterns
- leaving Excel.exe running “intentionally”
- killing all Excel processes (no PID scoping)
- swallowing COM errors without recording and re-raising/propagating
- COM initialization without guaranteed uninitialization on *all* failure paths
- unbounded waits during cleanup (e.g., “wait until workbook closes”) without a deadline/timeout

