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

## Core checks (required)
- DRY: no duplicated constants/rules/conditionals across modules.
- KISS: design is the simplest one that satisfies acceptance criteria.
- YAGNI: no speculative extensibility or unused abstractions.
- Separation of Concerns: boundaries align with authority owners.
- Law of Demeter: no deep cross-module traversal of internals.

## SOLID + DI checks (required)
- SRP: each module has one reason to change.
- OCP: extension points added only when a second variant exists.
- LSP: substitutions preserve pre/postconditions.
- ISP: contracts are minimal and consumer-driven.
- DIP/DI: dependencies injected via explicit constructors/parameters.

## Module-linking checks (required)
- Dependency graph is acyclic.
- No runtime discovery/eval-based wiring.
- No service locator pattern in domain logic.
- Shared utilities are leaf modules (pure/stateless, no authority logic).

## Reusability checks (required for shared modules)
- Public contract documented at authority entrypoint.
- Module is testable in isolation.
- No unnecessary transitive dependencies.
- Version/change policy declared when shared across repos/teams.

## Evidence to record
- authority owner touched:
- contract pre/postconditions:
- failure modes covered:
- tests proving invariants:
- performance/resource notes (if relevant):
