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
- `docs/agents/` has three stable layers: `docs/agents/governance/` (task jurisdictions, including the skills, settings, MCP, hooks, and dependencies standards), `docs/agents/interfaces/` (external systems), and `docs/agents/playbooks/` (design choices for internal layers).
- Each jurisdiction is one packaged folder `<name>/<name>.md` plus `<name>_index.md`, named under `docs/project/rules/rules.md`.

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
- Project data-truth records: `docs/project/data-truth/data-truth.md`
- Durable operational learnings: `docs/project/learning/learning.md`
- Governance-core validation, docs router and public-leaf behavior, and Python packaged-folder enforcement below the declared source roots: the package public API (`scripts/check_governance_core/__init__.py`).
- Check IDs, order, and reconciliation are private engine facts.
- Repo-owned reusable assets: `docs/agents/governance/skills/`, `docs/agents/governance/settings/`, `docs/agents/governance/mcp/`; runtime config and local-secret boundary: `docs/agents/governance/settings/settings.md`

## Authority graph (owner -> dependents)
- `AGENTS.md` Fundamental Principles and hard gates -> sole canonical text, precedence, owner-local identifiers, the coding and docs-modularity hard-gate triggers, and the structural declarations (FP block shape, Mandatory Foundations membership) consumed by lower owners, loaders, prompts, and the governance check.
- Python and project docs hold no copy of principle text and no expected hash.
- `Orchestration.md` -> agent lifecycle; its checker-readable contract (delegation, plan fields, message intake) is structurally validated behind the public API; live context isolation, report integration, and YAML instance semantics require agent evidence and independent review.
- `agents-manifest.yaml` -> Governance Agent profile and fallback routing, within the source boundary of `Orchestration.md` Task agents and focused exploration.
- `docs/agents/governance/documentation/documentation.md` -> the sole operative declarations of the documentation line limit, the required project branches, and the repeat-report settings (its Validation boundary), consumed by the docs and project-doc checks.
- The docs check reads every Markdown member of the bounded repository inventory; header and router scope stays `docs/`.
- Repeat report: one private `_repeat_report` module serves the docs and folder-architecture checks; owners: `docs/agents/governance/documentation/documentation.md` Validation boundary and `docs/agents/governance/coding/coding.md` No Duplicates.
- `docs/agents/governance/coding/coding.md` -> coding-principles authority. Its `code_decomposition_review_lines` declaration supplies the full-mode Python size warning through the declared coding foundation role. A missing or invalid declaration fails explicitly, with no fallback value.
- `scripts/check_governance_core/` -> the one public plain-data API: `__init__.py` re-exports the `__all__` members, and `__main__.py` only delegates to `main`.
- One private registry and engine composes cached document parsing, strict manifest parsing, docs and project checks, governance checks, bounded repository inventory, repository hygiene, folder architecture, and Python safety. Private module names are not consumer contracts.
- Root authority order plus `docs/agents/agents_index.md` router topology -> the ordered governance research corpus exposed by `resolve_documents`: `AGENTS.md`, `Orchestration.md`, then routed governance leaves.
- `SSOT-DEC-004` -> project-local docs route durable facts into declared `docs/project/` owner docs; `docs/project/changelog/changelog.md` owns tracked closure-record facts after owner promotion; working and mirror evidence stays non-owner evidence until promoted.
- `docs/agents/governance/principles/principles.md` -> constitutional application mechanics and the baseline/supersession schema; evidence and bugfix are sibling jurisdictions.
- `docs/agents/governance/ssot/ssot.md` -> cross-doc relations under `docs/agents/` (its Relation routing rule).
- The inventory owner behind the public checker derives file identity, type, and size from path metadata. It revalidates cached family candidates before reads and rejects changed identities, aliases, non-regular files, and noncanonical resolution. Docs validation consumes it directly with keyed parent-child lookup.
- The docs-policy timing witness derives its target from `AGENTS.md` FP-03 and reports attainment or misses; injected filesystem delay is an unmet goal; reporting success is not performance attainment.

