---
doc_type: policy
ssot_owner: AGENTS.md
update_trigger: AGENTS.md objective/invariants change
---

# 00 - Principles (First Principles)

## Invariants (SSOT)
The normative invariants live in `AGENTS.md` under:
- "Objective"
- "Non-Negotiables (Hard Gates)"

This doc extends those invariants with a practical first-principles operating protocol.

## Protocol (Model -> Proof -> Change)
Use this to prevent "fixing symptoms" and to reduce rework:

1) **Model** the system: inputs, outputs, side effects, boundaries.
2) **Trace to Authority** (canonical: AGENTS.md "Root-cause uplift"):
   - Don't patch at the symptom location.
   - Trace upstream to the **authority point** (config, schema, boundary, contract) where this error class should be structurally prevented.
   - Fix there: one fix at authority prevents N errors (leverage).
3) **Map SSOT owners** (constants/config/rules/workflows/lifecycle utilities) and extend them (no parallel ownership).
4) **State proof obligations**:
   - Preconditions: what must be true before work begins
   - Postconditions: what must be true after success
   - Failure modes: what can go wrong and how it should fail (explicitly)
5) **Choose verification** first:
   - tightest deterministic check available (tests > scenario run > lint/static check > manual steps)
   - include at least one failure-path check when feasible
6) **Implement minimally** (smallest diff that satisfies acceptance criteria).
7) **Verify and report evidence** (commands + outcomes, or deterministic manual checks if tooling is unavailable).

## Preferred patterns
- “Verify, then trust”: confirm paths/symbols/dependencies with repo + tools.
- Named rules for conditions (`is_*`, `require_*`, `validate_*`) to avoid duplicated `if` logic.
- Workflows orchestrate; UI and scripts call workflows.
- Resource safety via context managers and `finally`.

## Where to encode guidance
- Core docs (`docs/agents/*.md`): principle-level policy and runbooks; avoid platform/tool specifics.
- Playbooks (`docs/agents/playbooks/*.md`): copy/paste templates and checklists.
- Skills (`docs/agents/skills/*.md`): platform adapters + skill standards; reference core policy, do not duplicate it.

## Resource + speed discipline (reduce risk and time)
- When speed/scale is a goal, follow `AGENTS.md` "Performance & Speed (When Relevant)" (performance model, safe optimizations, bounded concurrency).
- Prefer bounded waits/timeouts and cancellation for anything that can block.
- Keep I/O transactional (temp + atomic replace) where overwrites matter.
- Keep discovery fast and complete: follow `docs/agents/05-context-retrieval.md`.

## Communication (make work auditable)
- Clearly separate what is verified vs assumed/unknown.
- If ambiguity would materially change code, stop and ask 1-3 clarifying questions.
- Always include verification evidence (commands + outcomes) or deterministic manual checks.

## Reject patterns
- Copy/paste helpers.
- Duplicate constants/config defaults in multiple files/docs.
- Multiple lifecycle implementations for the same external system (Excel, GUI queue/drain, etc.).
