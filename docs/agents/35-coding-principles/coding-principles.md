---
doc_type: policy
ssot_owner: AGENTS.md
update_trigger: coding design authority, module boundary, structural minimality, or coding-principles council review rules change
---

# 35 - Coding Principles and Authority Design

This delegated policy supports the hard-gated coding architecture, Authority Graph, SSOT, no-duplicate, and no-fallback requirements in `AGENTS.md`.
It explains how to apply those gates to implementation code so coding design remains authority-correct, auditable, and minimal.
If any wording conflicts with `AGENTS.md`, `AGENTS.md` wins.

## Authority Role
- `AGENTS.md` owns the always-on coding hard-gate trigger, conflict precedence, and Subagent Council requirement.
- This doc owns delegated coding-principles mechanics for implementation code: authority owner selection, SSOT jurisdiction, module/folder contracts, dependency direction, structural minimality, post-diff purification, and coding-design witnesses.
- `scripts/entrypoint_contracts.json` owns public contract filename pattern facts.
- `scripts/check_folder_architecture/scope.json` owns the current checker-readable enforcement scope.
- This doc must be applied whenever implementation code is planned, added, reviewed, refactored, decomposed, purified, or wired across authority boundaries.

## Owner Routing
- Concept-to-owner routing: `docs/agents/20-sources-of-truth-map/sources-of-truth-map.md`.
- Docs placement, routers, and public leaves: `docs/agents/25-docs-ssot-policy/docs-ssot-policy.md`.
- Logging, explicit failures, event names, and reason-code ownership: `docs/agents/30-logging-errors/logging-errors.md`.
- Config keys, defaults, constants, enum-like values, and config repair: `docs/agents/40-config-constants/config-constants.md`.
- Runtime-path, backend-selection, fallback, legacy, substitute, and cleanup rules: `AGENTS.md` and the runtime-path section in `docs/agents/20-sources-of-truth-map/sources-of-truth-map.md`.

## Scope
Apply this doc to implementation code that owns runtime behavior, workflow logic, reusable runtime contracts, authority folders, public entrypoints, orchestration boundaries, or dependency direction.

Launch-only PowerShell/shell wrappers and Python runtime shims such as `__main__.py` may exist as zero-logic delegates into the canonical folder contract. A script with owner-declared runtime-selection or validation responsibility must expose that responsibility through its declared owner/contract instead of being treated as a launcher shim.

Config payloads, fixtures, schemas, and generated artifacts do not become feature folders unless they start owning runtime behavior.

## SSOT Jurisdiction Mechanics
This section is the implementation-code mechanism for the `AGENTS.md` SSOT jurisdiction and duplication pruning rule. SSOT jurisdiction is an always-on design rule for implementation work. Implementation-code capability, workflow, checker, generator, UI, adapter, config, schema, validation, and test changes must preserve one owning jurisdiction for each decision-critical fact, rule, state, side effect, lifecycle, public contract, output, witness, and verification obligation. Docs routers, docs placement, and documentation-only changes route to `docs/agents/25-docs-ssot-policy/docs-ssot-policy.md` unless they also change implementation-code behavior.

Before non-trivial implementation, review, remediation, refactor, or post-diff cleanup, build or derive:
- `jurisdiction_map`: decision-critical fact/state/effect/lifecycle/output/witness -> owner -> public contract.
- `drift_ledger`: duplicate, stale, shadow, patch, compatibility, fallback, test-only, checker-specific, or wrong-owner surfaces.
- `source_level_fix_point`: owner contract, schema, config, validator, workflow, module, registry, scope file, or public entrypoint to strengthen.
- `deletion_reroute_plan`: non-owner code/docs/tests/scripts/prompts/reports/checker logic to delete, move, or reroute.
- `witness_plan`: tests, checks, deterministic manual checks, or review evidence proving owner semantics, no stale references, and no duplicate jurisdiction.

