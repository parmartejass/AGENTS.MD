---
doc_type: reference
ssot_owner: docs/project/architecture/architecture.md
update_trigger: repo layout, authority-routing profiles, or validation scripts change
---

# Architecture

## Boundary
- This root doc owns architecture pointers, responsibility splits, authority graph summaries, and structural relationships.
- It does not own durable project goal, reusable governance policy, data-truth records, closure records, learnings, source payloads, or work status.

## Current Summary
- The repo is a governance-pack source: reusable policy and source assets under `docs/agents/`, project authority docs under `docs/project/`, validation scripts under `scripts/`.
- `docs/agents/` has three stable layers: `governance/` (task jurisdictions, including the skills, settings, MCP, hooks, and dependencies standards), `interfaces/` (external systems), and `playbooks/` (design choices for internal layers); each jurisdiction is one packaged folder `<name>/<name>.md` plus `<name>_index.md` with no numeric prefixes.

## Branch-local owner subdocs
- None currently declared.
- Create an architecture subdoc when a stable structural truth cluster needs its own intent, boundary, invariant, change rule, and verification.
- Use a protected-behavior subdoc only when observable behavior is user-protected, regression-sensitive, or replaceable only under an equivalence rule.

## Entrypoints
- Governance constitution: `AGENTS.md`
- Agent lifecycle and workflow: `Orchestration.md`
- Governance Agent authority-routing manifest: `agents-manifest.yaml`
- Docs branch entrypoint: `docs/docs_index.md`
- Supporting governance docs: `docs/agents/agents_index.md`
- Governance-core package: `scripts/check_governance_core/` (launch commands: README Checks)

## SSOT pointers (concept -> owner)
- Fundamental Principles, constitutional rules, conflict precedence: `AGENTS.md`
- Agent lifecycle and role boundaries: `Orchestration.md`
- Governance Agent governance-authority routing: `agents-manifest.yaml`
- Cross-doc relations (concept -> owner -> path): `docs/agents/governance/ssot/ssot.md`
- Jurisdiction hand-off table: `docs/agents/governance/ssot/hand-offs/hand-offs.md`
- Docs placement, headers, durable-record mechanics: `docs/agents/governance/documentation/documentation.md`
- Project-doc scaffold shape: `docs/agents/governance/documentation/project-docs-template/project-docs-template.md`
- Project truth authority, tracked closure records, non-owner evidence surfaces: `SSOT-DEC-004` in `docs/agents/governance/ssot/authority-decisions/authority-decisions.md`
- Changelog closure records: `docs/project/changelog/changelog.md` owns tracked facts; `SSOT-DEC-004` owns valid/invalid surfaces; `docs/agents/governance/release/release.md` owns field template/order.
- Durable project intent, objective, acceptance criteria, non-goals, verification intent: `docs/project/goal/goal.md`
- Protected behavior records: branch-local architecture subdoc when concrete observable protected behavior exists.
- Project data-truth records: `docs/project/data-truth/data-truth.md`
- Durable operational learnings: `docs/project/learning/learning.md`
- Governance-core validation, including docs router/public-leaf behavior: governance-core package public API (`scripts/check_governance_core/__init__.py`)
- Python packaged-folder structure and interface enforcement below the source roots declared by the pack record at the governance root and the host record at the repository root: governance-core public contract
- Governance-core check IDs, order, reconciliation: private engine behind that public API; consumers use only the public API.
- Repo-owned reusable assets: `docs/agents/governance/skills/`, `docs/agents/governance/settings/`, `docs/agents/governance/mcp/`
- Runtime config and local-secret boundary: `docs/agents/governance/settings/settings.md`

