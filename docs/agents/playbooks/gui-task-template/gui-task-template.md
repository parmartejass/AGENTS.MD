---
doc_type: playbook
ssot_owner: AGENTS.md
update_trigger: GUI threading, performance, or cancellation expectations change
---

# Playbook — GUI Task (Tkinter/UI)

Use when:
- Task matches profile `gui_task` in `agents-manifest.yaml`.

## Governing evidence

This task scaffold applies `AGENTS.md` Fundamental Principles and Verification Floors. Record task type, blast radius, applicable owner obligations, and witnesses. Bugfix evidence uses `docs/agents/playbooks/bugfix-template/bugfix-template.md`; implementation design uses `docs/agents/35-coding-principles/coding-principles.md`. Agent lifecycle and authorization remain owned by `Orchestration.md`.

## UI requirements
- controls:
- input/scope confirmation:
- progress/current-phase display:
- terminal summary (success/partial/failure/skipped/cancelled):
- output/report/log pointer:
- cancel behavior:

## Threading design
- worker mechanism:
- queue message schema:
- drain interval:
- stop/cancel mechanism (event + UI poll; no join on UI thread):
- interruptible waits (use `Event.wait(...)`):

## Responsiveness & performance evidence
- Governing responsiveness contract and witness: `AGENTS.md` FP-03.
- Workload model (items/events, expected update rate, worst-case runtime):
- Queue strategy (avoid floods; coalesce progress; keep messages small; record queue size/backpressure bounds):
- UI update throttle (rate-limit progress updates; batch multiple messages per drain tick):
- Worker bounds (no unbounded threads; timeouts; guaranteed cleanup on cancel):
- FP-03 acknowledgment/status and controllable-decision timing witnesses:
- Evidence plan (how responsiveness and throughput are verified deterministically):

## Proof obligations (first principles)
- UI thread never blocks (how verified):
- all UI updates on main thread (how enforced):
- cancellation/shutdown semantics (what "cancelled" means + how verified):

## SSOT mapping (fill with exact repo locations)
- workflow entrypoint (runtime coordinator only):
- rules/validators owner (business rules and UI intent predicates):
- config keys owner:
- GUI queue/drain owner:

## Acceptance checks
- UI never blocks:
- no UI updates off main thread:
- user sees accepted input/scope, progress/current phase, terminal outcome, reason/action for skip/fail, and output/report/log pointer when applicable:
- visible summary matches workflow outcome vocabulary and counts:
- cancel stops worker:
- failure-path check executed:
- verification commands come from README.md "Checks":