## Modularity witness boundary
- Enforced now: checker owners validate the declared docs, folder, manifest, and code-change witness contract facts above.
- They enforce native-package structure below each Python source root declared in the pack's architecture record at the governance root and, when the repository root differs, in the host's own record at the repository root. Each root resolves against its own record root.
- Structure witnesses: `__init__.py` in every Python-bearing folder; no module directly in a source root; no nested declared roots within or across the two records; no host root inside the governance root; one record read once when the roots coincide.
- Interface witnesses: `__all__` declared once, complete and bound in the package entry; non-entry modules `_`-prefixed or `test*`; `__main__.py` limited to imports and one `__name__` guard delegating to a member imported from its package entry; no import of another package's `_` module from outside that package folder, with absolute imports resolved against each declared root's parent directory.
- Declared packaged-folder exceptions are reported as warnings.
- A Python file outside every declared root fails unless its record declares it as a root launcher (an existing `.py` file directly in that record's root, reported as a warning).
- Not claimed:
  - a root launcher's body or delegation target;
  - member-level privacy inside modules;
  - child-to-parent or sibling package import direction;
  - imports resolved through any base other than a declared root's parent;
  - an `__all__` declared through an annotated assignment or built from an expression (reported as undeclared);
  - names bound only inside top-level `if` or `try` blocks (reported as unbound);
  - an entry's non-re-export imports (reported as leaked public names);
  - language-general import enforcement;
  - broad hardcoded decision-fact scanning;
  - typed config boundary scanning;
  - selector runtime witnesses without separate structured owners;
  - that a README launcher command is run from the governance root.
- Re-verify through README Checks when the coding native-package table, the folder-architecture rule, the source-root markers, or the package layout change.

## Packaged-folder adoption (agent decomposition decisions implementing the 2026-10-03 and 2026-10-04 user decisions in `docs/project/goal/goal.md`)
- `scripts/check_governance_core/` is a regular Python package. The entry re-exports only.
  - The public boundary (request validation, dispatch, failure envelopes) is the private `_api` module.
  - The command line (argument parsing, one `dictConfig` logging setup, rendering) is the private `_cli` adapter.
  - The declared-path contract (`canonical_relative`, which rejects `.`, `resolve_declared_file`, `resolve_declared_directory`) is `_declared_paths`, consumed by the manifest, foundation, folder-architecture, and project-branch validators.
  - `_documents` is the single Markdown owner: `parse_markdown` parses CommonMark fences, operative lines and headings, and `paragraphs` and `blocks` segment those lines. `MarkdownDocument.markers(token)` is the single owner-marker parser (exact `<!-- token value -->` grammar; blockquoted lines are non-operative). `_corpus` resolves the routed governance corpus.
  - The native-package interface witnesses are `_package_interface` behind the folder-architecture check.
  - `_python_modules` parses each Python source once per run and indexes imports and module-level bindings, shared by the folder-architecture, package-interface, repeat-report and safety checks through `DocumentStore.python_module`.
  - Each layout literal (root authority names, `docs`, `docs/agents`, `docs/project`, `SKILL.md`, the manifest path, `__init__.py`) lives in one private module, and consumers import it.
  - The default governance root and the docs-policy owner path are each one private constant reused by test support, so every mode yields the same docs result.
- `scripts/` is a declared source root that only contains packages.
- Directory execution of the package folder is unsupported, because the launcher performs no import-path manipulation; downstream callers use the README Checks commands.
- The folder-architecture check receives both roots from the engine context:
  - The pack record at the governance root must declare at least one root.
  - The host record at the repository root, read only when that root differs, declares the host's own roots and exceptions and may declare none.
  - A host root inside the governance root is rejected.
  - The merged roots share one nesting rejection.
  - Python is scanned under the repository root.
  - A file outside every declared root is reported against the record that owns its location.
- Test modules mirror private-module jurisdictions: `test_docs_policy` (docs-policy declarations, routers and the Markdown repeat report), `test_coding_policy` (the coding declaration and the constant repeat report), `test_docs_timing` (the FP-03 docs witness), `test_inventory` (enumeration plus cached-family revalidation), `test_git_capture` (bounded Git capture lifecycle), `test_folder_architecture` (structure, root markers, interface witnesses), `test_orchestration_contract` (authority route and contract graph), `test_orchestration_delegation` (delegation, plan, and message-intake projections).
- Shared orchestration fixtures live in `_test_support`. It validates the unchanged live repository once per process and reuses the memo only while the constitution and every declared foundation file keep their validated file state. Other files the validation reads, such as the manifest, are outside the key. No test writes the live tree.
- `X-Bookmarks Import/` is the `SSOT-DEC-001` non-owner workspace and the deferred packaged-folder exception declared below.
- Its two regression tests live beside the scripts they load and run through README Checks, so deleting the workspace breaks only its own tests.

## Reserved jurisdictions
- Reserved, not created: `interfaces/printer`, `interfaces/web-api`, `interfaces/database`, `playbooks/naming`.
- A reserved jurisdiction's folder MUST be created at its first use, never in advance; this extends `docs/agents/governance/principles/principles.md` Stable baseline interface.

## Governance source roots
<!-- governance-core-python-root: scripts -->
<!-- governance-core-python-root: X-Bookmarks Import -->
<!-- governance-core-python-package-exception: X-Bookmarks Import -->
- These owner markers declare the Python source roots the folder-architecture check enforces for the repository that owns this record, and the roots exempt from packaged-folder enforcement.
- The check reads this record at the governance root, and a vendored host's own record at the repository root for the host's own roots only (user decisions 2026-10-03 and 2026-10-04 in `docs/project/goal/goal.md`).
- Similarly named paths are not included.

## Outputs
- A vendored governance pack under `.governance/` in downstream repos, with constitutional authority at `.governance/AGENTS.md`, lifecycle authority at `.governance/Orchestration.md`, project docs under `docs/project/`, and supporting governance docs under `.governance/docs/agents/`.
- Repo-owned source assets under `docs/agents/governance/skills/`, `docs/agents/governance/settings/`, and `docs/agents/governance/mcp/`.