## Authority graph (owner -> dependents)
- `AGENTS.md` Fundamental Principles and hard gates -> sole canonical text, precedence, owner-local identifiers, coding hard-gate trigger, docs-modularity trigger, and structural declaration consumed by lower owners, loaders, prompts, and checks.
- Lower declared owners retain binding rules within their jurisdictions; the constitutional conflict boundary does not demote them.
- The governance-core governance check derives block/heading/paragraph shape from that declaration; shared test support reads the live owner section.
- Neither Python nor project docs copy principle text or its expected hash; exact source equality and semantic compliance require separate evidence under FP-33.
- `Orchestration.md` -> sole detailed lifecycle authority consumed by loaders, prompts, support docs, agents, and orchestration checks.
- Its owner-declared delegation and plan projections are structurally validated behind the governance-core public API.
- Live context isolation, report integration, and YAML instance semantics require agent evidence and independent review, not a structural-checker claim.
- `agents-manifest.yaml` -> Governance Agent governance-only profile and fallback authority routing; it never selects repository or project task sources.
- `docs/agents/governance/documentation/documentation.md` -> sole operative documentation-line-limit and required-project-branch declarations consumed by the governance-core docs/project-doc handlers.
- Shared document parsing preserves physical LF evidence and derives filenames through the established contract.
- The docs handler reads every Markdown member of the bounded repository inventory; header/router scope remains `docs/`.
- Missing, ambiguous, or unsafe declarations and aliased or undecodable files fail explicitly; incidental AGENTS paths do not define the required set.
- `docs/agents/governance/documentation/documentation.md` -> bounded project authority-memory policy; project-doc leaves own the routed records it declares.
- `docs/agents/governance/coding/coding.md` -> single delegated coding-principles and runtime-code authority-design jurisdiction under the coding hard-gate trigger.
- Its `code_decomposition_review_lines` declaration supplies the full-mode Python size warning through the declared coding foundation role, replacing the checker-owned copy.
- Shared positive-integer document parsing serves coding and documentation declarations; counting, severity, and scope remain distinct.
- Missing or invalid coding declarations fail explicitly without a fallback value.
- `scripts/check_governance_core/` package -> sole public plain-data API (`__init__.py` only re-exports the `__all__` members bound in the private boundary module) and CLI (`__main__.py` only delegates to `main`, the private command-line adapter); package-internal tests exercise the public API and private modules, while external consumers use only the public members; one private registry/engine composes cached document parsing, strict manifest parsing, docs/project checks, governance checks, bounded repository inventory, repository hygiene/structure, and Python safety.
- Private module names are not consumer contracts.
- Root authority order plus `docs/agents/agents_index.md` router topology -> complete ordered governance research corpus exposed by `resolve_documents`: `AGENTS.md`, `Orchestration.md`, then routed governance leaves.
- `agents-manifest.yaml` remains Governance Agent routing data and does not define corpus membership.
- `docs/agents/governance/skills/` -> reusable skill bundles.
- `docs/agents/governance/settings/` -> shared settings sources and local-secret boundary.
- `docs/agents/governance/mcp/` -> canonical non-secret MCP payloads.
- `SSOT-DEC-004` -> project-local docs route durable facts into declared `docs/project/` owner docs; `docs/project/changelog/changelog.md` owns tracked closure-record facts after owner promotion.
- Working evidence and mirror closure evidence remain non-owner evidence unless promoted into the declared owner.
- `docs/agents/governance/ssot/authority-decisions/authority-decisions.md` -> allows `X-Bookmarks Import/` as a non-owner workspace exception without making it a canonical governance root.
- `X-Bookmarks Import/skills/governance-autoresearch/scripts/governance_research.py` -> research input collection only; its workspace skill routes governance changes to `AGENTS.md` and `Orchestration.md`.
- The X scripts own local CLI, default, and scoring behavior; current external API facts resolve through the canonical X API skill and X's active contract.
- `docs/agents/governance/principles/principles.md` -> delegated constitutional application mechanics and the baseline/supersession schema; evidence and bugfix are sibling governance jurisdictions with their own owner docs.
- `docs/agents/governance/ssot/ssot.md` -> sole owner of cross-doc relations under `docs/agents/`; owner docs carry no route lines, and a jurisdiction hand-off is recorded in its hand-offs sub-doc when a rule is moved between owners.
- Exact Fundamental Principles remain exclusively in `AGENTS.md`.
- The inventory owner behind the public checker derives file identity, type, and size from authoritative path metadata and revalidates cached family candidates before reads.
- It rejects changed identities, aliases, non-regular files, noncanonical resolution, and metadata failures.
- Docs validation consumes that owner directly and maintains no second per-file safety loop; keyed parent-child lookup removes repeated docs-tree scans.
- The docs-policy timing witness derives its target from `AGENTS.md` FP-03 and reports attainment or misses for corpus preparation, fresh inventories, direct decisions, complete cold/warm handlers, and the full timing scenario.
- Decision assertions, handler validation, and inventory equivalence remain required; injected filesystem delay MUST be reported as an unmet goal.
- This supersedes the earlier decision-only interpretation; reporting success is not performance attainment.
- Uninstrumented work remains explicit through the evidence owner; re-verify through README Checks when the timing witness or its owner changes.

