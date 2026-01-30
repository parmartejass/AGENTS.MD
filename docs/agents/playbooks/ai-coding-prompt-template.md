---
doc_type: playbook
ssot_owner: AGENTS.md
update_trigger: prompt structure or verification expectations change
---

# Playbook - AI Coding Prompt Template

Use this when you need a structured prompt for an AI assistant (Copilot Chat, Claude, etc.).
For bugfixes, also fill `docs/agents/playbooks/bugfix-template.md`.

Use when:
- You need a structured prompt for an AI assistant.
- Task matches profile `ai_prompt_authoring` in `agents-manifest.yaml`.

## Prompt skeleton (copy/paste)

```
Hard gates:
- Read and follow `AGENTS.md` (SSOT). If you cannot access it, ask for it before doing any work.

Task type: <feature|bugfix|refactor>

Goal:
Acceptance criteria:
- ...

Repo context (verified):
- Files to read first:
- Existing SSOT owners to extend:
- Entrypoint/workflow this must be wired through:
- Injection profiles matched (from `agents-manifest.yaml`):

First-principles artifacts:
- Model (inputs/outputs/side effects/boundaries):
- SSOT map (constants/config/rules/workflows/lifecycle):
- Proof obligations (preconditions/postconditions/failure modes):

Constraints:
- Follow `AGENTS.md` (SSOT): verify with tools, avoid duplicates, explicit failures, resource safety.
- Minimal diff; no unrelated refactors.
- No new dependencies unless explicitly approved.

Verification:
- Commands to run:
- If no automated tests: deterministic manual check steps:

Review / Validate (required before final response):
- Use `docs/agents/15-stuck-in-loop-generate-fresh-restart-prompt.md` for repetition/verification contradictions.
- Use `docs/agents/90-release-checklist.md` as the final pass (reference only; do not duplicate policies).

Output format:
1) Approach summary (<= 100 words)
2) Changes made (file list)
3) Assumptions / Unknowns
```

## Optional: Review → Loop Prompt + XML Confirmation File

Use this when you want a *supervisor loop* (queue messages / repeated runs) and a deterministic, file-based stop signal.
This is optional: only use it when the task is large/mechanical enough to benefit from iteration.

### What the assistant must produce (artifacts)
- `loop_prompt.md`: a single prompt you can feed repeatedly in a loop until done.
- `run_confirmation.xml`: an XML “stop file” that the assistant updates when complete.

### `run_confirmation.xml` template (copy/paste)
Example (you choose the path, e.g. `runs/<slug>/run_confirmation.xml`):

```xml
<run_confirmation version="1">
  <id>CHANGE_ME_UNIQUE_ID</id>
  <request>CHANGE_ME_USER_REQUEST_SUMMARY</request>
  <status>PENDING</status>
  <completion_token>&lt;promise&gt;COMPLETE&lt;/promise&gt;</completion_token>
  <updated_utc>1970-01-01T00:00:00Z</updated_utc>
  <evidence>
    <item>Empty until verified.</item>
  </evidence>
</run_confirmation>
```

### `loop_prompt.md` template (copy/paste)
The loop prompt must:
- Force a *review/discovery pass* first (map files/symbols/scenarios; no edits yet).
- Then implement minimally (SSOT adoption; no duplicates).
- Then verify deterministically.
- Only when verification passes: update `run_confirmation.xml` to `COMPLETE` and output the exact completion token.

```
Hard gates:
- Read and follow `AGENTS.md` (SSOT). If you cannot access it, ask for it before doing any work.
- Follow `AGENTS.md` Mandatory Execution Loop and Context Injection Procedure.

Task type: <feature|bugfix|refactor|review>
User request:
<paste request verbatim>

Run artifacts (must create/update these files):
- loop prompt (this file): <path to loop_prompt.md>
- confirmation file: <path to run_confirmation.xml>

Phase 1 — Review (no edits):
- Enumerate all relevant instances/entrypoints/call-sites/config/constants/rules/tests/scenarios linked to the request.
- Produce a verified file list to read next + `rg` search terms you used.
- Identify SSOT owners to extend (no parallel utilities/docs).
- If ambiguity remains that would change code materially: stop and ask 1–3 questions.

Phase 2 — Implement (minimal diff):
- Implement the smallest set of changes that satisfies the acceptance criteria.
- Do not add dependencies unless explicitly approved.

Acceptance criteria:
- <fill these in; must be objectively verifiable>

Verification (must run):
- <exact command(s) the agent will run>

Stop conditions:
- If you detect the same failure twice with the same root cause, STOP and output the filled restart prompt template from `docs/agents/15-stuck-in-loop-generate-fresh-restart-prompt.md`.

Completion protocol:
- If (and only if) all verification commands pass:
  - Update the confirmation file:
    - `<status>` -> `COMPLETE`
    - `<updated_utc>` -> current UTC timestamp
    - add 1–3 evidence items (commands run + outcomes)
  - Output exactly: <promise>COMPLETE</promise>
```

## Review / Validate (single step)
Use the "Review / Validate" section in the prompt skeleton above; do not add separate checklists here.
