---
doc_type: policy
ssot_owner: AGENTS.md
update_trigger: AGENTS.md objective/invariants change
---

# 00 — Principles (First Principles)

## Invariants
1) Correct: verified against the repo and tools; no guessed APIs/paths.
2) Deterministic: same inputs → same outputs (no hidden side effects; isolate I/O and side effects).
3) Maintainable: each concept defined exactly once (SSOT / no duplicates).
4) Auditable (Traceability): logs + clear run outcomes; failures are explicit (safe failure).
5) Safe: no resource leaks; Excel COM + GUI threading rules are enforced.
6) Searchable: critical concepts are discoverable via grep + semantic search.

## Preferred patterns
- “Verify, then trust”: confirm paths/symbols/dependencies with repo + tools.
- Named rules for conditions (`is_*`, `require_*`, `validate_*`) to avoid duplicated `if` logic.
- Workflows orchestrate; UI and scripts call workflows.
- Resource safety via context managers and `finally`.

## Reject patterns
- Copy/paste helpers.
- Duplicate constants/config defaults in multiple files/docs.
- Multiple lifecycle implementations for the same external system (Excel, GUI queue/drain, etc.).
