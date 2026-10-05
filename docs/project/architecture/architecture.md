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

## Entrypoints
- Governance constitution: `AGENTS.md`
- Agent lifecycle and workflow: `Orchestration.md`
- Governance Agent authority-routing manifest: `agents-manifest.yaml`
- Docs branch entrypoint: `docs/docs_index.md`
- Supporting governance docs: `docs/agents/agents_index.md`
- Governance-core package: `scripts/check_governance_core/` (launch commands: README Checks)

## SSOT pointers (concept -> owner)
- Fundamental Principles, constitutional rules, conflict precedence, foundation membership, prompt-intake dispositions: `AGENTS.md`
- Agent lifecycle, role boundaries, foundation loading and application evidence, intake sequencing: `Orchestration.md`
- Governance Agent governance-authority routing and detection semantics: `agents-manifest.yaml`
- Cross-doc relations (concept -> owner -> path): `docs/agents/governance/ssot/ssot.md`; jurisdiction hand-off table: `docs/agents/governance/ssot/hand-offs/hand-offs.md`
- Docs placement, headers, durable-record mechanics: `docs/agents/governance/documentation/documentation.md`; project-doc scaffold shape: its `project-docs-template/project-docs-template.md`
- Project truth authority, tracked closure records, non-owner evidence surfaces: `SSOT-DEC-004` in `docs/agents/governance/ssot/authority-decisions/authority-decisions.md`
- Changelog closure records: `docs/project/changelog/changelog.md` owns tracked facts; `SSOT-DEC-004` owns valid/invalid surfaces; `docs/agents/governance/release/release.md` owns field template/order.
- Durable project intent, objective, acceptance criteria, non-goals, verification intent: `docs/project/goal/goal.md`
- Protected behavior records: branch-local architecture subdoc when concrete observable protected behavior exists.
- Project data-truth records: `docs/project/data-truth/data-truth.md`; durable operational learnings: `docs/project/learning/learning.md`
- Governance-core validation, docs router/public-leaf behavior, Python packaged-folder enforcement below the declared source roots: the package public API (`scripts/check_governance_core/__init__.py`); check IDs, order, and reconciliation are private engine facts.
- Repo-owned reusable assets: `docs/agents/governance/skills/`, `docs/agents/governance/settings/`, `docs/agents/governance/mcp/`; runtime config and local-secret boundary: `docs/agents/governance/settings/settings.md`

## Authority graph (owner -> dependents)
- `AGENTS.md` Fundamental Principles and hard gates -> sole canonical text, precedence, owner-local identifiers, coding hard-gate trigger, docs-modularity trigger, and the structural declarations (FP block shape, Mandatory Foundations membership) consumed by lower owners, loaders, prompts, and the governance check; neither Python nor project docs copy principle text or an expected hash.
- `Orchestration.md` -> sole lifecycle authority; its checker-readable contract (delegation, plan fields, message intake) is structurally validated behind the public API; live context isolation, report integration, and YAML instance semantics require agent evidence and independent review.
- `agents-manifest.yaml` -> Governance Agent governance-only profile and fallback routing; it never selects repository or project task sources and does not define the research corpus.
- `docs/agents/governance/documentation/documentation.md` -> sole operative documentation-line-limit and required-project-branch declarations consumed by the docs and project-doc checks; the docs check reads every Markdown member of the bounded repository inventory, while header/router scope stays `docs/`.
- `docs/agents/governance/coding/coding.md` -> coding-principles authority; its `code_decomposition_review_lines` declaration supplies the full-mode Python size warning through the declared coding foundation role; a missing or invalid declaration fails explicitly without a fallback value.
- `scripts/check_governance_core/` -> sole public plain-data API (`__init__.py` re-exports the `__all__` members; `__main__.py` only delegates to `main`); one private registry/engine composes cached document parsing, strict manifest parsing, docs/project checks, governance checks, bounded repository inventory, repository hygiene, folder architecture, and Python safety; private module names are not consumer contracts.
- Root authority order plus `docs/agents/agents_index.md` router topology -> the ordered governance research corpus exposed by `resolve_documents`: `AGENTS.md`, `Orchestration.md`, then routed governance leaves.
- `SSOT-DEC-004` -> project-local docs route durable facts into declared `docs/project/` owner docs; `docs/project/changelog/changelog.md` owns tracked closure-record facts after owner promotion; working and mirror evidence stays non-owner evidence until promoted.
- `docs/agents/governance/principles/principles.md` -> constitutional application mechanics and the baseline/supersession schema; evidence and bugfix are sibling jurisdictions.
- `docs/agents/governance/ssot/ssot.md` -> sole owner of cross-doc relations under `docs/agents/`; owner docs carry no route lines; a moved rule is recorded in its hand-offs sub-doc.
- The inventory owner behind the public checker derives file identity, type, and size from path metadata, revalidates cached family candidates before reads, and rejects changed identities, aliases, non-regular files, and noncanonical resolution; docs validation consumes it directly with keyed parent-child lookup.
- The docs-policy timing witness derives its target from `AGENTS.md` FP-03 and reports attainment or misses; injected filesystem delay is an unmet goal; reporting success is not performance attainment.

