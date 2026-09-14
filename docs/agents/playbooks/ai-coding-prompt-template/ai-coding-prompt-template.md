---
doc_type: playbook
ssot_owner: AGENTS.md
update_trigger: prompt input scaffold or verification-input expectations change
---

# Playbook - AI Coding Prompt Template

Use this playbook to supply complete task intent to an AI coding workflow without copying or redefining the workflow itself. `AGENTS.md` owns constitutional hard gates, and `Orchestration.md` owns every role, plan, council, execution, review, correction, and terminal mechanic.

For bugfixes, also provide the evidence inputs requested by `docs/agents/playbooks/bugfix-template/bugfix-template.md`.

## Prompt skeleton (copy/paste)

```text
Required owners:
- Read and follow `AGENTS.md` before any work.
- Read and follow `Orchestration.md` before delegation, planning, mutation, or review.
- Apply the complete binding user-intent and user-decision precedence rules in `AGENTS.md` to the request below and earlier binding user messages.
- If a required owner is inaccessible or conflicts with the request, report the conflict through Main; do not invent a substitute rule.

Task type: <feature|bugfix|refactor|review>

Complete user request:
<paste without dropping binding details>

Goal:
- <desired outcome>

Acceptance evidence:
- <objective evidence that proves success>

Known in scope:
- <paths, components, workflows, or user-visible behavior>

Known out of scope / non-goals:
- <explicit exclusions>

Authorized mutations and side effects:
- <repository writes, external actions, or none>

Constraints:
- <security, compatibility, performance, resource, dependency, or timing constraints>

Known risks or failure conditions:
- <conditions that must fail explicitly>

Carry-forward evidence inputs (requester supplies when relevant; non-authoritative; record provenance and relevance):
- Verified failure evidence:
- Prior failed attempts and observed outcomes:
- Known-bad approaches or assumptions:
- Open unknowns:

Repository authority hints (non-binding until verified):
- <paths, entrypoints, config owners, or Unknown>

Verification intent:
- Use the commands owned by `README.md` section "Checks" when applicable.
- <targeted behavior/failure-path evidence required>

Bugfix evidence inputs (when applicable):
- Symptom/manifestation:
- Expected vs actual:
- Deterministic reproduction or MRE:
- Regression fixture:
- Disconfirming edge case:
- Failure-path expectation:

Requested user-facing output:
- <format, artifact, or concise summary>
```

## Use rules

- Supply mutable facts through their declared source/config owner under `AGENTS.md` FP-10 and FP-22.
- Apply the automatic durable-record retrieval and maintenance duties in `AGENTS.md`; this scaffold does not require the user to identify owner files or separately request documentation updates.
- Mark unverified repository hints as `Unknown` instead of presenting them as authority.
- Carry-forward evidence preserves observed failures, failed attempts, known-bad assumptions, and open unknowns as non-authoritative task input for a later user-started workflow. It grants no execution or continuation authority.
- Plan persistence, scope changes, correction limits, and terminal behavior follow `Orchestration.md`; this scaffold defines no parallel lifecycle.

## Review and validation

Follow `Orchestration.md` for review and workflow decisions, and `docs/agents/90-release-checklist/release-checklist.md` for release evidence.
