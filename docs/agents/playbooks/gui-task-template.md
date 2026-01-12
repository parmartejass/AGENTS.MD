---
doc_type: playbook
ssot_owner: AGENTS.md
update_trigger: GUI threading/cancellation expectations change
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

## SSOT mapping (fill with exact repo locations)
- workflow entrypoint:
- rules used:
- config keys used:
- GUI queue/drain owner:

## Acceptance checks
- UI never blocks:
- no UI updates off main thread:
- cancel stops worker:
