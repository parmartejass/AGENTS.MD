---
doc_type: reference
ssot_owner: docs/project/architecture/architecture.md
update_trigger: repo layout, authority-routing profiles, or validation scripts change
---

# Architecture

## Boundary
- This root doc owns project architecture pointers, responsibility splits, authority graph summaries, and structural relationships.
- It does not own durable project goal, reusable governance policy, data-truth records, tracked closure records, operational learnings, source asset payloads, or work-status records.

## When to create a branch-local owner subdoc
- Create an architecture subdoc when a stable structural truth cluster needs its own intent, boundary, invariant, change rule, and verification.
- Use a subdoc for protected behavior only when concrete observable behavior is user-protected, regression-sensitive, or replaceable only under an equivalence rule.

## Current Summary
- The repo is a governance-pack source with reusable policy/docs and source assets under `docs/agents/`, project-local authority docs under `docs/project/`, and validation scripts under `scripts/`.
- No branch-local architecture subdocs are currently declared.

## Branch-local owner subdocs
- None currently declared.

## Entrypoints
- Governance constitution: `AGENTS.md`
- Agent lifecycle and workflow: `Orchestration.md`
- Governance Agent authority-routing manifest: `agents-manifest.yaml`
- Docs branch entrypoint: `docs/docs_index.md`
- Supporting governance docs: `docs/agents/agents_index.md`
- Validation scripts: `scripts/`

## SSOT pointers (concept -> owner)
- Fundamental Principles, constitutional rules, and conflict precedence: `AGENTS.md`
- Agent lifecycle and role boundaries: `Orchestration.md`
- Governance Agent governance-authority routing: `agents-manifest.yaml`
- Docs placement, headers, and durable-record mechanics: `docs/agents/25-docs-ssot-policy/docs-ssot-policy.md`
- Project truth authority, tracked closure records, and non-owner evidence surfaces: `SSOT-DEC-004` in `docs/agents/22-ssot-authority-decisions/ssot-authority-decisions.md`
- Changelog closure records: `docs/project/changelog/changelog.md` owns tracked closure-record facts; `SSOT-DEC-004` owns valid/invalid closure-record surfaces; `docs/agents/90-release-checklist/release-checklist.md` owns field template/order.
- Durable project intent, objective, acceptance criteria, non-goals, and verification intent: `docs/project/goal/goal.md`
- Protected behavior records: branch-local architecture subdoc when concrete observable protected behavior exists.
- Project data-truth records: `docs/project/data-truth/data-truth.md`
- Durable operational learnings: `docs/project/learning/learning.md`
- Governance-core validation, including docs router/public-leaf behavior: `scripts/check_governance_core/check_governance_core_main.py` public API
- Python script public entrypoint enforcement: `scripts/check_governance_core/check_governance_core_main.py` public contract
- Governance-core check IDs/order/reconciliation: private engine behind `scripts/check_governance_core/check_governance_core_main.py`; consumers use only the public API.
- Repo-owned reusable assets: `docs/agents/skills/`, `docs/agents/settings/`, `docs/agents/mcp/`
- Runtime config and local-secret boundary: `docs/agents/settings/00-settings-standards/settings-standards.md`

## Authority graph (owners -> dependents)
- `AGENTS.md` Fundamental Principles and hard gates -> sole canonical text, precedence, owner-local identifiers, coding hard-gate trigger, docs-modularity trigger, and structural declaration consumed by lower owners, loaders, prompts, and checks. Lower declared owners retain binding rules and contracts within their own jurisdictions; the constitutional conflict boundary does not demote them. The existing governance-core governance check derives block/heading/paragraph shape from that declaration; shared test support reads the live owner section. Neither Python nor project docs copy the principle text or its expected hash. Exact source equality and semantic compliance require separate evidence under FP-33.
- `Orchestration.md` -> sole detailed lifecycle authority consumed by loaders, prompts, support docs, agents, and orchestration checks; its owner-declared delegation and plan projections are structurally validated behind the governance-core public API. Live context isolation, report integration, and YAML instance semantics require agent evidence and independent review, not a structural-checker claim.
- `agents-manifest.yaml` -> Governance Agent governance-only profile and fallback authority routing; it never selects repository or project task sources.
- `docs/agents/25-docs-ssot-policy/docs-ssot-policy.md` -> sole operative documentation-line-limit and required-project-branch declarations consumed by the existing governance-core docs/project-doc handlers; shared document parsing preserves physical LF evidence and derives filenames through the established contract. The docs handler reads every Markdown member of the bounded repository inventory; header/router scope remains `docs/`. Missing/ambiguous/unsafe declarations and aliased or undecodable files fail explicitly. Incidental AGENTS paths do not define the required set.
- `docs/agents/25-docs-ssot-policy/docs-ssot-policy.md` -> bounded project authority-memory policy/detail; project-doc leaves own the routed records declared by that policy
- `docs/agents/35-coding-principles/coding-principles.md` -> single delegated coding-principles and runtime-code authority-design mechanics jurisdiction under the `AGENTS.md` coding hard-gate trigger. Its `code_decomposition_review_lines` declaration supplies the full-mode Python size warning through the declared coding foundation role, replacing the checker-owned copy. Shared positive-integer document parsing serves both coding and documentation declarations; their counting, severity, and scope remain distinct. Missing or invalid coding declarations fail explicitly without a fallback value.
- `scripts/check_governance_core/check_governance_core_main.py` -> single public plain-data API and CLI; its public-contract tests cover docs routing, repository structure, and Python safety without external private imports.
- `scripts/check_governance_core/check_governance_core_main.py` -> sole public governance-core boundary; one private registry/engine composes cached document parsing, strict manifest parsing, docs/project checks, governance checks, bounded repository inventory, repository hygiene/structure, and Python safety. Private module names are not consumer contracts.
- Root authority order plus `docs/agents/agents_index.md` router topology -> complete ordered governance research corpus exposed by `resolve_documents`: `AGENTS.md`, `Orchestration.md`, then routed governance leaves. `agents-manifest.yaml` remains Governance Agent routing data and does not define corpus membership.
- `docs/agents/skills/` -> reusable skill bundles
- `docs/agents/settings/` -> shared settings examples and local-secret boundary
- `docs/agents/mcp/` -> canonical non-secret MCP payloads
- `docs/agents/22-ssot-authority-decisions/ssot-authority-decisions.md` `SSOT-DEC-004` -> project-local docs route durable facts into declared `docs/project/` owner docs; `docs/project/changelog/changelog.md` owns tracked closure-record facts after owner promotion; working evidence and mirror closure evidence remain non-owner evidence unless promoted into the declared owner.
- `docs/agents/22-ssot-authority-decisions/ssot-authority-decisions.md` -> allows `X-Bookmarks Import/` as a non-owner workspace exception without making it a canonical governance root
- `X-Bookmarks Import/skills/governance-autoresearch/scripts/governance_research.py` -> research input collection only; its workspace skill routes governance changes to `AGENTS.md` and `Orchestration.md`. The X scripts own local CLI/default/scoring behavior; current external API facts resolve through the canonical X API skill and X's active contract.