Do not preserve drift with wrappers, compatibility branches, local predicates, test-only allowances, checker-specific patches, duplicated constants, fallback paths, private config interpretations, or caller-owned copies of owner rules.
If code exists only to compensate for a missing, weak, stale, ambiguous, or bypassed owner contract, delete or replace it through the owner.

Capability modules must be designed around the owning contract, not the current patch example. They accept validated intent or plain-data instructions from the authority owner, apply behavior generically within that declared contract, and report the full work universe: planned, eligible, applied, skipped, failed, and reasons. Unsupported, missing, ambiguous, or invalid inputs must produce explicit outcomes, not silent no-ops.

Adding, removing, or wiring behavior must update the owner-owned contract, registry, schema, config, scope file, validator, or public entrypoint first. Callers, wrappers, sibling modules, tests, docs, and checkers must consume that owner; they must not privately infer membership, routing, accepted alternatives, ordering, validation predicates, allowed paths, forbidden paths, or lifecycle semantics.

Feature requests must be decomposed into the feature authority and the reusable mechanics authority when boundary signals show that mechanics, external resources, lifecycle handling, validation, operation evidence, or transformation behavior can be reused, tested, or changed independently of one caller. Feature owners keep feature policy, settings intent, required/optional semantics, future extension shape, instruction building, and feature-level success/failure meaning. Mechanics owners expose generic operations through mechanics-shaped plain-data instructions and return operation evidence without knowing caller-feature policy.

Wrong-owner feature absorption through mechanics centralization is a jurisdiction defect. A mechanics owner must not accept caller-feature policy terms, config keys/defaults, required/optional semantics, domain-specific alternatives, future feature settings, or feature-shaped success/failure meanings. If a mechanics owner must change whenever one caller feature's settings or policy change, the caller feature has been absorbed by the wrong owner; if a feature duplicates the reusable mechanics, the mechanics boundary has been bypassed.

When lifecycle, finalization, promotion, cleanup, and operation evidence are one runtime invariant, keep them inside one stateful mechanics/workflow authority; caller features may request that capability, but must not recreate or reinterpret that lifecycle.

## Pre-Change Coding Design Review
Before implementation code changes, identify:
- intended behavior to preserve or strengthen;
- authority owner for each decision-critical responsibility;
- public entrypoint or contract for each touched authority;
- config, constants, schema, data, logging, and runtime-path owners consumed by the code;
- affected invariants and deterministic witnesses;
- duplicate, substitute, fallback, compatibility, or temporary logic that must be removed or routed to the owner.

If the owner is missing or conflicting, stop at the authority gap. Do not patch around the gap with a wrapper, local conditional, compatibility branch, or helper that becomes a second owner.

## Authority-Correct Design Standard
- One authority owns each decision-critical responsibility.
- Select the real SSOT jurisdiction and owner first; then move or keep behavior there.
- Preserve intended behavior while deleting duplicate, substitute, fallback, temporary, or non-authoritative logic.
- Valid boundary adapters are allowed when they adapt external I/O or platform APIs for the owning authority; they must not own business rules, config defaults, lifecycle policy, or runtime-path selection unless that is their declared authority.
- Orchestration code coordinates already-authoritative steps. It must call rule/config/lifecycle/runtime-path owners instead of implementing their decisions locally.
- UI, CLI, prompts, and checkboxes provide intent inputs; they do not own business rules, constants, config meaning, or workflow eligibility.

## Module and Folder Contracts
- Every distinct runtime capability is represented by an authority folder with exactly one registry-resolved public entrypoint file.
- Runtime public contract filenames are resolved by `scripts/entrypoint_contracts.json`.
- When another language or artifact kind needs a public contract, add the contract family to `scripts/entrypoint_contracts.json` and record the adopted authority boundary in `docs/project/architecture/architecture.md`.
- Internal files and child folders are private implementation details unless they become separately declared authorities.
- Consumers use the folder entrypoint only; no deep imports, sibling imports, or child-to-parent imports.
- Public contracts accept and return plain data. Live handles and external resources stay behind the owning boundary.
- Parent entrypoints are the only connectors across child authorities.
- Folder entrypoints stay thin, import-safe, and orchestration-only; private files hold detailed logic.
- Apply the same authority-folder rules recursively when a child folder gains independently owned behavior.

