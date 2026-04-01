---
doc_type: playbook
ssot_owner: AGENTS.md
update_trigger: modularity/authority-boundary policy or design-principle guidance changes
---

# Playbook - Module Architecture Checklist

Use when:
- Creating or modifying feature folders and their integration links.
- Reviewing reusability, coupling, and change safety.

Reference: `docs/agents/35-authority-bounded-modules/authority-bounded-modules.md`

This checklist is a prompting scaffold.

## Core checks
- DRY: no duplicated constants/rules/conditionals across modules.
- KISS: design is the simplest one that satisfies acceptance criteria.
- YAGNI: no speculative extensibility or unused abstractions.
- Separation of Concerns: boundaries align with authority owners.
- Law of Demeter: no deep cross-module traversal of internals.

## Folder contract checks
- One feature, one folder.
- Exactly one public folder entrypoint (`main.py` or `index.ts`, or one documented equivalent for another language).
- Parent entrypoint is the only connector between children.
- Public entrypoints take plain data in and return plain data out.
- Pure logic stays free of I/O; entrypoints wire I/O to logic.

## Dependency checks
- Dependency graph is acyclic.
- No sibling imports.
- No child-to-parent imports.
- No runtime discovery/eval-based wiring.
- No service locator pattern in domain logic.
- Shared utilities are leaf modules (pure/stateless, no authority logic).

## Reusability checks (shared modules)
- Public contract documented at authority entrypoint.
- Module is testable in isolation.
- No unnecessary transitive dependencies.
- Version/change policy declared when shared across repos/teams.
- `shared/` is introduced only after the same pure shape/utility is duplicated across 3+ folders.

## Folder Architecture Record (fill before adding logic)
- parent entrypoint:
- feature folder:
- public contract file:
- change summary:
- current entrypoint LOC:

### Boundary signal check
- distinct invariants/rules introduced? (Y/N):
- distinct lifecycle/state handling introduced? (Y/N):
- distinct I/O boundary or side effects introduced? (Y/N):
- independently testable component introduced? (Y/N):
- likely independent change cadence from entrypoint? (Y/N):

### Decomposition decision
- any signal above is Y? (Y/N):
- if Y: create/extend private files or child folders now (required):
- if N: keep in entrypoint with rationale:
- LOC > 300 soft guardrail reached? (Y/N):
- if LOC guardrail reached: extract now or defer with rationale:

### Wiring rules
- entrypoint stays orchestration + public contract only:
- private files hold distinct logic/rules/strategies:
- child folders are connected only by the parent entrypoint:
- shared leaf modules stay pure/stateless and authority-neutral:
- no cycles or deep-import bypasses of public contracts:
- deletion test witness recorded:

### Contract change gate
- entrypoint signature changed? (Y/N):
- if Y: current contract:
- if Y: proposed contract:
- if Y: parent callers identified:
- if Y: user approval recorded before edit:

### Example pattern (feature-centered)
- `speed-mode/main.py` (authority/public contract)
- `speed-mode/criteria_fast.py` (private logic)
- `speed-mode/criteria_balanced.py` (private logic)
- `speed-mode/criteria_safe.py` (private logic)
- `shared/speed_math.py` (pure reusable leaf utility)

## Evidence to record
- authority owner touched:
- contract pre/postconditions:
- failure modes covered:
- tests proving invariants:
- deletion test result:
- performance/resource notes (if relevant):
