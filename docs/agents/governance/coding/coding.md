---
doc_type: policy
ssot_owner: docs/agents/governance/coding/coding.md
update_trigger: coding design authority, module boundary, structural minimality, or coding-principles review obligations change
---

# Coding

Jurisdiction: implementation-code authority owner selection, SSOT jurisdiction mechanics, module and folder contracts, orchestration boundaries, dependency direction, structural minimality, adapters, runtime-path rules, comments, post-diff purification, and coding-design witnesses.

## Scope

- MUST apply whenever implementation code is planned, added, reviewed, refactored, decomposed, purified, or wired across authority boundaries.
- Applies to code owning runtime behavior, workflow logic, reusable runtime contracts, authority folders, public entrypoints, orchestration boundaries, or dependency direction.
- Launch-only shell wrappers and Python shims such as `__main__.py` MAY exist as zero-logic delegates into the canonical folder contract.
- A script with owner-declared runtime-selection or validation responsibility MUST expose that responsibility through its declared owner contract, not as a launcher shim.
- Config payloads, fixtures, schemas, and generated artifacts MUST NOT become feature folders unless they start owning runtime behavior.

## SSOT jurisdiction mechanics

Before non-trivial implementation, review, remediation, refactor, or post-diff cleanup, MUST build or derive:

- `jurisdiction_map`: decision-critical fact/state/effect/lifecycle/output/witness -> owner -> public contract.
- `drift_ledger`: duplicate, stale, shadow, patch, compatibility, fallback, test-only, checker-specific, or wrong-owner surfaces.
- `source_level_fix_point`: owner contract, schema, config, validator, workflow, module, registry, scope file, or public entrypoint to strengthen.
- `deletion_reroute_plan`: non-owner code/docs/tests/scripts/prompts/reports/checker logic to delete, move, or reroute.
- `witness_plan`: tests, checks, deterministic manual checks, or review evidence proving owner semantics, no stale references, and no duplicate jurisdiction.

Rules:

- Prohibited: preserving drift with wrappers, compatibility branches, local predicates, test-only allowances, checker-specific patches, duplicated constants, fallback paths, private config interpretations, or caller-owned copies of owner rules.
- Code existing only to compensate for a missing, weak, stale, ambiguous, or bypassed owner contract MUST be deleted or replaced through the owner.
- Capability modules MUST be designed around the owning contract, not the current patch example; they accept validated intent or plain-data instructions and report the full work universe: planned, eligible, applied, skipped, failed, and reasons.
- Adding, removing, or wiring behavior MUST update the owner-owned contract, registry, schema, config, scope file, validator, or public entrypoint first.
- Callers, wrappers, sibling modules, tests, docs, and checkers MUST consume that owner and MUST NOT privately infer membership, routing, accepted alternatives, ordering, validation predicates, allowed or forbidden paths, or lifecycle semantics.
- Feature requests MUST be decomposed into the feature authority and the reusable mechanics authority when mechanics, external resources, lifecycle handling, validation, operation evidence, or transformation behavior can be reused, tested, or changed independently of one caller.
- Feature owners MUST keep feature policy, settings intent, required/optional semantics, future extension shape, instruction building, and feature-level success/failure meaning.
- Mechanics owners MUST expose generic operations through mechanics-shaped plain-data instructions and return operation evidence without knowing caller-feature policy.
- Prohibited: a mechanics owner accepting caller-feature policy terms, config keys or defaults, required/optional semantics, domain-specific alternatives, future feature settings, or feature-shaped success/failure meanings.
- A mechanics owner that must change whenever one caller feature's settings or policy change is a wrong-owner absorption defect; a feature duplicating the reusable mechanics has bypassed the mechanics boundary.
- Lifecycle, finalization, promotion, cleanup, and operation evidence forming one runtime invariant MUST stay inside one stateful mechanics or workflow authority; callers MAY request that capability but MUST NOT recreate or reinterpret the lifecycle.

