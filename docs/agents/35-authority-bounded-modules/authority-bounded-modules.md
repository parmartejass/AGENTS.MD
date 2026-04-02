---
doc_type: policy
ssot_owner: AGENTS.md
update_trigger: authority graph rules change OR module boundary/contract guidance changes
---

# 35 - Folder-Centered Authority Modules with Explicit Contracts

This policy supports the hard-gated "Authority Graph" requirement.
It explains how to structure code so authority boundaries are explicit and auditable.
If any wording conflicts with `AGENTS.md`, `AGENTS.md` wins.

## Core rules (authority alignment)
- One authority per decision-critical responsibility.
- The authority boundary is represented by a feature folder with exactly one public entrypoint file.
- Python authorities expose `main.py`; TypeScript authorities expose `index.ts`.
- If another language is used, the equivalent public contract file must be recorded in `docs/project/architecture/architecture.md`.
- Internal files or child folders are allowed inside the feature folder, but they must not expose public contracts directly.
- Each authority exposes a single explicit public contract; consumers use the folder contract only.
- UI/presentation layers are consumers; they do not own business rules, constants, or config.
- Core principle: high cohesion + low coupling.

## Contract expectations (what "explicit" means)
- Declare inputs, outputs, and side effects (I/O boundaries must be visible).
- State preconditions, postconditions, and failure modes.
- The contract is defined in the folder entrypoint (code); docs reference the symbol/path, not restate it.
- Public contracts take plain data in and return plain data out.
- Avoid hidden writes, global state changes, or live resource handles outside the contract.

## Dependency direction (keep boundaries clean)
- Config/constants/schema types are leaf dependencies (authorities may depend on them; they do not depend on authorities).
- Workflows compose authorities; UI calls workflows.
- The parent entrypoint is the only connector across child folders.
- Children must not import siblings or parents.
- Avoid cycles across authority boundaries.

## Decomposition trigger + guardrail
- Use the decomposition decision flow in `docs/agents/playbooks/design-principles-checklist/design-principles-checklist.md` before adding logic to folder entrypoints.
- Distinct invariants, lifecycle, I/O boundaries, testability, or change-cadence signals require extracting private files or child folders.
- Split inside the same folder first; promote to a child folder when the behavior becomes independently owned.
- Follow the `400 LOC` hard gate in `AGENTS.md`; LOC alone is not a reason for unrelated refactors.

## Boundary discipline
- I/O stays at the boundary: folder entrypoints or boundary helpers may perform I/O, but pure logic functions must not.
- `shared/` is optional and may contain only data shapes and pure/stateless utilities.
- `shared/` must not become a second authority for workflow decisions or business rules.
- Do not extract to `shared/` until the exact same pure shape/utility is duplicated across 3+ folders.

## Witnesses
- Tests or runtime validation prove preconditions/postconditions.
- Logs or reports name the contract and outcome.
- Map each pre/postcondition to at least one witness signal (test or runtime log).
- Schema/type checks prove data shape (rules/validation remain in their SSOT owner).
- The deletion test is a required architecture witness: deleting one feature folder should break only its parent entrypoint.

## Reject patterns
- Deep imports that bypass the public contract.
- Sibling-to-sibling imports or child-to-parent imports.
- The same rule or constant defined in multiple modules.
- UI logic deciding business rules or workflow branching.
- "Helper" modules that become a second authority for the same responsibility.

## Where to record boundaries
- Record the authority graph and module boundaries in `docs/project/architecture/architecture.md` (project root),
  or in the workflow registry when that is the repo's SSOT for entrypoints.
- When a project adopts a cross-project governance authority decision, reference the governing decision ID from `docs/agents/22-ssot-authority-decisions/ssot-authority-decisions.md`.
- If `docs/project/architecture/architecture.md` is missing, create it before other changes.

## References (SSOT)
- `docs/agents/20-sources-of-truth-map/sources-of-truth-map.md`
- `docs/agents/10-repo-discovery/repo-discovery.md`
