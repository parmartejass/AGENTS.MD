---
doc_type: playbook
ssot_owner: AGENTS.md
update_trigger: performance/speed guidance changes OR new recurring hotspot patterns emerge
---

# Playbook — Performance Hotspots (Safe Optimizations)

Use when:
- Task matches profile `perf_hotspots` in `agents-manifest.yaml` (e.g., `iterrows`, per-cell Excel loops).

## Change classification (required)
- task type (feature|bugfix|refactor):
- blast radius (modules/workflows/users):
- if bugfix/regression: fill `docs/agents/playbooks/bugfix-template/bugfix-template.md`.
- if feature/behavior change: satisfy `AGENTS.md` "Verification Floors (Hard Gate)" behavior-change/new-feature minimums (including shift-left baseline).
- if refactor/behavior-neutral: satisfy `AGENTS.md` "Verification Floors (Hard Gate)" behavior-neutral minimums.
- if new logic is introduced: apply `docs/agents/35-coding-principles/coding-principles.md` under the `AGENTS.md` coding hard gate.

## Goal
- Improve speed/throughput with the fastest safe correct method within validated workload, domain, resource, and workflow boundaries.
- Do not trade away data integrity, deterministic behavior, user-facing feedback, cleanup, or logging for speed.

## Hotspot identification (verify first)
- What is slow (CPU vs I/O vs COM/network round-trips):
- Where is the loop/scan (symbol + file path + call sites):
- Size model (rows/items/files; worst-case bounds):

## Safe optimization levers (pick the minimal set)
- No safety/correctness trade-offs.
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
- Workload/resource bounds: rows/items/files/bytes, memory/concurrency limits, queue/chunk/batch sizes.
- Cache/batch witness: cache scope/key/invalidation and batch/chunk strategy used.
- Complexity reasoning (big-O + dominant constants) when benchmarks aren’t feasible.
- Correctness witness: output equivalence/regression check on frozen representative fixtures.
- Disconfirming check: one edge/adversarial case that could invalidate the optimization hypothesis.
- Guard check: run full test suite (or smoke suite) after optimization to confirm no regressions outside the hotspot (verify metric improved + guard nothing else broke).