## Modularity witness boundary
- Enforced now: checker owners validate the declared docs, folder, manifest, and code-change witness contract facts above, including native-package structure below each Python source root declared in the pack's architecture record at the governance root and, when the repository root differs, in the host's own record at the repository root, each resolved against its own record root (`__init__.py` in every Python-bearing folder; no module directly in a source root; no nested declared roots within or across the two records; no host root inside the governance root; one record read once when the roots coincide) and the native-package interface witnesses (`__all__` declared once, complete and bound in the package entry; non-entry modules `_`-prefixed or `test*`; `__main__.py` limited to imports and one `__name__` guard delegating to a member imported from its package entry; no import of another package's `_` module from outside that package folder, with absolute imports resolved against each declared root's parent directory), except declared packaged-folder exceptions, which are reported as warnings.
- Not claimed: member-level privacy inside modules, child-to-parent or sibling package import direction, imports resolved through any base other than a declared root's parent, an `__all__` declared through an annotated assignment or built from an expression (reported as undeclared), names bound only inside top-level `if` or `try` blocks (reported as unbound), an entry's non-re-export imports (reported as leaked public names), language-general import enforcement, broad hardcoded decision-fact scanning, typed config boundary scanning, selector runtime witnesses without separate structured owners, or that a README launcher command is run from the governance root.
- Re-verify through README Checks when the coding native-package table, the folder-architecture rule, the source-root markers, or the package layout change.

## Packaged-folder adoption (agent decomposition decisions implementing the 2026-10-03 and 2026-10-04 user decisions in `docs/project/goal/goal.md`)
- `scripts/check_governance_core/` is a regular Python package: the entry re-exports only; the public boundary (request validation, dispatch, failure envelopes) is the private `_api` module; the command line (argument parsing, one `dictConfig` logging setup, rendering) is the private `_cli` adapter; the declared-path contract (`canonical_relative`, which rejects `.`, `resolve_declared_file`, `resolve_declared_directory`) is `_declared_paths`, consumed by the manifest, foundation, folder-architecture, and project-branch validators; `MarkdownDocument.markers(token)` is the single owner-marker parser (exact `<!-- token value -->` grammar; blockquoted lines are non-operative); the native-package interface witnesses are `_package_interface` behind the folder-architecture check; `_python_modules` parses each Python source once per run and indexes imports, shared by the folder-architecture and safety checks through `DocumentStore.python_module`; each layout literal (root authority names, `docs`, `docs/agents`, `docs/project`, `SKILL.md`, the manifest path, `__init__.py`) lives in one private module and consumers import it; the default governance root and the docs-policy owner path are each one private constant reused by test support, so every mode yields the same docs result.
- `scripts/` is a declared source root that only contains packages; directory execution of the package folder is unsupported because the launcher performs no import-path manipulation; the superseded custom entry file was removed without a compatibility shim and downstream callers use the README Checks commands.
- The folder-architecture check receives both roots from the engine context: the pack record at the governance root must declare at least one root; the host record at the repository root (read only when that root differs) declares the host's own roots and exceptions and may declare none; a host root inside the governance root is rejected; the merged roots share one nesting rejection; Python is scanned under the repository root; a file outside every declared root is reported against the record that owns its location.
- Test modules mirror private-module jurisdictions: `test_docs_policy` (docs-policy declarations and routers), `test_docs_timing` (the FP-03 docs witness), `test_inventory` (enumeration plus cached-family revalidation), `test_git_capture` (bounded Git capture lifecycle), `test_folder_architecture` (structure, root markers, interface witnesses), `test_orchestration_contract` (authority route and contract graph), `test_orchestration_delegation` (delegation, plan, and message-intake projections); shared orchestration fixtures live in `_test_support`, which validates the unchanged live repository once per process and reuses the memo only while the constitution and every declared foundation file keep their validated file state (other files the validation reads, such as the manifest, are outside the key; no test writes the live tree).
- `X-Bookmarks Import/` is the `SSOT-DEC-001` non-owner workspace and the deferred packaged-folder exception declared below; its two regression tests live beside the scripts they load and run through README Checks, so deleting the workspace breaks only its own tests.

## Reserved jurisdictions
- Reserved, not created: `interfaces/printer`, `interfaces/web-api`, `interfaces/database`, `playbooks/naming`.
- A reserved jurisdiction is declared on first use through a `supersession` record; creating its folder in advance is Prohibited.

## Governance source roots
<!-- governance-core-python-root: scripts -->
<!-- governance-core-python-root: X-Bookmarks Import -->
<!-- governance-core-python-package-exception: X-Bookmarks Import -->
- These owner markers declare the Python source roots the folder-architecture check enforces for the repository that owns this record and the roots exempt from packaged-folder enforcement; the check reads this record at the governance root and a vendored host's own record at the repository root for the host's own roots only (user decisions 2026-10-03 and 2026-10-04 in `docs/project/goal/goal.md`); similarly named paths are not included.

## Retired checker contracts
- Retired change-record checker surfaces are governed by `SSOT-DEC-004`; downstream callers MUST use the current README Checks command list.

## Outputs
- A vendored governance pack under `.governance/` in downstream repos, with constitutional authority at `.governance/AGENTS.md`, lifecycle authority at `.governance/Orchestration.md`, project docs under `docs/project/`, and supporting governance docs under `.governance/docs/agents/`.
- Repo-owned source assets under `docs/agents/governance/skills/`, `docs/agents/governance/settings/`, and `docs/agents/governance/mcp/`.