## Pre-change coding design review

Before implementation code changes, MUST identify:

- intended behavior to preserve or strengthen;
- the authority owner for each decision-critical responsibility;
- the public entrypoint or contract for each touched authority;
- config, constants, schema, data, logging, and runtime-path owners consumed by the code;
- affected invariants and deterministic witnesses;
- duplicate, substitute, fallback, compatibility, or temporary logic to remove or route to the owner.

A missing or conflicting owner is an authority gap: work MUST stop there; Prohibited: patching around it with a wrapper, local conditional, compatibility branch, or helper that becomes a second owner.

## Module and folder contracts

- One public interface or API is the module owner's declared contract surface, including all documented public operations.
- Every distinct runtime capability MUST be an authority folder with exactly one owner-resolved public entrypoint file.
- Direct Python feature folders under `scripts/` MUST expose `scripts/<feature>/<feature>_main.py`; the governance-core public contract enforces this.
- Another language or artifact kind needing a public contract MUST record the adopted authority boundary in the architecture project doc and add a deterministic checker witness before consumers rely on it.
- Internal files and child folders MUST stay behind the folder entrypoint unless separately declared authorities; Prohibited: deep imports, sibling imports, child-to-parent imports.
- Public contracts MUST accept and return plain data; live handles and external resources stay behind the owning boundary.
- Parent entrypoints are the only connectors across child authorities.
- Folder entrypoints MUST stay thin, import-safe, and orchestration-only; private files hold detailed logic.
- These authority-folder rules MUST apply recursively when a child folder gains independently owned behavior.
- Documentation-only structure changes follow the documentation jurisdiction.

## Orchestration boundaries

- Orchestration code MAY order already-authoritative steps, pass plain data between authority entrypoints, enforce the workflow state machine, record phase transitions and outcomes, and invoke bounded cleanup.
- Orchestration code MUST consume business rules, validation predicates, constants and defaults, backend-selection rules, lifecycle policies, retry policy, GUI-thread safety, COM safety, subprocess safety, and UI/checkbox semantics from their owners.
- Any decision-critical branch in orchestration MUST call a named authority-owned rule, config, or lifecycle contract and record the selected authority path before execution.
- After validation, execution, commit, or cleanup failure, orchestration MUST emit the terminal outcome and stop that branch.

## Dependency direction

- Config, constants, schema, and data-shape owners are leaf dependencies; workflows compose authorities; UI calls workflows.
- UI, CLI, prompts, and checkboxes supply intent inputs only; they MUST NOT own business rules, workflow branching, constants, config meaning, or workflow eligibility.
- Composing an authority MUST NOT transfer ownership: a parent MAY decide whether to call a child from a validated runtime plan but MUST NOT inspect, duplicate, or reimplement the child's private logic.
- Dependency graphs across authority boundaries MUST remain acyclic.
- `shared/` MAY contain only owner-neutral, pure or stateless shapes, protocols, or utilities whose semantics route to another declared owner.
- `shared/` MUST NOT own feature policy, workflow mechanics, config or default interpretation, validation predicates, branching, lifecycle or resource handling, outcome meanings, mechanics orchestration, or caller-specific instruction builders; shared code that must change for one feature's settings or policy belongs in that feature, mechanics, config, or schema owner.
- Consumer boundaries MUST use explicit parameter or constructor injection.
- Extensible capabilities MUST expose bounded authoritative discovery or registered handlers on the owning composition contract, and MUST record discovery scope, ordering, validation, termination, cost, cache invalidation, and explicit unsupported outcomes.
- Consumers receive the resolved contract; Prohibited: consumer-implemented discovery, hardcoded open-world capability lists, unowned service location, unbounded dynamic wiring, eval-based wiring.

## Structural minimality

code_decomposition_review_lines: 400

