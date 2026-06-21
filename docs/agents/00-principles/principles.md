---
doc_type: policy
ssot_owner: AGENTS.md
update_trigger: AGENTS.md requirements or referenced section headings change
---

# 00 - Principles (First Principles)

This doc extends the invariants in `AGENTS.md` with a practical first-principles operating protocol.
It is supporting guidance only.

## Protocol (Model -> Proof -> Change)
This protocol is supporting guidance only (non-normative) and is intended to prevent symptom-only fixes and reduce rework:

1) **Modeling** the system: inputs, outputs, side effects, boundaries.
2) **Tracing to Authority** (root-cause uplift):
   - Use `docs/agents/playbooks/rca-methods-template/rca-methods-template.md` for method steps/examples.
3) **Mapping SSOT jurisdictions and owners** (constants/config/rules/workflows/lifecycle utilities) and applying `AGENTS.md` Non-Negotiable #1 without parallel ownership.
4) **Deriving task authority** when the output is non-trivial:
   - Identify the minimum control artifact needed before final output can be trusted, such as an authority map, source map, extraction ledger, validation matrix, patch plan, or test fixture.
   - Generate the final output from that artifact and verify against it before claiming proof.
5) **Stating proof obligations**:
   - Preconditions: what must be true before work begins
   - Postconditions: what must be true after success
   - Failure modes: what can go wrong and how it should fail (explicitly)
   - Invariants + witnesses: define how correctness is measured and recorded
6) **Choosing verification first**:
   - Reference the repo-root `README.md` "Checks" (SSOT for commands).
   - A tight deterministic check is typically preferred when it satisfies the verification floors and proves the proof obligations.
   - A failure-path check is useful when feasible.
7) **Minimal implementation** (smallest diff that satisfies acceptance criteria).
8) **Verification and evidence reporting** (commands + outcomes, or deterministic manual checks if tooling is unavailable).

## Preferred patterns
- "Verify, then trust": confirm paths/symbols/dependencies with repo + tools.
- "Patch, do not fork": improve the current highest owning authority through explicit patch/supersession; do not create disconnected framework versions or parallel docs.
- Named rules for conditions (`is_*`, `require_*`, `validate_*`) in the appropriate SSOT owner to avoid duplicated `if` logic (see `docs/agents/20-sources-of-truth-map/sources-of-truth-map.md`).
- Workflows orchestrate; UI and scripts call workflows.
- Resource safety via context managers and `finally`.

## Where to encode guidance
- Core docs (`docs/agents/*.md`): principle-level policy and runbooks; avoid platform/tool specifics.
- Playbooks (`docs/agents/playbooks/playbooks_index.md` and child branches): copy/paste templates and checklists.
- Source-only assets (`docs/agents/skills/00-skill-standards/skill-standards.md`, `docs/agents/settings/00-settings-standards/settings-standards.md`): repo-owned reusable bundles and shared settings examples; reference core policy, do not duplicate it.

## Resource + speed discipline (reduce risk and time)
- For speed/scale work: performance model, safe optimizations, bounded concurrency.
- Bounded waits/timeouts and cancellation are required for blocking operations.
- For write workflows: use the two-phase commit pattern (no writes before validation).
- Transactional I/O (temp + atomic replace) is recommended where overwrites matter.
- Fast/complete discovery is supported by `docs/agents/05-context-retrieval/context-retrieval.md`.

## Communication (make work auditable)
- Clearly separating verified facts from assumptions/unknowns improves auditability.
- If ambiguity would materially change code, asking 1-3 clarifying questions reduces rework risk.
- Verification evidence (commands + outcomes) or deterministic manual checks should be included.

## Council evidence discipline (supporting)
- Council summaries are recorded-truth artifacts (D) that provide review witnesses for risk decisions.
- For non-micro changes, use the full council output fields.
- If `go_no_go` is `hold`, do not implement until reconciliation is complete or user risk acceptance is explicit.

## Non-normative anti-pattern examples
Examples (included here as guidance only):
- Copy/paste helpers.
- Duplicate constants/config defaults in multiple files/docs.
- Multiple lifecycle implementations for the same external system (Excel, GUI queue/drain, etc.).