## Foundation ownership and validation
- The 2026-09-13 keep-locations decision is recorded in `docs/project/goal/goal.md`.
- `AGENTS.md` Mandatory Foundations is the sole versioned membership declaration.
- `Orchestration.md` consumes it for parent reads, application evidence, missing-source outcomes, and context transitions.
- This keeps constitutional choice separate from lifecycle mechanics without moving or copying owners.
- Loaders, shared compaction instructions, foundation routers, and `agents-manifest.yaml` route to those owners.
- The manifest selects additional authorities only; the obsolete foundation-only coding profile and conditional foundation entries are removed.
- Applicable deeper owners retain their duties and owner-declared optionality.
- The governance-core boundary parses the declaration once per full run, retains validated role/path pairs once, derives the ordered authority view, and passes the coding-role path to folder validation.
- Canonical file identity and strict reads remain inventory/document responsibilities.
- Malformed, missing, unsafe, aliased, or unreadable foundations fail explicitly without fallback membership; private implementation stays behind the unchanged public API.
- Foundation fixture support consumes public `run_checks` governance success before extracting literal owner markers as mutation data.
- It neither validates membership itself nor imports the private foundation parser; the 2026-09-13 correction removed that caller dependency.
- A temporary-copy witness renames the private parser and its internal call: public validation stays valid, fixture imports fail before correction, fixture setup passes afterward.
- Regression coverage proves rejected public validation prevents owner-data extraction.
- `resolve_documents` remains the independent router-owned research corpus with its existing root prefix and DFS contract; mandatory startup loading is not a new corpus selector.
- Narrow docs and project-doc modes retain their own required authorities and acquire no unrelated foundation or profile blockers.
- Verification resolves through README Checks and focused public-API foundation scenarios.
- Structural passes prove declaration and routing behavior, not live application, source-isolated reasoning, future platform autoloading, or uninstrumented timing.
- Re-verify on foundation/lifecycle, checker, routing, or public-contract changes.

## Prompt-intake contract and validation
- `AGENTS.md` User Prompt Intake and Durable Project Truth owns prompt-originated constitutional semantics; documentation retains admission, placement, provenance, redaction, and safe supersession, with relations routed by the SSOT map.
- `Orchestration.md` contract version 3 owns `message_intake`, `prompt_intake`, parent continuation, outcome-specific intake returns, and prospective plan migration; role and state vocabularies remain unchanged.
- The existing governance-core public API consumes that projection through its private orchestration/delegation validators. Parsed task roles and plan fields are reused for cross-links; no public API, new module, copied outcome vocabulary, or prose-keyword check was introduced.
- This replaces the scattered constitutional prompt bullets and late-only maintenance route; fixtures continue consuming the live owner, and unsupported old contract declarations fail explicitly without a runtime fallback.
- Verified on 2026-09-28 through README Checks: focused orchestration cases and the full 124-test suite passed (one existing native-symlink privilege skip), as did docs, project-docs, full and strict governance checks. Re-verify when intake ownership, schema, consumers, source boundaries, or accepted intent changes.
- Structural success does not prove live capture order, complete materiality, correct semantic ownership, or agent obedience; those require workflow evidence and independent review. End-to-end verification exceeded the constitutional timing target; uninstrumented model/platform work remains unverified.

## Cleanup authority consolidation

- Agent decision, 2026-10-02: two private result constructors inside `scripts/check_governance_core/` replace repeated envelopes behind the unchanged public API; the ordered `EMITTERS` registry in `X-Bookmarks Import/skills/x-research/scripts/x_search.py` owns mode membership and dispatch.
- Owner-routed loader, scaffold, configuration, hand-off and router cleanup retains unique obligations in their existing authorities; dead private members and duplicate declarations are removed under those contracts.
- The canonical [Changelog](../changelog/changelog.md) delegates earlier evidence to [Changelog History](../changelog/history.md); current closure records remain in the owner and archival evidence retains its recorded review qualifications.
- Verification and re-verification follow README Checks, frozen public/engine/CLI outputs, byte-preserved history and independent owner-equivalence review; rerun when these owners, contracts, registry, archive or consumers change.

