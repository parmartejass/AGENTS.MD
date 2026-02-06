---
doc_type: policy
ssot_owner: AGENTS.md
update_trigger: AGENTS.md requirements or referenced section headings change
---

# 00 - Principles (First Principles)

## Invariants (SSOT: `AGENTS.md`)
Normative requirements live in `AGENTS.md` (and win on conflict). Start with:
- "Objective"
- "Non-Negotiables (Hard Gates)"

This doc extends those invariants with a practical first-principles operating protocol.
It is supporting guidance only; follow `AGENTS.md` "Mandatory Execution Loop (Follow For Every Task)" for the required end-to-end procedure.

## Hard gate references (SSOT: `AGENTS.md`)
Index only (do not restate requirements here):
- "Prime Directive: Verify, Then Trust"
- "First-Principles Protocol (Hard Gate)"
- "First-Principles + SSOT + Evidence Model (Hard Gate)" (truth layers R/S/D; invariants + witnesses)
- "Authority Graph (Required for non-trivial systems)" (see also `docs/agents/35-authority-bounded-modules.md`)
- "Workflow State Machine + Two-Phase Commit (When writes occur)"
- "Defect vocabulary + root-cause fix policy" (under `AGENTS.md` "First-Principles Protocol (Hard Gate)" and "Bias-Resistant Debugging (Hard Gate)")
- "RCA workflow + method stack (Fishbone/Pareto/5 Whys/FMEA)" (under `AGENTS.md` "Bias-Resistant Debugging (Hard Gate)")
- "Bias-Resistant Debugging (Hard Gate)"
- "Verification Floors (Hard Gate)"
- "Shift-left quality baseline" (under `AGENTS.md` "Verification Floors (Hard Gate)")
- "Rewrite Risk Policy"
- "Mandatory modularity and reusability checklist" (under `AGENTS.md` "Mandatory Modularity + SOLID/DI (Authority Bloat Prevention)")
- "Subagent Council (Hard Gate)"
- "Change Contract (Required for any change record)"

## Protocol (Model -> Proof -> Change)
This protocol is supporting guidance only (non-normative) and is intended to prevent symptom-only fixes and reduce rework:

1) **Modeling** the system: inputs, outputs, side effects, boundaries.
2) **Tracing to Authority** (canonical: AGENTS.md "Root-cause uplift"):
   - It is preferable not to patch at the symptom location; if a symptom-level patch is unavoidable, record why upstream prevention is infeasible and what error class remains unprevented.
   - Trace upstream to the **authority point** (config, schema, boundary, contract) where this error class should be structurally prevented.
   - Fix there when feasible: one fix at authority prevents N errors (leverage).
3) **Mapping SSOT owners** (constants/config/rules/workflows/lifecycle utilities) and extending them (no parallel ownership).
4) **Stating proof obligations**:
   - Preconditions: what must be true before work begins
   - Postconditions: what must be true after success
   - Failure modes: what can go wrong and how it should fail (explicitly)
   - Invariants + witnesses: follow `AGENTS.md` "Invariants + Witnesses (Required)" (define how correctness is measured and recorded)
5) **Choosing verification first**:
   - Reference `AGENTS.md` "Verification Floors (Hard Gate)" and the repo-root `README.md` "Checks" (SSOT for commands).
   - A tight deterministic check is typically preferred when it satisfies the verification floors and proves the proof obligations.
   - A failure-path check is useful when feasible.
6) **Minimal implementation** (smallest diff that satisfies acceptance criteria).
7) **Verification and evidence reporting** (commands + outcomes, or deterministic manual checks if tooling is unavailable).

## Preferred patterns
- "Verify, then trust": confirm paths/symbols/dependencies with repo + tools.
- Named rules for conditions (`is_*`, `require_*`, `validate_*`) in the appropriate SSOT owner to avoid duplicated `if` logic (see `docs/agents/20-sources-of-truth-map.md`).
- Workflows orchestrate; UI and scripts call workflows.
- Resource safety via context managers and `finally`.

## Where to encode guidance
- Core docs (`docs/agents/*.md`): principle-level policy and runbooks; avoid platform/tool specifics.
- Playbooks (`docs/agents/playbooks/*.md`): copy/paste templates and checklists.
- Skills (`docs/agents/skills/00-skill-standards.md`): platform adapters + skill standards; reference core policy, do not duplicate it.

## Resource + speed discipline (reduce risk and time)
- For speed/scale work, the governing policy is `AGENTS.md` "Performance & Speed (When Relevant)" (performance model, safe optimizations, bounded concurrency).
- Bounded waits/timeouts and cancellation are recommended for blocking operations.
- For write workflows, the governing policy is `AGENTS.md` "Workflow State Machine + Two-Phase Commit (When writes occur)".
- Transactional I/O (temp + atomic replace) is recommended where overwrites matter.
- Fast/complete discovery is supported by `docs/agents/05-context-retrieval.md`.

## Communication (make work auditable)
- Clearly separating verified facts from assumptions/unknowns improves auditability.
- If ambiguity would materially change code, asking 1-3 clarifying questions reduces rework risk.
- Verification evidence (commands + outcomes) or deterministic manual checks should be included.

## Non-normative anti-pattern examples
Examples (mapped to `AGENTS.md` hard gates and included here as guidance only):
- Copy/paste helpers.
- Duplicate constants/config defaults in multiple files/docs.
- Multiple lifecycle implementations for the same external system (Excel, GUI queue/drain, etc.).
