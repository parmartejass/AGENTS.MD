---
doc_type: policy
ssot_owner: docs/agents/governance/principles/principles.md
update_trigger: first-principles application mechanics or the baseline and supersession schema change
---

# Principles

Jurisdiction: how governing principles are applied to a task before and during non-trivial work, plus the baseline and supersession record schema.

## First-principles gate

- Required before any non-trivial implementation, mutation, or recommendation.
- Record every item below as task evidence.
- Return `hold` when a required item cannot be resolved.

## Model and scope

- Record the FP-04 and FP-07 items as task evidence.

## SSOT map

- Record each decision-critical fact, state, side effect, and witness against its owner.
- Record the public contract through which that owner is consumed.

## Root-cause uplift

- Trace every defect from symptom to the earliest defective authority, contract, or boundary.
- Fix at that authority. Add or strengthen invariants and validation there.
- Required: make the error class structurally impossible, not the single symptom.
- Record why upstream prevention is infeasible when a symptom-level patch is unavoidable.
- Record the residual error class left unprevented by any symptom-level patch.

## Structural consolidation

- Treat findings mapping to one invariant or authority as one defect.
- Consolidate the fix inside that authority owner.

## Derived task authority

- Required for any non-trivial output: identify or create the minimum task-specific control artifact.
- Control artifact forms: authority map, source map, extraction ledger, validation matrix, patch plan, test fixture.
- Generate the final output from that control artifact and verify against it.
- MUST treat the control artifact, not the final output, as the authority.

## Proof obligations

- Record preconditions and postconditions for each affected contract.
- Record the failure modes the change must cover.
- Required: each obligation names its owner and its witness.

## Verification

- Record exact commands or deterministic manual checks before claiming completion.
- Required: at least one failure-path check where feasible.

## Resource bounds

- Record timeouts and cancellation for every bounded operation.
- External resources MUST be released in `finally` or a context manager; Record the owned handle or PID and its cleanup result.

## Performance constraints

- Measure performance before selecting a design.
- Select algorithm and I/O strategy against the declared performance target.

## Design principles

- Apply DRY, KISS, YAGNI, Separation of Concerns, and Law of Demeter to generation and maintenance.
- Apply SOLID and dependency inversion to every module boundary.

## Delegated quality mechanics

- Convert reactive RCA learnings into proactive prevention.

## Stable baseline interface

```yaml
baseline:            # required in every interfaces owner and playbooks owner doc
  interface: <the stable, universal, direct interface chosen>
  pattern: <the required structural shape built on the interface>
  reason: <why it is the direct interface; what it avoids>
  exception: <the only permitted secondary path and its trigger, or none>
supersession:        # required whenever real work departs from a declared baseline
  baseline: <declared baseline being superseded>
  gap: <verified capability or performance gap>
  evidence: <witness proving the gap>
  preserved_outcomes: <correctness, preservation, explicit outcomes kept>
  proposed_baseline: <update to promote into the owning jurisdiction>
```

- Every interfaces owner and every playbooks owner MUST carry one `baseline` block.
- A governance owner that selects a tool interface MAY carry one sourced `baseline` block.
- The `pattern` key records the jurisdiction's required design shape. Body sections state its rules.
- A reserved jurisdiction MUST be declared on first use through one `supersession` record naming its proposed baseline.
