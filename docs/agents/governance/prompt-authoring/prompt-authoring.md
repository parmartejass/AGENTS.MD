---
doc_type: playbook
ssot_owner: docs/agents/governance/prompt-authoring/prompt-authoring.md
update_trigger: prompt input scaffold or verification-input expectations change
---

# Prompt Authoring

Jurisdiction: the task-intent scaffold supplied to an AI coding workflow.

## Task scaffold

```text
Required owners:
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

Source boundary (tools and roots the executor may use; sources it reads itself versus supplied here):
- <tools, roots, or none>

Task boundary (sibling work this task must not duplicate; stop condition):
- <boundary and stop condition>

Verification intent:
- Use the commands owned by `README.md` section "Checks" when applicable.
- <targeted behavior/failure-path evidence required>

Bugfix evidence inputs (when applicable; the bugfix jurisdiction owns the evidence floor):
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

- Mutable facts MUST be supplied through their declared source or config owner.
- Replies to the user MUST use few words per line and one item per line; narrative MUST NOT replace a jurisdiction-named finding.
- A question to the user MUST be a jurisdiction-level choice with a named default; open technical follow-ups are prohibited.
- The scaffold MUST NOT require the user to identify owner files.
- The scaffold MUST NOT require the user to separately request documentation updates.
- Unverified repository hints MUST be marked `Unknown`.
- Presenting an unverified hint as authority is Prohibited.
- Carry-forward evidence preserves failures, failed attempts, known-bad assumptions, and open unknowns.
- Carry-forward evidence is non-authoritative task input for a later user-started workflow.
- Carry-forward evidence grants no execution or continuation authority.
