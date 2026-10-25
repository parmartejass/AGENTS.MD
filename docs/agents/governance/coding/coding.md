---
doc_type: policy
ssot_owner: docs/agents/governance/coding/coding.md
update_trigger: coding design authority, module boundary, native package mechanics, structural minimality, or coding-principles review obligations change
---

# Coding

Jurisdiction: implementation-code authority owner selection, SSOT jurisdiction mechanics, packaged-folder code mechanics, orchestration boundaries, dependency direction, structural minimality, adapters, runtime-path rules, comments, post-diff purification, and coding-design witnesses.

## Scope

- MUST apply whenever implementation code is planned, added, reviewed, refactored, decomposed, purified, or wired across authority boundaries.
- Applies to code that owns runtime behavior, workflow logic, reusable runtime contracts, packaged folders, public entrypoints, orchestration boundaries or dependency direction.
- A script with owner-declared runtime-selection or validation responsibility MUST expose that responsibility through its declared owner contract, not as a launcher.
- Config payloads, fixtures, schemas and generated artifacts MUST stay out of separate packaged folders until they own runtime behavior.

## SSOT jurisdiction mechanics

Before non-trivial implementation, review, remediation, refactor, or post-diff cleanup, MUST build or derive:

- `jurisdiction_map`: decision-critical fact/state/effect/lifecycle/output/witness -> owner -> public contract.
- `drift_ledger`: duplicate, stale, shadow, patch, compatibility, fallback, test-only, checker-specific, or wrong-owner surfaces.
- `source_level_fix_point`: owner contract, schema, config, validator, workflow, module, registry, scope file, or public entrypoint to strengthen.
- `deletion_reroute_plan`: non-owner code/docs/tests/scripts/prompts/reports/checker logic to delete, move, or reroute.
- `witness_plan`: tests, checks, deterministic manual checks, or review evidence proving owner semantics, no stale references, and no duplicate jurisdiction.

Rules:

- Prohibited ways to preserve drift: wrappers, compatibility branches, local predicates, test-only allowances, checker-specific patches, duplicated constants, fallback paths, private config interpretations, caller-owned copies of owner rules.
- Code existing only to compensate for a missing, weak, stale, ambiguous, or bypassed owner contract MUST be deleted or replaced through the owner.
- Capability modules MUST be designed around the owning contract, not the current patch example.
- Capability modules MUST accept validated intent or plain-data instructions.
- Capability modules MUST report the full work universe: planned, eligible, executed, skipped, failed, and reasons.
- Adding, removing, or wiring behavior MUST update the owner-owned contract, registry, schema, config, scope file, validator, or public entrypoint first.
- Callers, wrappers, sibling modules, tests, docs and checkers MUST consume that owner.
- They MUST take membership, routing, accepted alternatives, ordering, validation predicates, allowed or forbidden paths and lifecycle semantics from the owner and never infer them privately.
- MUST split a feature request into a feature authority and a reusable mechanics authority when its mechanics, external resources, lifecycle handling, validation, operation evidence or transformation behavior can be reused, tested or changed apart from one caller.
- Feature owners MUST keep feature policy, settings intent, required/optional semantics, future extension shape, instruction building, and feature-level success/failure meaning.
- Mechanics owners MUST expose generic operations through mechanics-shaped plain-data instructions and return operation evidence without knowing caller-feature policy.
- Prohibited in a mechanics owner's input: caller-feature policy terms, config keys or defaults, required/optional semantics, domain-specific alternatives, future feature settings, feature-shaped success or failure meanings.
- A mechanics owner that must change whenever one caller feature's settings or policy change has a wrong-owner absorption defect.
- A feature that duplicates the reusable mechanics has bypassed the mechanics boundary.
- Lifecycle, finalization, promotion, cleanup and operation evidence that form one runtime invariant MUST stay inside one stateful mechanics or workflow authority.
- Callers MAY request that capability. Prohibited: a caller recreating or reinterpreting the lifecycle.

## Pre-change coding design review

Before implementation code changes, MUST identify:

- the intended behavior to preserve or strengthen
- the authority owner of each decision-critical responsibility
- the public entrypoint or contract of each touched authority
- the config, constants, schema, data, logging and runtime-path owners the code consumes
- the affected invariants and their deterministic witnesses
- duplicate, substitute, fallback, compatibility, or temporary logic to remove or route to the owner.

