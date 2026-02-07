---
doc_type: playbook
ssot_owner: AGENTS.md
update_trigger: modularity/authority-boundary policy or design-principle guidance changes
---

# Playbook - Design Principles Checklist

Use when:
- Creating or modifying modules and their integration links.
- Reviewing reusability, coupling, and change safety.

Reference authority:
- `AGENTS.md` "Mandatory Modularity + SOLID/DI (Authority Bloat Prevention)"
- `AGENTS.md` "First-Principles Protocol (Hard Gate)"
- `docs/agents/35-authority-bounded-modules.md`

This checklist is derived from `AGENTS.md`. If any wording conflicts, `AGENTS.md` wins.

## Core checks
- DRY: no duplicated constants/rules/conditionals across modules.
- KISS: design is the simplest one that satisfies acceptance criteria.
- YAGNI: no speculative extensibility or unused abstractions.
- Separation of Concerns: boundaries align with authority owners.
- Law of Demeter: no deep cross-module traversal of internals.

## SOLID + DI checks
- SRP: each module has one reason to change.
- OCP: extension points added only when a second variant exists.
- LSP: substitutions preserve pre/postconditions.
- ISP: contracts are minimal and consumer-driven.
- DIP/DI: dependencies injected via explicit constructors/parameters.

## Module-linking checks
- Dependency graph is acyclic.
- No runtime discovery/eval-based wiring.
- No service locator pattern in domain logic.
- Shared utilities are leaf modules (pure/stateless, no authority logic).

## Reusability checks (shared modules)
- Public contract documented at authority entrypoint.
- Module is testable in isolation.
- No unnecessary transitive dependencies.
- Version/change policy declared when shared across repos/teams.

## Module Decomposition Record (fill before adding logic)
- authority module/entrypoint:
- change summary:
- current module file LOC:

### Boundary signal check
- distinct invariants/rules introduced? (Y/N):
- distinct lifecycle/state handling introduced? (Y/N):
- distinct I/O boundary or side effects introduced? (Y/N):
- independently testable component introduced? (Y/N):
- likely independent change cadence from entrypoint? (Y/N):

### Decomposition decision
- any signal above is Y? (Y/N):
- if Y: create/extend child module now (required):
- if N: keep in entrypoint with rationale:
- LOC > 300 soft guardrail reached? (Y/N):
- if LOC guardrail reached: extract now or defer with rationale:

### Wiring rules
- entrypoint stays orchestration + public contract only:
- child modules hold distinct logic/rules/strategies:
- shared leaf modules stay pure/stateless and authority-neutral:
- no cycles or deep-import bypasses of public contracts:

### Example pattern (feature-centered)
- `speed_mode/entrypoint.py` (authority/public contract)
- `speed_mode/criteria_fast.py` (criterion module)
- `speed_mode/criteria_balanced.py` (criterion module)
- `speed_mode/criteria_safe.py` (criterion module)
- `shared/speed_math.py` (pure reusable leaf utility)

## Evidence to record
- authority owner touched:
- contract pre/postconditions:
- failure modes covered:
- tests proving invariants:
- performance/resource notes (if relevant):