## Orchestration Boundaries
- Orchestration code may order already-authoritative steps, pass plain data between authority entrypoints, enforce the workflow state machine, record phase transitions/outcomes, and invoke bounded cleanup.
- Orchestration code consumes business rules, validation predicates, constants/defaults, backend-selection rules, lifecycle policies, retry policy, GUI-thread safety, COM safety, subprocess safety, and UI/checkbox semantics from their owners.
- Any decision-critical branch in orchestration calls a named authority-owned rule/config/lifecycle contract and records the selected authority path before execution.
- After validation, execution, commit, or cleanup failure, orchestration emits the terminal outcome and stops that branch.

## Dependency Direction
- Config, constants, schema, and data-shape owners are leaf dependencies.
- Workflows compose authorities; UI calls workflows.
- Composing an authority does not transfer ownership. A parent may decide whether to call a child from a validated runtime plan, but must not inspect, duplicate, or reimplement the child's private logic.
- Dependency graphs across authority boundaries must remain acyclic.
- `shared/` may contain only owner-neutral, pure/stateless shapes, protocols, or utilities whose semantics route to another declared owner. It must not own feature policy, workflow mechanics, config/default interpretation, validation predicates, branching, lifecycle/resource handling, outcome meanings, mechanics orchestration, or caller-specific instruction builders. If shared code must change for one feature's settings or policy, it belongs in that feature owner or the real mechanics/config/schema owner.
- Use explicit parameter/constructor injection. Service locators, runtime discovery, dynamic import, and eval-based wiring are outside the current coding contract unless a future owner explicitly adopts them with deterministic witnesses.

## Structural Minimality
- The default implementation path is the smallest authority-correct design that preserves or strengthens behavior.
- Existing owner-owned contracts, registries, schemas, config, validators, and entrypoints must be used when they cover the responsibility; repeated local conditionals and checker-specific patch logic are prohibited.
- Split inside the same folder first; promote to a child folder only when the behavior becomes independently owned.
- Before adding logic to an entrypoint, check boundary signals: distinct invariants/rules, distinct lifecycle/state handling, distinct I/O boundary or side effects, independent testability, and separate owner update triggers or independent change cadence.
- If any boundary signal is present, create or extend private files or child folders under the same authority parent before adding entrypoint logic; if no signal is present, keep the logic in the entrypoint with a rationale.
- Reusable mechanics must be promoted or extended only when boundary signals show the capability can be reused, tested, or changed independently while caller-feature policy remains in the feature owner; request-specific logic must stay in its current authority with a rationale.
- Before adding logic to folder entrypoints, record the decomposition decision and witness against this doc's owner sections in the task plan, council summary, or review output.
- A file that exceeds 400 LOC, or that the current change would make exceed 400 LOC, is a coding-principles trigger for the affected responsibility; before closure, apply this whole doc as with any patch, bugfix, feature change, addition, removal, refactor, or wiring change.
- The decision scope is the affected responsibility across all applicable owners, contracts, entrypoints, and call sites.
- The recorded decomposition decision and witness must apply the SSOT Jurisdiction Mechanics, Pre-Change Coding Design Review, Authority-Correct Design Standard, Module and Folder Contracts, Orchestration Boundaries, Dependency Direction, and Structural Minimality sections to choose the correct owner and change shape before code is moved.
- The decision must account for applicable current-module, parent/higher workflow, feature-folder, reusable-mechanics, `shared/`, script/checker, config/schema/data-owner, adapter, public-entrypoint, external-adapter, duplicate-pruning, deletion, and reroute boundaries.
- Apply SOLID/DI, DRY, KISS, YAGNI, Separation of Concerns, and Law of Demeter inside the authority-folder model.
- LOC reduction is valid closure evidence only when correctness, validation, explicit outcomes, observability, witnesses, SSOT jurisdiction/routing, and public-contract clarity remain intact. Numeric LOC targets are evidence pressure for authority-preserving decomposition.
- Any remaining LOC increase must be justified by required behavior, stronger validation, stronger observability, or clearer authority boundaries.