Work MUST halt at a missing or conflicting owner (FP-13, FP-27). Prohibited: patching around it with a wrapper, local conditional, compatibility branch or helper that becomes a second owner.

## Packaged-folder code mechanics

- These code mechanics extend FP-13 and the constitutional packaged-folder contract, which owns the rule. This section owns the code mechanics and the private-visibility convention for code.

```yaml
baseline:
  interface: the language's native package and module system
  pattern: "per language, one row of the table below: the native package mechanism, its public-entry file and member declaration, its private-name convention, its launcher form, and the deterministic witness that enforces them"
  reason: "interpreters, import systems, packaging tools, and test runners resolve the native mechanism directly; a custom entry-file convention is a wrapper that needs import-path manipulation and a private checker rule to hold"
  exception: none
```

| Language | Packaged folder | Public entrypoint and members | Private internals | Launcher | Source | Witness |
| --- | --- | --- | --- | --- | --- | --- |
| Python | regular package: a directory with `__init__.py` | `__init__.py`; public members listed in `__all__` | `_`-prefixed modules and names; `test*` modules are test-runner internals | `__main__.py`, run from the import root as `python -m <package>` | Python Language Reference, The import system (regular packages); Python Library Reference, `__main__` | governance-core folder-architecture check: entry presence and source-root containment, `__all__` declared once, complete and bound, `_` or `test` module names, launcher limited to imports and one guarded delegation to its entry, cross-package deep imports. Member-level privacy and child-to-parent import direction stay manual review. |

- Before code in a language absent from this table relies on it, the project architecture record MUST record that language's packaged folder, public entrypoint and members, private-visibility mechanism, launcher, authoritative source and deterministic witness.
- Adopting such a language in the governance source adds its row to this table.
- A declared source root, as the Lexicon (ssot) defines it, exposes no public entrypoint and is declared by the project architecture record.
- A root launcher, as the Lexicon (ssot) defines it, is a custom entry-file exception.
- A root launcher MUST only delegate to one packaged folder's public entry; its launch adaptation stays an FP-21 adapter.
- A root launcher is permitted only when the project architecture record declares it with `<!-- governance-core-root-launcher: <file> -->` beside the user decision and its re-evaluation trigger.
- The folder-architecture check accepts exactly the declared Python files and reports each one as a re-evaluation warning.
- Imports between modules of one packaged folder are internal.
- Prohibited: a caller outside the folder importing its private modules (deep import).
- Prohibited: a child package importing a sibling or parent package.
- A package's own tests are package internals.
- Every caller outside the package, including another package's tests, MUST use only its public members.
- Public contracts MUST accept and return plain data.
- Live handles and external resources MUST stay behind the owning boundary.
- Parent public entrypoints are the only connectors across child authorities.
- Public entrypoints and launchers MUST stay thin and import-safe.
- Public entrypoints MUST only orchestrate; private modules hold the detailed logic.
- Documentation-only structure changes follow the documentation jurisdiction.

## Orchestration boundaries

- Orchestration code MAY:
  - order already-authoritative steps
  - pass plain data between authority entrypoints
  - enforce the workflow state machine
  - record phase transitions and outcomes
  - invoke bounded cleanup.
- Orchestration code MUST take these from their owners: business rules, validation predicates, constants and defaults, backend-selection rules, lifecycle policies, retry policy, GUI-thread safety, COM safety, subprocess safety, and UI/checkbox semantics.
- Any decision-critical branch in orchestration MUST call a named authority-owned rule, config, or lifecycle contract and record the selected authority path before execution.
- After validation, execution, commit, or cleanup failure, orchestration MUST emit the terminal outcome and stop that branch.

## Dependency direction

