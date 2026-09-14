---
doc_type: playbook
ssot_owner: AGENTS.md
update_trigger: performance/speed guidance changes OR new recurring hotspot patterns emerge
---

# Playbook — Performance Hotspots (Safe Optimizations)

Use when:
- Task matches profile `perf_hotspots` in `agents-manifest.yaml` (e.g., `iterrows`, per-cell Excel loops).

## Governing evidence

This task scaffold applies `AGENTS.md` Fundamental Principles and Verification Floors. Record task type, blast radius, applicable owner obligations, and witnesses. Bugfix evidence uses `docs/agents/playbooks/bugfix-template/bugfix-template.md`; implementation design uses `docs/agents/35-coding-principles/coding-principles.md`. Agent lifecycle and authorization remain owned by `Orchestration.md`.

## Goal
- Required outcome and timing witness under `AGENTS.md` FP-02 and FP-03:
- Applicable workload and preservation constraints:

## Hotspot identification (verify first)
- What is slow (CPU vs I/O vs COM/network round-trips):
- Where is the loop/scan (symbol + file path + call sites):
- Size model (rows/items/files; worst-case bounds):

## Safe optimization levers (pick the minimal set)
- Governing performance contract and witness: `AGENTS.md` FP-03 and Performance & Speed.
- Replace per-item round-trips with bulk operations (Excel: avoid per-cell COM calls; dataframes: avoid row-wise Python loops when a vectorized/groupby/join exists).
- Cache expensive lookups deterministically (precompute maps/indices); define cache key/scope, max size, and invalidation when inputs/schema/ranges change.
- Reduce repeated scans (compute bounds once; avoid repeated `rg`/directory walks/parse passes).
- Batch/chunk processing with explicit bounds (memory caps, timeouts, cancellation-aware cleanup).
- Queue work only with explicit bounds, backpressure/coalescing, and deterministic output ordering.
- Keep concurrency bounded and output deterministic (stable ordering rules; avoid races on shared outputs).

## Proof obligations
- Preconditions: inputs validated; schemas/headers known; config/SSOT owners identified.
- Postconditions: outputs identical (or per spec); run outcomes/logs recorded; all external resources cleaned up.
- Failure path: at least one deterministic failure-case run (missing input / invalid header / permission denied).

## Evidence plan
- Deterministic timing capture (same inputs, same environment): what is measured and where recorded.
- FP-03 controllable-decision and applicable acknowledgment/status latency witnesses; uninstrumented model/platform timings explicitly unverified.
- Workload/resource bounds: rows/items/files/bytes, memory/concurrency limits, queue/chunk/batch sizes.
- Cache/batch witness: cache scope/key/invalidation and batch/chunk strategy used.
- Complexity reasoning (big-O + dominant constants) when benchmarks aren’t feasible.
- Correctness witness: output equivalence/regression check on frozen representative fixtures.
- Disconfirming check: one edge/adversarial case that could invalidate the optimization hypothesis.
- Guard check: run full test suite (or smoke suite) after optimization to confirm no regressions outside the hotspot (verify metric improved + guard nothing else broke).
