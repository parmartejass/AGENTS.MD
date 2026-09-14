---
doc_type: policy
ssot_owner: docs/agents/00-principles/evidence/evidence.md
update_trigger: truth layers, witness duties, verification floors, or performance evidence boundaries change
---

# Evidence and Verification

This delegated owner applies `AGENTS.md` FP-01, FP-03, and FP-32 through FP-34. Agent roles and terminal decisions remain owned by `Orchestration.md`.

## First-Principles + SSOT + Evidence Model (Hard Gate)

Truth layers (use these terms):
- Runtime truth (R): what actually happens at runtime (processes, files, memory, handles).
- Semantic truth (S): what the system is meant to do (invariants, contracts, rules).
- Recorded truth (D): what artifacts claim (configs, logs, reports, docs).

Implications:
- First principles defines S (invariants). SSOT governs authority in D (consistency, not correctness).
- Instrumentation binds R to S and D. An invariant is invalid unless it has a measurable witness recorded in D.
- SSOT does not guarantee correctness; it guarantees that one authority wins when records disagree.

### Invariants + Witnesses (Required)
- For every change, list the invariants it affects or relies on.
- Use these categories when applicable: data, ordering, atomicity, idempotency, lifecycle, observability.
- Each invariant must have a witness: what is measured, where it is recorded, and the pass criteria.
- Witnesses must be deterministically verifiable via tools or explicit manual checks.

### Authority-Constrained Reasoning (Hard Gate)
- Apply FP-01 and FP-33 through the following authority-application witness; acknowledgment is not evidence.
- Use authority inputs as binding minimum constraints for every decision-critical claim. A stronger task-specific design is allowed only when it is explicitly authority-preserving and does not change future allowed behavior without an owner update.
- For every non-trivial plan, implementation, review, remediation, or final decision, record an authority-application witness with `authority_inputs`, `applied_obligations`, `decision_basis`, and `evidence`.
- Classify each decision-critical design move, recommendation, finding, or go/no-go basis as `authority_required`, `authority_preserving`, `owner_update_required`, `authority_conflict`, or `unsupported`.
- Fail closed with `hold` for missing relevant authority inputs or obligations, decision-critical `unsupported`, `authority_conflict`, or unresolved `owner_update_required`; "read and followed docs" is not a witness.

### Scannable Output Shape (Hard Gate)
- Non-trivial plans, reviews, implementation records, prompt scaffolds, agent reports, and final reports must use a task-derived scannable structure, not undifferentiated prose.
- Make decision-critical inputs, SSOT owners, decisions/changes, evidence/witnesses, risks, status/go-no-go, and gaps/unknowns visually detectable; tiny conversational responses may stay prose-only when none of those are in scope.


### Verification Floors (Hard Gate)
- Verification commands are a single SSOT in the repo: the README "Checks" section. Do not invent commands. If a required verification step is repeatable, add the command to README before running; otherwise record deterministic manual steps in the report.
- Minimums by change type (in addition to repo-specific checks):
  - Docs-only or formatting: run doc-related checks if present; otherwise record a deterministic manual check.
  - Behavior-neutral code change: run baseline checks relevant to the touched area plus at least one targeted smoke test if available; if none, record a deterministic manual check.
  - Behavior change or new feature: baseline checks plus targeted tests covering the new behavior and at least one failure-path check (see I/O guidance in `docs/agents/80-testing-real-files/testing-real-files.md` when applicable).
  - Bugfix/regression: follow `docs/agents/00-principles/diagnosis/diagnosis.md` (no extra exceptions) and run applicable tests, including deterministic MRE witness, regression test, at least one disconfirming edge/adversarial test, and at least one failure-path check. Durable bug/regression truth belongs in the highest owning project doc, while executable evidence belongs in tests, fixtures, and verification output.
- Shift-left quality baseline (new features/behavior changes): before merge, encode prevention with tests (TDD/BDD where feasible), design pre-mortem or failure-mode review, relevant static checks, contract tests on module/service boundaries, and observability-by-design.
- Coverage/fixtures:
  - If coverage thresholds exist (CI/config/tooling), meet them and do not lower them.
  - If no coverage thresholds exist, require fixture-backed tests: regression fixture for bugfixes; representative scenario/fixture for new features when feasible.
  - Fixtures must be deterministic and sanitized (no secrets/PII/licensed data).
- For changes affecting I/O or file processing, follow `docs/agents/80-testing-real-files/testing-real-files.md` (supporting guidance).


### Rewrite Risk Policy
Large rewrites are risk amplification unless all are true:
- pre-existing invariants are enumerated and preserved
- old vs new outputs are comparable on frozen fixtures
- staged rollout and rollback exist
- performance/resource invariants are measured

The selected rewrite scope MUST satisfy these witnesses and FP-08, FP-09, and FP-34.


### 9) Performance & Speed (When Relevant)

FP-03 owns timing requirements. Before optimizing a processing path, record workload bounds, bottleneck hypothesis, cache/batch/chunk/queue strategy, invalidation, memory/concurrency limits, deterministic ordering, cancellation, and cleanup. Measure repository-controlled paths against the applicable requirement with output-equivalence and failure-path witnesses. Report model/platform/network timings outside repository instrumentation as unverified; do not claim a static check proves them. These evidence boundaries do not relax FP-03.

