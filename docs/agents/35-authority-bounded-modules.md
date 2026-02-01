---
doc_type: policy
ssot_owner: AGENTS.md
update_trigger: authority graph rules change OR module boundary/contract guidance changes
---

# 35 - Authority-Bounded Modules with Explicit Contracts

This policy supports the hard-gated "Authority Graph" requirement in `AGENTS.md`.
It explains how to structure code so authority boundaries are explicit and auditable.

## Core rules (authority alignment)
- One authority per decision-critical responsibility.
- The authority boundary is represented by a single module or package entrypoint; internal submodules are allowed but must not expose public contracts.
- Each authority exposes a single explicit public contract; consumers use the contract only.
- UI/presentation layers are consumers; they do not own business rules, constants, or config.

## Contract expectations (what "explicit" means)
- Declare inputs, outputs, and side effects (I/O boundaries must be visible).
- State preconditions, postconditions, and failure modes (see `AGENTS.md` "First-Principles Protocol").
- The contract is defined in the authority module entrypoint (code); docs reference the symbol, not restate it.
- Avoid hidden writes or global state changes outside the contract.

## Dependency direction (keep boundaries clean)
- Config/constants/schema types are leaf dependencies (authorities may depend on them; they do not depend on authorities).
- Workflows compose authorities; UI calls workflows.
- Avoid cycles across authority boundaries.

## Witnesses (required by `AGENTS.md`)
Use the existing "Invariants + Witnesses" rule in `AGENTS.md`:
- Tests or runtime validation prove preconditions/postconditions.
- Logs or reports name the contract and outcome.
- Map each pre/postcondition to at least one witness signal (test or runtime log).
- Schema/type checks prove data shape (rules/validation remain in their SSOT owner).

## Reject patterns
- Deep imports that bypass the public contract.
- The same rule or constant defined in multiple modules.
- UI logic deciding business rules or workflow branching.
- "Helper" modules that become a second authority for the same responsibility.

## Where to record boundaries
- Record the authority graph and module boundaries in `docs/project/architecture.md` (project root),
  or in the workflow registry when that is the repo's SSOT for entrypoints.
- If `docs/project/architecture.md` is missing, create it per the `AGENTS.md` Documentation SSOT Policy before other changes.

## References (SSOT)
- `AGENTS.md` (Authority Graph, Non-Negotiables, Invariants + Witnesses)
- `docs/agents/20-sources-of-truth-map.md`
- `docs/agents/10-repo-discovery.md`
