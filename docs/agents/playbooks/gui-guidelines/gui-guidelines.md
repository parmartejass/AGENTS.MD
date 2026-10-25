---
doc_type: playbook
ssot_owner: docs/agents/playbooks/gui-guidelines/gui-guidelines.md
update_trigger: presentation, feedback, or UI requirements scaffold rules change
---

# GUI Guidelines

Jurisdiction: presentation and feedback design and the UI requirements scaffold.

```yaml
baseline:
  interface: the toolkit's native widgets, layout, and theme
  pattern: "visible state presents drained run events and the owner-backed snapshot as recorded; no UI-local reinterpretation; every style value resolves from the declared design-system token set, never an inline literal"
  reason: "native widgets keep platform behaviour and input handling; one vocabulary keeps the visible state truthful; token resolution keeps one visual system across screens"
  exception: "a theme layer over the same native widgets is permitted; substituting a canvas-drawn widget set requires a recorded supersession"
```

- An operator-facing capability MUST expose a non-terminal surface (GUI or workbook template) bound to the same config snapshot. It MUST count as complete only with that surface.

## Feedback
- Status, progress, and result feedback MUST stay current.
- The UI MUST present the workflow result exactly as recorded.
- The visible terminal summary MUST use the run-outcomes vocabulary and counts verbatim.
- A determinate progress indicator MUST be driven by a known denominator. Unknown-duration work MUST use the indeterminate form and MUST show no percentage.
- Error text MUST name what failed and the corrective action. Generic text such as "invalid input" fails this rule.

## UI requirements scaffold
```
- controls:
- where each run-outcomes user-facing summary element is shown:
- empty state per view (what is missing, why, next action):
- cancel behavior (as the user sees it):
- acceptance: every run-outcomes user-facing summary element is visible:
```
