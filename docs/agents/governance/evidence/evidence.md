---
doc_type: policy
ssot_owner: docs/agents/governance/evidence/evidence.md
update_trigger: truth layers, witness duties, verification floors, or performance evidence boundaries change
---

# Evidence

Jurisdiction: truth layers, invariant witnesses, authority-application evidence, verification floors, rewrite risk, performance measurement, and the scannable output and change-contract scaffolds.

## Truth layers

- Runtime truth (R): what happens at runtime - processes, files, memory, handles.
- Semantic truth (S): what the system must do - invariants, contracts, rules.
- Recorded truth (D): what artifacts claim - configs, logs, reports, docs.
- First principles define S; SSOT governs authority in D.
- Instrumentation binds R to S and D.
- An invariant without a measurable witness recorded in D is invalid.
- SSOT guarantees one authority wins on disagreement, not correctness.

## Invariants and witnesses

- Required: list every invariant a change affects or relies on.
- Use these categories: data, ordering, atomicity, idempotency, lifecycle, observability.
- Each invariant MUST declare what is measured, where it is recorded, and the pass criteria.
- Witnesses MUST be deterministically verifiable by tool or explicit manual check.

## Authority-constrained reasoning

- Treat authority inputs as binding minimum constraints for every decision-critical claim.
- A stronger task-specific design is permitted only when authority-preserving.
- Prohibited: changing future allowed behavior without an owner update.
- Required for every non-trivial plan, implementation, review, remediation, or final decision: an authority-application witness.

Authority-application witness fields:

| Field | Content |
|---|---|
| `authority_inputs` | Owners and obligations consulted, by path. |
| `applied_obligations` | Which obligations bound this decision. |
| `decision_basis` | The rule that decided the outcome. |
| `evidence` | Measured witness or command output proving application. |

- Classify each decision-critical move, recommendation, finding, or go/no-go basis as `authority_required`, `authority_preserving`, `owner_update_required`, `authority_conflict`, or `unsupported`.
- Return `hold` for missing relevant authority inputs or obligations.
- Return `hold` for decision-critical `unsupported`, `authority_conflict`, or unresolved `owner_update_required`.
- Prohibited: acknowledgment, including "read and followed docs", as a witness.

## Scannable output shape

- Non-trivial plans, reviews, implementation records, prompt scaffolds, and reports MUST use task-derived scannable structure.
- Prohibited: undifferentiated prose for those outputs.
- Make inputs, SSOT owners, decisions, evidence, risks, status, and gaps visually detectable.
- Tiny conversational responses stay prose-only when none of those are in scope.

## Verification floors

- The repo-root `README.md` Checks section is the single command SSOT.
- Prohibited: inventing verification commands.
- Add a repeatable command to README before running it; otherwise record deterministic manual steps.
- Docs-only or formatting: run doc checks if present; otherwise record a deterministic manual check.
- Behavior-neutral code change: baseline checks for the touched area plus one targeted smoke test; otherwise a deterministic manual check.
- Behavior change or new feature: baseline checks, targeted tests for the new behavior, and one failure-path check.
- Record durable bug and regression truth in the highest owning project doc; keep executable evidence in tests, fixtures, and output.
- Shift-left baseline for new features and behavior changes: tests before merge, test-first where feasible, pre-mortem or failure-mode review, static checks, boundary contract tests, observability by design.
- I/O or file-processing changes MUST meet the testing jurisdiction's real-file verification minimums.

## Rewrite risk policy

- A large rewrite amplifies risk by discarding proven invariants and is Prohibited unless all four witnesses hold.
- Pre-existing invariants enumerated and preserved.
- Old and new outputs comparable on frozen fixtures.
- Staged rollout and rollback exist.
- Performance and resource invariants measured.

## Performance and speed

- Record workload bounds before selecting a process design.
- Record the bottleneck hypothesis - CPU, I/O, or round-trips.
- Record the applicable cache, batch, chunk, or queue strategy and its invalidation rule.
- Record memory and concurrency limits, deterministic ordering, cancellation, and cleanup.
- Measure the complete operation: request, preparation, queue wait, processing, I/O, persistence, verification, cleanup.
- Retain component timings alongside the end-to-end result.
- Classify every measured operation against the constitutional near-instant completion target.
- Preserve output-equivalence and failure-path witnesses when optimizing.
- Report excluded or uninstrumented work as unverified, including model, platform, and network work.
- A passing structural or reporting check does not establish performance attainment.
- Workload bounds and instrumentation limits exempt no process from the performance target.

## Performance hotspot scaffold

- Trigger: manifest profile `perf_hotspots`.
- Required when the task targets a known hotspot such as per-row loops or per-cell external calls; measure and locate the hotspot first, then record only the minimal lever set.

```
- goal: required outcome and timing witness
- preservation_constraints: correctness/safety invariants that must survive
- slow_class: CPU vs I/O vs round-trips
- hotspot_location: symbol + file path + call sites
- size_model: rows/items/files with worst-case bounds
- lever_bulk: bulk ops; no per-cell COM, no row-wise dataframe loops
- lever_cache: deterministic precomputed maps; key, scope, max size, invalidation
- lever_scan: compute bounds once; remove repeated scans and parse passes
- lever_batch: chunk with memory caps, timeouts, cancellation-aware cleanup
- lever_concurrency: bounded workers, stable ordering, no races on shared outputs
- precondition: inputs validated; schemas/headers known; config owners identified
- postcondition: outputs identical or per spec; outcomes logged; resources cleaned
- failure_path: one deterministic failure run (missing input / invalid header / permission denied)
- timing_capture: same inputs, same environment; what measured, where recorded
- bounds_witness: rows/items/files/bytes, memory/concurrency limits, chunk sizes
- cache_batch_witness: cache scope/key/invalidation and batch strategy used
- complexity_reasoning: big-O plus dominant constants when benchmarks are infeasible
- correctness_witness: output equivalence on frozen representative fixtures
- disconfirming_check: one edge case that could invalidate the optimization hypothesis
- guard_check: measured improvement confirmed; full or smoke suite confirming nothing outside the hotspot broke
```

## Change contract scaffold

- Required for behavior changes and bugfixes; each filled field cites its owner and records scoped non-applicability.

```
- A_observed: observed behavior
- A_expected: expected behavior
- A_scope: rows/files/modules/users impacted
- A_blast_radius: what else the change could impact
- B_data_invariants: INV-D1..n
- B_ordering_invariants: INV-O1..n
- B_atomicity_invariants: INV-A1..n (all-or-nothing / two-phase commit)
- B_idempotency_invariants: INV-I1..n
- B_lifecycle_invariants: INV-L1..n (external resources)
- B_observability_invariants: INV-OBS1..n (outcome/log completeness)
- C_witnesses: one row per invariant (ID | signal | where recorded | pass criteria)
- D_authority_impacted: config / parser / writer / lifecycle / logger / reporting (Y or N each)
- D_canonical_key_location: where the canonical definition lives when config is impacted
- D_no_duplication_proof: removed / replaced by
- G_rollout_owner: declared rollout or config owner and selected path
- G_rollback_plan: how the change is reverted
- G_data_safety: atomic writes, backups, temp plus rename
```

Example witness rows (non-normative):

| Invariant ID | Witness signal | Where recorded | Pass criteria |
|---|---|---|---|
| INV-L1 | Owned external PID exit and unrelated PID preservation | lifecycle-owner record | owned PID exited; unrelated processes preserved |
| INV-A1 | No writes before validation complete | log.phase sequence | no write events before VALIDATED |

- Closure: every listed invariant has a passing witness and the applicable verification floor is met.
