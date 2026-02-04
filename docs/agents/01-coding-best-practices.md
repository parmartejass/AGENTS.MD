---
doc_type: policy
ssot_owner: AGENTS.md
update_trigger: AGENTS.md core principles or hard gates change
---

# 01 — Coding Best Practices (First Principles Distilled)

These are distilled, non-negotiable rules. Adhering to them eliminates most bugs at the source; violating any one opens a class of defects.

---

## The 7 Invariants

### 1. Verify Before You Act
Never guess paths, imports, APIs, or config keys. Use tools to confirm facts exist before using them. If unverifiable, treat as **Unknown** and ask.

### 2. Single Source of Truth (SSOT)
Every fact has exactly one owner. Find it, extend it. Never duplicate constants, rules, config, or logic across files.

### 3. Fail Explicitly
No silent skips. Every branch must either succeed with evidence or fail with a logged reason code. Catch specific exceptions only; re-raise with context.

### 4. Resource Safety
Acquire late, release in `finally`. Use context managers. Bound all waits with timeouts. No infinite loops.

### 5. Minimal Diff
Change only what acceptance criteria require. No bundled refactors, no speculative features, no extra "cleanup."

### 6. Fix at the Authority
When debugging, trace upstream to the contract/boundary that should prevent the error class. One authority fix prevents N symptoms.

### 7. Prove Correctness
State preconditions, postconditions, and failure modes. Define invariants with measurable witnesses. Run deterministic verification before claiming done.

---

## Quick Trace Protocol (When a Bug Occurs)

```
1. Reproduce (MRE) → capture exact inputs + observed output
2. Locate symptom   → file:line where failure manifests
3. Trace upstream   → which authority/contract should have prevented this?
4. Fix at authority → add/strengthen validation or invariant there
5. Add witness      → test that fails before fix, passes after
6. Verify           → run repo checks; confirm no regressions
```

---

## Anti-Patterns (Immediate Red Flags)

| Pattern | Why It Fails |
|---------|--------------|
| Hardcoded literal repeated in 2+ places | Drift; silent inconsistency |
| Empty `except:` or `except Exception: pass` | Silent failure; masked bugs |
| Infinite loop / unbounded wait | Hangs; resource exhaustion |
| File/resource opened without `with` or `finally` | Leak on exception path |
| Editing code you haven't read | Blind mutation; unintended side effects |
| Guessing API/path without verification | Hallucinated dependencies; runtime crash |
| Patching symptom without root-cause analysis | Whack-a-mole; bug reappears elsewhere |

---

## Minimum Verification (Before Merge)

1. All new code is reachable from an entrypoint (no orphans).
2. All invariants have witnesses (tests or deterministic checks).
3. No new duplicates introduced (grep for literals/logic).
4. Repo checks pass (lint, type, test as defined in README "Checks").

---

*Canonical policy: `AGENTS.md`. This doc is a distilled reference only.*
