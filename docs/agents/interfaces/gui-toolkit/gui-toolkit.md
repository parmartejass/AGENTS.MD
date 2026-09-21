---
doc_type: policy
ssot_owner: docs/agents/interfaces/gui-toolkit/gui-toolkit.md
update_trigger: GUI threading, queue drain, or cancellation mechanics change
---

# GUI Toolkit

Jurisdiction: UI-thread safety, worker/queue threading mechanics, and cancellation mechanics.

## Baseline
```yaml
baseline:
  interface: the toolkit's native main-thread scheduler and queue drain
  pattern: "worker posts to a bounded queue; one owned self-rescheduling after() drain consumes it; cancel event observed; drain id cancelled on destroy; no joins and no blocking sleeps on the UI thread"
  reason: "the event loop is the only execution context that owns the widget tree; cross-thread toolkit calls fail when the loop is not dispatching, and marshalling wrappers only re-enter this same scheduler"
  exception: none without a recorded supersession naming the verified gap
```

## Invariants
1. The UI thread MUST NOT block on long work, including thread joins.
2. UI updates MUST occur only on the main thread.
3. Workers MUST communicate through queue messages.
4. Workers MUST observe a shutdown/cancel event.
5. Cancellation waits MUST be interruptible; the cancellation owner MUST use `Event.wait(timeout)` or its declared equivalent and witness interruption on cancellation.
6. Status, progress, and result feedback MUST be posted through the queue and MUST NOT block.

## Required pattern
- The UI thread starts the worker and schedules `after(...)` to drain the queue.
- The worker posts bounded/coalesced progress, terminal results, errors, cancellation state, and run/report/log pointers to the queue.
- The drain callback MUST reschedule itself, store the returned `after()` identifier, and cancel that identifier in the window destroy handler.
- Worker joins MUST run off the UI thread on the shutdown path with a bounded timeout and a recorded result.
- The UI thread updates widgets only from drained messages.
- Stop and close handlers set the cancel event and return immediately; the UI polls completion via `after(...)`.

## Forbidden patterns
- Updating UI from a worker thread.
- Invoking any external-system interface from the UI thread.
- Shipping without a cancellation/shutdown mechanism.
- Calling `join()` from UI event handlers.
- Using `time.sleep(...)` in cancellable loops instead of `Event.wait(...)`.
- Calling `after(ms)` without a callback on the UI thread.

## Task scaffold
```
- worker mechanism:
- queue message schema:
- queue size and backpressure bounds:
- drain interval and drain identifier cancelled on destroy:
- stop/cancel mechanism (event + UI poll, no join on UI thread):
- interruptible waits (Event.wait):
- worker bounds (no unbounded threads, timeouts, guaranteed cleanup on cancel):
```