- That operative declaration is the sole code-size review value: one column-zero key, a colon and single space, and a positive decimal integer without sign or leading zero.
- Fenced, indented-code, and quoted examples supply no value; missing, malformed, duplicate, nonpositive, or unsupported-sized integers fail explicitly without a default.
- Governance-core counts `str.splitlines()` records including comments and blanks for its Python structural subset and warns only above the declared value.
- The default implementation path MUST be the smallest authority-correct design that preserves or strengthens behavior.
- Existing owner-owned contracts, registries, schemas, config, validators, and entrypoints MUST be used when they cover the responsibility; Prohibited: repeated local conditionals, checker-specific patch logic.
- MUST split inside the same folder first; promote to a child folder only when the behavior becomes independently owned.
- Before adding logic to an entrypoint, MUST check boundary signals: distinct invariants or rules, distinct lifecycle or state handling, distinct I/O boundary or side effects, independent testability, separate owner update triggers or independent change cadence.
- If any boundary signal is present, MUST create or extend private files or child folders under the same authority parent before adding entrypoint logic; with no signal, keep the logic in the entrypoint and record the rationale.
- Reusable mechanics MUST be promoted or extended only when boundary signals show the capability can be reused, tested, or changed independently while caller-feature policy stays in the feature owner; request-specific logic stays in its current authority with a recorded rationale.
- Before adding logic to folder entrypoints, MUST record the decomposition decision and witness against this doc's sections in the confirmed plan or role-bounded agent report.
- A file exceeding `code_decomposition_review_lines`, or that the current change would make exceed it, is a coding-principles trigger for the affected responsibility; this whole doc MUST be applied before closure as with any patch, bugfix, feature change, addition, removal, refactor, or wiring change.
- The decision scope is the affected responsibility across all applicable owners, contracts, entrypoints, and call sites.
- The decision MUST account for applicable current-module, parent or higher workflow, feature-folder, reusable-mechanics, `shared/`, script/checker, config/schema/data-owner, adapter, public-entrypoint, external-adapter, duplicate-pruning, deletion, and reroute boundaries.
- LOC reduction is valid closure evidence only when correctness, validation, explicit outcomes, observability, witnesses, SSOT jurisdiction and routing, and public-contract clarity remain intact; numeric LOC targets are evidence pressure for authority-preserving decomposition.
- Any remaining LOC increase MUST be justified by required behavior, stronger validation, stronger observability, or clearer authority boundaries.

## Contract change gate

- Before changing a public entrypoint, MUST record current and proposed contracts, the contract fields (inputs, outputs, authorized actions, side effects, errors, compatibility, versioning, extension rules), identified active callers, migration and removal impact, and deterministic compatibility witnesses.
- The assigned execution agent MAY change private internals within its authorized assignment when the public contract remains stable and recorded witnesses prove behavior preservation or authorized strengthening.

## Valid and Invalid Adapters

Valid adapters MUST:

- record the adapter justification, owning boundary, authorized scope, and review witness;
- isolate external I/O, subprocess, GUI, COM, network, file, or platform APIs at the owning boundary;
- translate transport or representation only between external formats and owner-issued plain-data contracts, preserving owner-issued semantic values exactly; semantic resolution or correction stays with the declared owner under `AGENTS.md` Resolve once before fan-out;
- report failures through the logging and outcome owner without choosing substitute behavior;
- stay private unless they are the authority's declared public entrypoint.

Invalid adapters, all Prohibited:

- choosing fallback, legacy, compatibility, or substitute runtime paths after failure;
- duplicating config defaults, constants, validation predicates, or business rules;
- hiding missing owners behind permissive wrappers;
- exposing a second public entrypoint for the same authority;
- making cleanup run alternate business logic or convert failure into success.

## No Duplicates

Duplication, all Prohibited:

- repeating the same literal with the same meaning across files or docs;
- repeating the same conditional logic or rule across files;
- copy/paste helpers with minor variations.

## No Fallback or Legacy Runtime Paths