## Current modularity witness boundary
- Enforced now: checker owners validate the declared docs, folder, manifest, and code-change witness contract facts above, including native-package structure below each Python source root declared in the pack's architecture record at the governance root and, when the repository root differs, in the host's own record at the repository root, each resolved against its own record root (`__init__.py` in every Python-bearing folder; no module directly in a source root; no nested declared roots within or across the two records; no host root inside the governance root; one record read once when the roots coincide) and the native-package interface witnesses (`__all__` declared once, complete and bound in the package entry; non-entry modules `_`-prefixed or `test*`; `__main__.py` limited to imports and one `__name__` guard delegating to a member imported from its package entry; no import of another package's `_` module from outside that package folder, with absolute imports resolved against each declared root's parent directory), except declared packaged-folder exceptions, which are reported as warnings.
- Not claimed: member-level privacy inside modules, child-to-parent or sibling package import direction, imports resolved through any base other than a declared root's parent, an `__all__` declared through an annotated assignment or built from an expression (reported as undeclared), names bound only inside top-level `if` or `try` blocks (reported as unbound), an entry's non-re-export imports (reported as leaked public names), language-general import enforcement, broad hardcoded decision-fact scanning, typed config boundary scanning, selector runtime witnesses without separate structured owners, or that a README launcher command is run from the governance root.

## Packaged-folder adoption
- Agent decision implementing the 2026-10-03 user decisions in `docs/project/goal/goal.md` (consolidated packaged-folder rule, full migration, retained router naming, deferred X workspace): `scripts/check_governance_core/` is a regular Python package with its `__init__.py` public API, a `__main__.py` launcher that only delegates to `main` and runs from the governance root as a module, `_`-prefixed private modules, and package-internal tests and fixtures; `scripts/` is a declared source root that only contains packages.
- Agent decomposition decision, 2026-10-03 (SRP follow-up authorized in `docs/project/goal/goal.md`): the entry re-exports only; the public boundary (request validation, dispatch, failure envelopes) is the private `_api` module and the command line (argument parsing, one `dictConfig` logging setup, rendering) is the private `_cli` adapter, split on distinct I/O boundaries and change cadence; the owner-declared path contract (`canonical_relative`, `resolve_declared_file`, `resolve_declared_directory`) is the private `_declared_paths` module consumed by the manifest, foundation, folder-architecture and project-branch validators; `MarkdownDocument.markers(token)` is the single owner-marker parser (exact `<!-- token value -->` grammar; blockquoted lines are non-operative); the native-package interface witnesses are the private `_package_interface` module behind the folder-architecture check (AST parse boundary and independently testable rules); the default governance root and the docs-policy owner path are each one private constant reused by test support, and narrow docs modes keep that path without the foundation declaration so every mode yields the same docs result.
- Agent decision, 2026-10-04, implementing the 2026-10-04 user decision in `docs/project/goal/goal.md`: the folder-architecture check receives both roots from the engine context; the pack record at the governance root must declare at least one root, the host record at the repository root (read only when that root differs) declares the host's own roots and exceptions and may declare none, a host root inside the governance root is rejected because the pack record owns it, the merged roots share one nesting rejection, Python is scanned under the repository root, and a file outside every declared root is reported against the record that owns its location; no root list or limit is hardcoded.
- Test modules follow the same jurisdictions: `test_docs_policy` (docs-policy declarations and routers), `test_docs_timing` (the FP-03 docs witness), `test_inventory` (enumeration plus cached-family revalidation), `test_git_capture` (bounded Git capture lifecycle), `test_folder_architecture` (structure, root markers, interface witnesses), `test_orchestration_contract` (authority route and contract graph) and `test_orchestration_delegation` (delegation, plan and message-intake projections). Agent decision 2026-10-05 (Msg9 stability workflow) superseding the whole-file rationale: the delegation tests mirror the separate `_orchestration_delegation` rules module and the capture tests mirror `_git_capture`, so both split along existing module boundaries; shared orchestration fixtures live in `_test_support`.
- The superseded custom entry file was removed without a compatibility shim; downstream callers use the README Checks commands. Directory execution of the package folder is unsupported because the launcher performs no import-path manipulation.
- Docs folders keep the `<authority>_index.md` router as their public entrypoint, the retained exception recorded in `SSOT-DEC-003`.
- `X-Bookmarks Import/` is the declared packaged-folder exception below: its flat modules and directly launched skill scripts stay non-conformant until the re-evaluation trigger in `docs/project/goal/goal.md`; its two regression tests live beside the scripts they load (`skills/*/scripts/test_*.py`) and run through README Checks, so deleting the workspace breaks only its own tests (deletion test restored 2026-10-03).
- Verification: README Checks, including the launcher subprocess, `__all__`, README-reference, package-structure, root-marker and interface witnesses; re-verify when the coding native-package table, the folder-architecture rule, the source-root markers, or the package layout change.

