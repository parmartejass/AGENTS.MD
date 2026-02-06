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
- if bugfix/regression: fill `docs/agents/playbooks/bugfix-template.md` and satisfy `AGENTS.md` "Bias-Resistant Debugging (Hard Gate)".
- if behavior change/new feature: satisfy `AGENTS.md` "Verification Floors (Hard Gate)" shift-left baseline.
- if refactor/behavior-neutral change: satisfy `AGENTS.md` "Verification Floors (Hard Gate)" behavior-neutral minimums.
- if new logic is introduced: apply `AGENTS.md` Non-Negotiable 11 "Mandatory Modularity + SOLID/DI (Authority Bloat Prevention)".

## Goal
- Improve speed/throughput without data loss, determinism regressions, or weakened cleanup/logging.

## Hotspot identification (verify first)
- What is slow (CPU vs I/O vs COM/network round-trips):
- Where is the loop/scan (symbol + file path + call sites):
- Size model (rows/items/files; worst-case bounds):

## Safe optimization levers (pick the minimal set)
- Follow `AGENTS.md` "Performance & Speed (When Relevant)" (no safety/correctness trade-offs).
- Replace per-item round-trips with bulk operations (Excel: avoid per-cell COM calls; dataframes: avoid row-wise Python loops when a vectorized/groupby/join exists).
- Cache expensive lookups deterministically (precompute maps/indices); define invalidation when inputs change.
- Reduce repeated scans (compute bounds once; avoid repeated `rg`/directory walks/parse passes).
- Batch/chunk processing with explicit bounds (memory caps, timeouts, cancellation-aware cleanup).
- Keep concurrency bounded and output deterministic (stable ordering rules; avoid races on shared outputs).

## Proof obligations
- Preconditions: inputs validated; schemas/headers known; config/SSOT owners identified.
- Postconditions: outputs identical (or per spec); run outcomes/logs recorded; all external resources cleaned up.
- Failure path: at least one deterministic failure-case run (missing input / invalid header / permission denied).

## Evidence plan
- Deterministic timing capture (same inputs, same environment): what is measured and where recorded.
- Complexity reasoning (big-O + dominant constants) when benchmarks aren’t feasible.
- Correctness witness: output equivalence/regression check on frozen representative fixtures.
- Disconfirming check: one edge/adversarial case that could invalidate the optimization hypothesis.
