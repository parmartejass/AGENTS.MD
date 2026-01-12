---
doc_type: policy
ssot_owner: AGENTS.md
update_trigger: GUI threading/cancellation invariants change
---

# 60 — GUI Threading (Tkinter / UI)

## Invariants
1) UI thread never blocks on long work.
2) UI updates happen only on the main thread.
3) Worker communicates via queue messages.
4) Worker observes a shutdown/cancel event.

## Required pattern (conceptual)
- UI thread starts worker and schedules `after(...)` to drain queue.
- Worker performs long work and posts progress/results/errors to the queue.
- UI thread updates widgets only from drained messages.

## Forbidden patterns
- updating UI from worker thread
- calling Excel COM from UI thread
- no cancellation/shutdown mechanism