- MUST choose one explicit deterministic runtime path from the current SSOT contract.
- Runtime code MUST NOT implement or select fallback, legacy, compatibility, shadow, downgrade, or substitute execution branches for the same responsibility.
- Unsupported, unverified, unavailable, retired, or legacy paths MUST produce a terminal `FAILED` or `SKIPPED + reason` outcome for the affected workflow or item, and MUST NOT trigger substitute execution or workflow continuation by another method.
- Docs, evidence, migration notes, history, and projection metadata MAY record legacy, fallback, or compatibility behavior as recorded truth only; runtime code MUST NOT treat those records as executable authority or use them to select a workflow path.
- Compatibility projections and setup targets MAY exist only as non-authoritative projection or setup records declared by their owning SSOT, and MUST NOT continue a failed primary workflow or substitute for the current runtime contract.
- Cleanup after validation, execution, or commit failure is cleanup-only: release resources, close handles, undo or mark partial writes when applicable, record the terminal outcome, and stop, raise, or return it.
- Cleanup MUST be deterministic and bounded; cleanup failure MUST be recorded explicitly, for example `FAILED_CLEANUP`, and MUST NOT mask the original failure.
- Cleanup MUST NOT run alternate business rules, alternate backends, legacy methods, or substitute workflow steps, and MUST NOT convert a failed or unsupported path into successful continuation.
- Performance, cost, convenience, dependency availability, and environment differences MUST NOT select an alternate runtime path unless that path is the single current SSOT contract for the workflow.
- Defaults and JSON create, normalize, and repair mechanics, their outcomes, and pre-selection validation belong to the config playbook; consumers MUST use that owner.

## Code Comment Policy

- Comments MUST be why-only: invariants, rationale, and safety constraints.
- Prohibited: restating logic or duplicating constants and defaults in comments.
- Comments MUST reference SSOT symbols or modules when a pointer is needed.

## Post-diff jurisdictional purification

After implementation and before closure, MUST review the diff and prove it expresses one jurisdiction per behavior, checking for:

- duplicated literals, predicates, config lists, runtime-path selectors, or outcome meanings;
- wrappers or adapters that bypass the real owner;
- fallback, legacy, compatibility, shadow, or substitute paths in runtime code;
- checker-specific patch logic defining validation semantics belonging to the owner;
- public contract drift without caller-impact evidence and authorization under the contract change gate;
- orphan code, orphan docs, unreferenced helpers, or new files outside their authority parent;
- stale references to retired authority paths.

## Authority Graph (Required for non-trivial systems)

- Non-trivial means more than one workflow entrypoint, or more than one SSOT jurisdiction, or external resource dependencies such as COM, database, or network.
- MUST apply SSOT jurisdiction mechanics and module and folder contracts to build the graph.
- MUST record the authority graph and module boundaries in the architecture project doc, or in the workflow registry when that is the repo's SSOT for entrypoints.
- A project adopting a cross-project governance authority decision MUST reference the governing decision ID from the SSOT authority-decisions owner.
- Project-owner creation and required linkage follow the documentation jurisdiction.

## Witnesses and final report fields

MUST record or be able to report:

- the coding authority owner touched;
- the public contract path and whether the public contract changed;
- preconditions, postconditions, and failure modes covered;
- invariants affected, with witness commands or deterministic manual checks;
- the feature/mechanics composition witness when reusable capability boundaries are in scope: feature owner, mechanics owner, mechanics-shaped instruction contract, operation evidence contract, forbidden caller-policy terms ruled out, and independent-update proof that feature settings can change without mechanics-owner edits while mechanics stay reusable by another caller;
- duplicate, substitute, or fallback logic removed or ruled out;
- valid adapters kept, with their boundary role;
- the deletion-test result showing that deleting one feature folder breaks only its parent entrypoint, or a scoped rationale when the deletion test does not apply;
- README-listed checks run and their outcomes.