## Contract Change Gate
- Public entrypoint contract changes require explicit current contract, proposed contract, caller impact, and approval before editing.
- Private internals may change when the public contract stays stable and witnesses prove behavior preservation or intentional strengthening.

## Valid and Invalid Adapters
Valid adapters:
- isolate external I/O, subprocess, GUI, COM, network, file, or platform APIs at the owning boundary;
- translate between external formats and plain-data contracts;
- report failures through the logging/outcome owner without choosing substitute behavior;
- stay private unless they are the authority's declared public entrypoint.

Invalid adapters:
- choose fallback, legacy, compatibility, or substitute runtime paths after failure;
- duplicate config defaults, constants, validation predicates, or business rules;
- hide missing owners behind permissive wrappers;
- expose a second public entrypoint for the same authority;
- make cleanup run alternate business logic or convert failure into success.

## Post-Diff Jurisdictional Purification
After implementation and before closure, review the diff for:
- duplicated literals, predicates, config lists, runtime-path selectors, or outcome meanings;
- wrappers/adapters that bypass the real owner;
- fallback, legacy, compatibility, shadow, or substitute paths in runtime code;
- checker-specific patch logic that defines validation semantics belonging to the owner;
- public contract drift without explicit caller-impact approval;
- orphan code, orphan docs, or new files outside the authority parent;
- stale references to retired authority paths.

Post-diff purification is the owner-alignment pass that proves the diff expresses one jurisdiction per behavior.

## Witnesses and Final Report Fields
Record or be able to report:
- coding authority owner touched;
- public contract path and whether the public contract changed;
- preconditions, postconditions, and failure modes covered;
- invariants affected, with witness commands or deterministic manual checks;
- feature/mechanics composition witness when reusable capability boundaries are in scope: feature owner, mechanics owner, mechanics-shaped instruction contract, operation evidence contract, forbidden caller-policy terms ruled out, and independent-update proof that feature settings can change without mechanics-owner edits while mechanics remain reusable by another caller;
- duplicate/substitute/fallback logic removed or ruled out;
- valid adapters kept, with their boundary role;
- deletion-test result showing that deleting one feature folder breaks only its parent entrypoint, or scoped rationale when the deletion test is not applicable;
- README-listed checks run and outcomes.

## Reject Patterns
- Deep imports that bypass the public contract.
- Sibling-to-sibling imports or child-to-parent imports.
- The same rule, constant, config list, or runtime-path selector defined in multiple modules.
- Repeated local enforcement branches when a contract, registry, schema, config owner, or authority-owned validator can represent the rule once.
- Checker-specific policy copies instead of owner-owned contract data or validation.
- Hardcoded data-facing or business facts outside the owning input/config/data authority.
- Mechanics contracts or APIs shaped around one caller feature's policy terms, defaults, required/optional semantics, alternatives, future settings, or success/failure meanings.
- `shared/` helpers that own feature policy, config interpretation, validation predicates, lifecycle, workflow branching, mechanics orchestration, outcome meanings, or caller-specific instruction building.
- UI logic deciding business rules or workflow branching.
- Orchestration branches that implement business rules directly instead of calling the owner.
- Failure handlers that continue through alternate backends, legacy paths, substitute subprocesses, or compatibility workflow steps.
- Helper modules that become a second authority for the same responsibility.

## Where to Record Boundaries
- Record authority graph and module boundaries in `docs/project/architecture/architecture.md` or the workflow registry when that is the repo's SSOT for entrypoints.
- When a project adopts a cross-project governance authority decision, reference the governing decision ID from `docs/agents/22-ssot-authority-decisions/ssot-authority-decisions.md`.
- If `docs/project/architecture/architecture.md` is missing, create it before other changes.

## References
- `AGENTS.md`
- `docs/agents/20-sources-of-truth-map/sources-of-truth-map.md`
- `docs/agents/10-repo-discovery/repo-discovery.md`