- `docs/agents/00-principles/principles.md` -> delegated constitutional application mechanics; nested evidence and diagnosis owners preserve their relocated obligations behind `principles_index.md`. Exact Fundamental Principles remain exclusively in `AGENTS.md`.

- The inventory owner behind the public checker derives file identity/type/size from authoritative path metadata, revalidates cached family candidates before reads, and rejects changed identities, aliases, non-regular files, noncanonical resolution, and metadata failures. Docs validation consumes that owner directly; it does not maintain a second per-file safety loop. Keyed parent-child lookup removes repeated docs-tree scans.
- The docs-policy timing witness applies `AGENTS.md` FP-03's decision deadline to policy resolution, cached document lookup, and physical-line decisions on already-read text. Complete docs handlers, fresh filesystem inventories, and corpus loading retain measured observations; handler validation and inventory equivalence remain required. Operation-boundary regressions preserve this distinction. Re-verify through README Checks when the timing witness or its owner changes.

## Foundation ownership and validation
- The 2026-09-13 keep-locations decision is recorded in `docs/project/goal/goal.md`. `AGENTS.md` Mandatory Foundations is the sole versioned membership declaration; `Orchestration.md` consumes it for parent reads, application evidence, missing-source outcomes, and context transitions. This keeps constitutional choice separate from lifecycle mechanics without moving or copying owners.
- Loaders, shared compaction instructions, foundation routers, and `agents-manifest.yaml` route to those owners. The manifest selects additional authorities only; the obsolete foundation-only coding profile and conditional foundation entries are removed. Applicable deeper owners retain their duties and owner-declared optionality.
- The existing governance-core boundary parses the declaration once per full run, retains validated role/path pairs once, derives the ordered authority view for existing consumers, and passes the coding-role path to folder validation. Canonical file identity and strict reads remain inventory/document responsibilities; malformed, missing, unsafe, aliased, or unreadable foundations fail explicitly without fallback membership. Private implementation files remain behind the unchanged public API.
- Foundation fixture support consumes public `run_checks` governance success before extracting literal owner markers as mutation data; it neither validates membership itself nor imports the private foundation parser. The 2026-09-13 correction removes that caller dependency. A temporary-copy witness renames the private parser and its internal call: public validation stays valid, fixture imports fail before correction, and fixture setup passes afterward. Regression coverage also proves rejected public validation prevents owner-data extraction.
- `resolve_documents` remains the independent router-owned research corpus with its existing root prefix and DFS contract; mandatory startup loading is not a new corpus selector. Narrow docs/project-doc modes retain their own required authorities and do not acquire unrelated foundation/profile blockers.
- Verification resolves through README Checks and focused public-API foundation scenarios. Structural passes prove declaration and routing behavior, not live application, source-isolated reasoning, future platform autoloading, or uninstrumented timing. Re-verify on foundation/lifecycle, checker, routing, or public-contract changes.

## Current Modularity Witness Boundary
- Enforced now: checker owners validate the declared docs, folder, manifest, and code-change witness contract facts above.
- Not claimed: language-general import enforcement, broad hardcoded decision-fact scanning, typed config boundary scanning, or selector runtime witnesses without separate structured owners.

## Governance source roots
<!-- governance-core-python-root: scripts -->
<!-- governance-core-python-root: X-Bookmarks Import -->
- These owner markers declare the Python source roots enforced for this governance-pack checkout.
- `X-Bookmarks Import/` remains the non-owner workspace exception governed by `SSOT-DEC-001`; similarly named paths are not included.

## Retired Checker Contracts
- Retired change-record checker surfaces are governed by `SSOT-DEC-004`.
- Replacement verification path: route durable facts through the owning project docs and run the README "Checks" project-doc, docs-router, and governance-core commands.
- Downstream callers must use the current README "Checks" command list.

## Outputs
- A vendored governance pack under `.governance/` in downstream repos, with constitutional authority at `.governance/AGENTS.md`, lifecycle authority at `.governance/Orchestration.md`, project docs under `docs/project/`, and supporting governance docs under `.governance/docs/agents/`.
- Repo-owned source assets under `docs/agents/skills/`, `docs/agents/settings/`, and `docs/agents/mcp/`; runtime installation is consumer-owned and not a tracked repo output.