## Stability hardening (2026-10-05)
- Agent decisions, Msg9/Msg10 stability workflow (CH-20261005-001) within the 2026-10-05 stability-scope decision in `docs/project/goal/goal.md`; private internals behind the unchanged public API.
- One literal per layout fact: root authority names, the `docs`, `docs/agents` and `docs/project` roots and `SKILL.md` live in `_documents`; the manifest path in `_manifest`; the native package entry `__init__.py` in `_package_interface`; consumers import them.
- `canonical_relative` rejects a path without parts (`.`), so every declared-path consumer fails at the path owner instead of resolving its own root.
- Per-run parse cache: `DocumentStore.python_module` caches one parse per decoded source from the private `_python_modules` parser, which indexes import statements by a statement-only breadth-first walk equal to the `ast.walk` order (split from `_documents` at the decomposition trigger: distinct rules and tests); folder-architecture witnesses and Python safety share it. Safety keeps `tokenize` source decoding; the key is the resolved path plus decoded text. Deep-import owners resolve through the inventory's package entries, not filesystem probes. Invalidation: one store per run.
- `agents-manifest.yaml` `profiles.packaging.detect.keywords`: the bare `package` keyword, which matched packaged-folder prompts, is replaced by narrow release-artifact phrases (the list stays in the manifest); packaged-folder prompts no longer route release-packaging authorities while release-artifact prompts still do, checked under case-insensitive substring and whole-word readings.
- Test support validates the unchanged live repository once per process; the memo is reused only while the constitution and every declared foundation file keep the file state they had when validated, and each fixture still runs its own checks; other files the validation reads (for example the manifest) are outside the key, and no test writes the live tree.
- FP-03: measured before/after values and their classification live in CH-20261005-001; interpreter start plus package import take roughly 95 ms on the measuring host before any check runs, so the narrow modes sit near 100 ms and full and strict stay above it. Re-verify through README Checks when these modules, fixture support or the manifest profiles change.

## Reserved jurisdictions
- Reserved, not created: `interfaces/printer`, `interfaces/web-api`, `interfaces/database`, `playbooks/naming`.
- A reserved jurisdiction is declared on first use through a `supersession` record; creating its folder in advance is Prohibited.

## Governance source roots
<!-- governance-core-python-root: scripts -->
<!-- governance-core-python-root: X-Bookmarks Import -->
<!-- governance-core-python-package-exception: X-Bookmarks Import -->
- These owner markers declare the Python source roots the folder-architecture check enforces for the repository that owns this record and the roots exempt from packaged-folder enforcement; the check reads this record at the governance root, a known input of the check, and a vendored host's own record at the repository root for the host's own roots only (user decisions 2026-10-03 and 2026-10-04 in `docs/project/goal/goal.md`), so a host never re-declares these roots and a host without Python outside the pack declares none.
- `X-Bookmarks Import/` remains the non-owner workspace exception governed by `SSOT-DEC-001` and the deferred packaged-folder exception decided on 2026-10-03 in `docs/project/goal/goal.md`; similarly named paths are not included.

## Retired checker contracts
- Retired change-record checker surfaces are governed by `SSOT-DEC-004`.
- Replacement verification path: route durable facts through the owning project docs and run the README Checks project-doc, docs-router, and governance-core commands.
- Downstream callers MUST use the current README Checks command list.

## Outputs
- A vendored governance pack under `.governance/` in downstream repos, with constitutional authority at `.governance/AGENTS.md`, lifecycle authority at `.governance/Orchestration.md`, project docs under `docs/project/`, and supporting governance docs under `.governance/docs/agents/`.
- Repo-owned source assets under `docs/agents/governance/skills/`, `docs/agents/governance/settings/`, and `docs/agents/governance/mcp/`; runtime installation is consumer-owned and not a tracked repo output.
