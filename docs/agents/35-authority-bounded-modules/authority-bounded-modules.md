---
doc_type: policy
ssot_owner: AGENTS.md
update_trigger: authority graph rules change OR module boundary/contract guidance changes
---

# 35 - Folder-Centered Authority Modules with Explicit Contracts

This delegated policy supports the hard-gated "Module Architecture" and "Authority Graph" requirements in `AGENTS.md`.
It explains how to apply those gates so runtime-code authority boundaries are explicit and auditable.
If any wording conflicts with `AGENTS.md`, `AGENTS.md` wins.

## Authority role
- `AGENTS.md` owns the always-on code-modularity hard gate and conflict precedence.
- This doc owns delegated runtime-code module-contract mechanics under that gate: boundary application, contract expectations, dependency direction, decomposition procedure, boundary witnesses, and reject-pattern guidance.
- `scripts/entrypoint_contracts.json` owns public contract filename pattern facts.
- `scripts/check_folder_architecture/scope.json` owns the current checker-readable enforcement scope.
- Use this doc whenever implementation code is added, reviewed, refactored, decomposed, or wired across feature-folder boundaries.

## Core rules (authority alignment)
- One authority per decision-critical responsibility.
- The authority boundary is represented by a feature folder with exactly one public entrypoint file.
- Runtime public contract filenames are resolved by `scripts/entrypoint_contracts.json`.
- Python executable authorities therefore expose `<authority>_main.py`; TypeScript executable authorities therefore expose `<authority>_index.ts`.
- If another language is used, add the family/artifact contract to `scripts/entrypoint_contracts.json` and record the adopted public contract file in `docs/project/architecture/architecture.md`.
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
- Workflow and parent entrypoints are runtime coordinators: they sequence authority calls, pass plain data, record outcomes, and invoke cleanup, but they do not own business-rule predicates, validation logic, constants/defaults, backend-selection rules, resource lifecycle policy, or UI/checkbox semantics.
- Checkbox state, CLI flags, and other user selections are intent inputs; workflow entrypoints may route from them only after validating them against the config/rule authority that owns their meaning.
- Composing an authority does not transfer ownership. A parent may decide whether to call a child from a validated runtime plan, but must not inspect, duplicate, or reimplement the child's private business logic.
- The parent entrypoint is the only connector across child folders.
- Children must not import siblings or parents.
- Avoid cycles across authority boundaries.

## Decomposition trigger + guardrail
- Use the decomposition decision flow in `docs/agents/playbooks/design-principles-checklist/design-principles-checklist.md` before adding logic to folder entrypoints.
- Distinct invariants, lifecycle, I/O boundaries, testability, or change-cadence signals require extracting private files or child folders.
- Split inside the same folder first; promote to a child folder when the behavior becomes independently owned.
- Follow the `400 LOC` hard gate in `AGENTS.md`; LOC alone is not a reason for unrelated refactors.

## Structural minimality
- The default implementation path is the smallest authority-correct design that preserves or strengthens behavior.
- Before adding code, identify the authority owner, public entrypoint or contract, config/data/schema source if any, affected invariants, and behavior-preservation witness.
- Prefer existing owner-owned contracts, registries, schemas, config, and entrypoints over repeated local conditionals or checker-specific patch logic.
- Continue consolidating while behavior remains equivalent or stronger. LOC reduction is valid evidence only when correctness, explicit failure, witnesses, and SSOT ownership remain intact.
- Numeric LOC-reduction targets are evidence pressure toward structural minimality, not quotas.
- Any remaining LOC increase must be justified by new required behavior, stronger validation, or stronger observability.

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
- Repeated local enforcement branches when a contract, registry, schema, config owner, or authority-owned validator can represent the rule once.
- Checker-specific patch logic that encodes policy outside the policy owner instead of reading contract data or calling the owner-owned validation path.
- Hardcoded data-facing or business facts outside the owning input/config/data authority.
- UI logic deciding business rules or workflow branching.
- Orchestration branches that implement business rules directly instead of calling the rule/config/lifecycle authority.
- Failure handlers that continue by choosing an alternate backend, legacy path, substitute subprocess, or compatibility workflow step.
- "Helper" modules that become a second authority for the same responsibility.

## Where to record boundaries
- Record the authority graph and module boundaries in `docs/project/architecture/architecture.md` (project root),
  or in the workflow registry when that is the repo's SSOT for entrypoints.
- When a project adopts a cross-project governance authority decision, reference the governing decision ID from `docs/agents/22-ssot-authority-decisions/ssot-authority-decisions.md`.
- If `docs/project/architecture/architecture.md` is missing, create it before other changes.

## References (SSOT)
- `docs/agents/20-sources-of-truth-map/sources-of-truth-map.md`
- `docs/agents/10-repo-discovery/repo-discovery.md`
