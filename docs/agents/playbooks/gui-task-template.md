---
doc_type: playbook
ssot_owner: AGENTS.md
update_trigger: GUI threading, performance, or cancellation expectations change
---

# Playbook — GUI Task (Tkinter/UI)

Use when:
- Task matches profile `gui_task` in `agents-manifest.yaml`.

## UI requirements
- controls:
- progress display:
- cancel behavior:

## Threading design
- worker mechanism:
- queue message schema:
- drain interval:

## Responsiveness & performance plan (when relevant)
- Follow `AGENTS.md` "Performance & Speed (When Relevant)" (UI stays correct + responsive; no safety trade-offs).
- Workload model (items/events, expected update rate, worst-case runtime):
- Queue strategy (avoid floods; coalesce progress; keep messages small; consider max queue size/backpressure):
- UI update throttle (rate-limit progress updates; batch multiple messages per drain tick):
- Worker bounds (no unbounded threads; timeouts; guaranteed cleanup on cancel):
- Evidence plan (how responsiveness and throughput are verified deterministically):

## Proof obligations (first principles)
- UI thread never blocks (how verified):
- all UI updates on main thread (how enforced):
- cancellation/shutdown semantics (what "cancelled" means + how verified):

## SSOT mapping (fill with exact repo locations)
- workflow entrypoint:
- rules used:
- config keys used:
- GUI queue/drain owner:

## Acceptance checks
- UI never blocks:
- no UI updates off main thread:
- cancel stops worker:
