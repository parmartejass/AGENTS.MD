---
doc_type: policy
ssot_owner: AGENTS.md
update_trigger: GUI threading/cancellation invariants change
---

# 60 — GUI Threading (Tkinter / UI)

## Invariants
1) UI thread never blocks on long work (including thread joins).
2) UI updates happen only on the main thread.
3) Worker communicates via queue messages.
4) Worker observes a shutdown/cancel event.
5) Cancellation waits are interruptible (prefer `Event.wait(timeout)` over `time.sleep`).
6) User-visible status/progress/result feedback is posted through the queue and stays concise, current, and non-blocking.

## Required pattern (conceptual)
- UI thread starts worker and schedules `after(...)` to drain queue.
- Worker performs long work and posts bounded/coalesced progress, terminal results, errors, cancellation state, and run/report/log pointers to the queue.
- UI thread updates widgets only from drained messages.
- Stop/close handlers set cancel event and return immediately; UI polls worker completion via `after(...)`.

## Forbidden patterns
- updating UI from worker thread
- calling Excel COM from UI thread
- no cancellation/shutdown mechanism
- calling `join()` from UI event handlers
- `time.sleep(...)` in cancellable loops (use `Event.wait(...)` instead)
- long-running work with no visible progress/current-phase feedback
- reporting success/failure in the UI by reinterpreting workflow outcomes instead of presenting the workflow result

