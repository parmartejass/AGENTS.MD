---
doc_type: policy
ssot_owner: docs/agents/interfaces/gui-toolkit/gui-toolkit.md
update_trigger: GUI toolkit baseline, UI-thread, or process window platform facts change
---

# GUI Toolkit

Jurisdiction: UI-thread safety, off-thread work, cancellation, and process window facts in desktop UI runtimes.

## Baseline
```yaml
baseline:
  interface: the toolkit's native main-thread scheduler
  pattern: "widget tree touched only on the UI thread; long work off-thread, bounded and cancellable; UI thread never blocks"
  reason: "the event loop is the only execution context that owns the widget tree; cross-thread toolkit calls fail when the loop is not dispatching, and marshalling wrappers only re-enter this same scheduler"
  exception: none without a recorded supersession naming the verified gap
```

## UI thread
- Workers MUST stop within a bounded time after cancellation.
- Scheduled UI callbacks MUST be cancelled before their widgets are destroyed.
- Process DPI awareness cannot change after the first window exists.