- Config, constants, schema and data-shape owners are leaf dependencies.
- Workflows compose authorities.
- UI calls workflows.
- UI, CLI, prompts and checkboxes MUST supply intent inputs only.
- Business rules, workflow branching, constants, config meaning and workflow eligibility MUST stay with their owners, never with UI, CLI, prompts or checkboxes.
- Composing an authority MUST leave ownership with the composed child.
- A parent MAY decide from a validated runtime plan whether to call a child.
- Prohibited: a parent inspecting, duplicating or reimplementing the child's private logic.
- Dependency graphs across authority boundaries MUST remain acyclic.
- `shared/` MAY contain only owner-neutral, pure or stateless shapes, protocols, or utilities whose semantics route to another declared owner.
- Prohibited in `shared/`: feature policy, workflow mechanics, config or default interpretation, validation predicates, branching, lifecycle or resource handling, outcome meanings, mechanics orchestration, caller-specific instruction builders.
- Shared code that must change for one feature's settings or policy belongs in that feature, mechanics, config or schema owner.
- Consumer boundaries MUST use explicit parameter or constructor injection.
- Extensible capabilities MUST expose bounded authoritative discovery or registered handlers on the owning composition contract.
- They MUST record discovery scope, ordering, validation, termination, cost, cache invalidation and explicit unsupported outcomes.
- Consumers MUST receive the resolved contract.
- Prohibited: consumer-implemented discovery, hardcoded open-world capability lists, unowned service location, unbounded dynamic wiring, eval-based wiring.

## Structural minimality

code_decomposition_review_lines: 400

- That operative declaration is the only code-size review value: one positive decimal integer.
- Examples in fences, indented code or quotes supply no value.
- Governance-core reads the value with no default. It counts `str.splitlines()` records, comments and blanks included, for its Python structural subset, and warns only above the declared value.
- The default implementation path MUST be the smallest authority-correct design that preserves or strengthens behavior.
- That path MUST use the existing owner-owned contracts, registries, schemas, config, validators and entrypoints when they cover the responsibility.
- Prohibited: repeated local conditionals, checker-specific patch logic.
- MUST split inside the same folder first.
- Promotion to a child folder MUST wait until the behavior becomes independently owned.
- Before adding logic to an entrypoint, MUST check the boundary signals: distinct invariants or rules, distinct lifecycle or state handling, distinct I/O boundary or side effects, independent testability, separate owner update triggers or independent change cadence.
- With any signal present, MUST create or extend private files or child folders under the same authority parent first.
- With no signal present, the logic stays in the entrypoint.
- MUST record the decomposition decision and its witness against this doc in the confirmed plan or the role-bounded agent report.
- MUST promote or extend reusable mechanics only when boundary signals show the capability can be reused, tested or changed on its own while caller-feature policy stays in the feature owner.
- Request-specific logic stays in its current authority with a recorded rationale.
- A file over `code_decomposition_review_lines`, or one the current change would push over it, triggers a coding-principles review of the affected responsibility.
- That review covers all applicable owners, contracts, entrypoints, call sites, and the current-module, workflow, feature-folder, reusable-mechanics, `shared/`, script/checker, config/schema/data-owner, adapter, public-entrypoint, duplicate-pruning, deletion, and reroute boundaries.
- This whole doc MUST be applied before closure, as with any other change.
- LOC reduction is valid closure evidence only when correctness, validation, explicit outcomes, observability, witnesses, SSOT jurisdiction and routing, and public-contract clarity remain intact.
- A remaining LOC increase MUST be justified by required behavior, stronger validation, stronger observability or clearer authority boundaries.

## Contract change gate

- Before changing a public entrypoint, MUST record the current and proposed contracts with their FP-14 fields, the identified active callers, the migration and removal impact, and deterministic compatibility witnesses.
- The assigned execution agent MAY change private internals within its authorized assignment while the public contract stays stable and recorded witnesses prove behavior preservation or authorized strengthening.

## Valid and Invalid Adapters

Valid adapters MUST:

- record the adapter justification, owning boundary, authorized scope and review witness
- isolate external I/O, subprocess, GUI, COM, network, file or platform APIs at the owning boundary
- translate only transport or representation between external formats and owner-issued plain-data contracts, preserving owner-issued semantic values exactly
- report failures through the logging and outcome owner and choose no substitute behavior
- stay private unless they are the authority's declared public entrypoint.

Semantic resolution and correction stay with the declared owner under `AGENTS.md` Resolve once before fan-out.

Prohibited adapter behavior (invalid adapters):

- choosing a fallback, legacy, compatibility or substitute runtime path after failure
- duplicating config defaults, constants, validation predicates or business rules
- hiding a missing owner behind a permissive wrapper
- exposing a second public entrypoint for the same authority
- making cleanup run alternate business logic or convert failure into success.

