---
doc_type: reference
ssot_owner: myapp/runner/runner_main.py
update_trigger: workflow behavior or scope changes
---

# Goal

## Objective

Provide a dual-entry automation where:
- users can run a GUI, and
- agents/tests can run a CLI,

while **both** call the same orchestration entrypoint: `myapp.runner.runner_main.run_job()`.

## Acceptance criteria (minimum)

- At least one happy-path scenario runs end-to-end on real files.
- At least one failure-path scenario runs deterministically.
- No `print()` in runtime code; logs include start/fail boundaries with context.
- Cancellation exists in the GUI and is observed by the worker/core loop.

## Durable intent

- Preserve a dependency-minimal reference implementation for agents to copy by pattern after target-repo discovery.
- Keep template project docs aligned with the governance pack's durable owner-doc truth model without making the example a policy owner.

## Boundary
- This root doc owns template purpose, success criteria, non-goals, and verification intent.
- It does not own reusable governance policy, template architecture, data-truth routing, or operational learnings.

## When to create a branch-local owner subdoc
- Create a goal subdoc when a durable template intent cluster would bloat or blur this root objective.
- Do not use goal subdocs as task records or change history.

## Current Summary
- The template demonstrates a dual-entry GUI/CLI pattern with one shared runner contract.
- No branch-local goal subdocs are declared.

## Branch-local owner subdocs
- None currently declared.

## Non-goals

- This template does not prescribe a domain (Excel, PDFs, etc.). Replace `myapp/core/` with your domain logic.
