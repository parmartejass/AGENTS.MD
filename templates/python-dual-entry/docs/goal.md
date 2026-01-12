---
doc_type: reference
ssot_owner: myapp/runner.py
update_trigger: workflow behavior or scope changes
---

# Goal

## Objective

Provide a dual-entry automation where:
- users can run a GUI, and
- agents/tests can run a CLI,

while **both** call the same orchestration entrypoint: `myapp.runner.run_job()`.

## Acceptance criteria (minimum)

- At least one happy-path scenario runs end-to-end on real files.
- At least one failure-path scenario runs deterministically.
- No `print()` in runtime code; logs include start/fail boundaries with context.
- Cancellation exists in the GUI and is observed by the worker/core loop.

## Non-goals

- This template does not prescribe a domain (Excel, PDFs, etc.). Replace `myapp/core/` with your domain logic.