## No Duplicates

- Each literal with one meaning MUST appear once across files and docs.
- Each conditional logic block or rule MUST appear once across files.
- Prohibited: copy/paste helpers with minor variations.
- Witness: the folder-architecture check warns when a module-level constant name is bound in more than one module (repeat report).

## No Fallback or Legacy Runtime Paths

- MUST choose one explicit deterministic runtime path from the current SSOT contract.
- Prohibited in runtime code: implementing or selecting a fallback, legacy, compatibility, shadow, downgrade or substitute execution branch for the same responsibility.
- An unsupported, unverified, unavailable, retired or legacy path MUST produce a terminal `FAILED` or `SKIPPED + reason` outcome for the affected workflow or item.
- Such a path MUST NOT trigger substitute execution or continue the workflow by another method.
- Docs, evidence, migration notes, history and projection metadata MAY record legacy, fallback or compatibility behavior as recorded truth only.
- Runtime code MUST NOT treat those records as executable authority or use them to select a workflow path.
- Compatibility projections and setup targets MAY exist only as non-authoritative projection or setup records declared by their owning SSOT.
- They MUST NOT continue a failed primary workflow or substitute for the current runtime contract.
- Cleanup after validation, execution or commit failure is cleanup-only. It releases resources, closes handles, undoes or marks partial writes when applicable, records the terminal outcome, and stops, raises or returns it.
- Cleanup MUST be deterministic and bounded.
- Cleanup failure MUST be recorded explicitly, for example `FAILED_CLEANUP`, and MUST NOT mask the original failure.
- Prohibited in cleanup: alternate business rules, alternate backends, legacy methods, substitute workflow steps, and turning a failed or unsupported path into successful continuation.
- Performance, cost, convenience, dependency availability and environment differences MUST NOT select an alternate runtime path. The one exception: that path is the single current SSOT contract for the workflow.
- The config playbook owns defaults, the JSON create, normalize and repair mechanics, their outcomes, and pre-selection validation. Consumers MUST use that owner.

## Code Comment Policy

- Comments MUST be why-only: invariants, rationale, and safety constraints.
- Prohibited in comments: restated logic, duplicated constants and defaults.
- Comments MUST reference SSOT symbols or modules when a pointer is needed.

## Post-diff jurisdictional purification

After implementation and before closure, MUST review the diff and prove it expresses one jurisdiction per behavior, checking for:

- duplicated literals, predicates, config lists, runtime-path selectors or outcome meanings
- wrappers or adapters that bypass the real owner
- fallback, legacy, compatibility, shadow, or substitute paths in runtime code
- checker-specific patch logic that defines validation semantics the owner holds
- public contract drift without caller-impact evidence and authorization under the contract change gate
- orphan code, orphan docs, unreferenced helpers or new files outside their authority parent
- stale references to retired authority paths.

## Authority Graph (Required for non-trivial systems)

- The Lexicon (ssot) defines "non-trivial" for this section.
- MUST apply SSOT jurisdiction mechanics and packaged-folder code mechanics to build the graph (FP-13).
- MUST record the authority graph and module boundaries in the architecture project doc. When the workflow registry is the repo's SSOT for entrypoints, MUST record them there instead.
- A project adopting a cross-project governance authority decision MUST reference the governing decision ID from the SSOT authority-decisions owner.
- Project-owner creation and required linkage follow the documentation jurisdiction.

## Witnesses and final report fields

MUST record or be able to report:

- the coding authority owner touched
- the public contract path, and whether the public contract changed
- the preconditions, postconditions and failure modes covered
- the invariants affected, with witness commands or deterministic manual checks
- the feature/mechanics composition witness when reusable capability boundaries are in scope: feature owner, mechanics owner, mechanics-shaped instruction contract, operation evidence contract, forbidden caller-policy terms ruled out, and independent-update proof (feature settings change with no mechanics-owner edit, and the mechanics stay reusable by another caller)
- the duplicate, substitute or fallback logic removed or ruled out
- the valid adapters kept, with their boundary role
- the deletion-test result (FP-13): deleting one packaged folder breaks only its parent's public entrypoint, or a scoped rationale when the deletion test does not apply
- README-listed checks run and their outcomes.
