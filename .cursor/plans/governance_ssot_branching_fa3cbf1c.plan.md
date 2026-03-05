---
name: governance discoverability and ssot routing
overview: Expand the current docs/agents branching idea into a repo-wide discoverability and SSOT routing refactor so every governed surface is easy to find, every new addition lands under one documented owner, and source/vendored validation stays correct.
todos:
  - id: inventory-governed-surfaces
    content: Build a search-derived inventory of governed surfaces and all consumers of current flat governance paths across docs, scripts, templates, `.cursor/agents`, `.cursor/plans`, and change records.
    status: pending
  - id: split-discoverability-owners
    content: Define one owner per discoverability responsibility across `README.md`, project docs, governance docs, docs policy, platform adapters, and the machine-readable path contract.
    status: pending
  - id: codify-placement-rules
    content: Codify deterministic placement rules, branch creation rules, index eligibility, pointer-stub limits, and historical-artifact treatment so new additions always land in the right SSOT.
    status: pending
  - id: add-layout-contract
    content: Extend `agents-manifest.yaml` with a scoped machine-readable governance layout contract (authority paths, registered branch indexes, scan roots, temporary aliases) without turning it into a second repo-surface owner.
    status: pending
  - id: harden-validators
    content: Refactor manifest/docs/change-record validators to consume the layout contract, enforce resolved-path containment and leaf-only semantics, and support both source-repo and vendored-governance roots.
    status: pending
  - id: document-hidden-surfaces
    content: Document `.cursor/agents` and `.cursor/plans` as source-repo-only governed surfaces with explicit owner docs, lifecycle classification, and reverse traceability to canonical owners.
    status: pending
  - id: move-governance-docs
    content: Move flat governance docs into registered branch folders and update every governed consumer from the inventory in one atomic cutover.
    status: pending
  - id: add-traceability-checks
    content: Add repo-surface completeness, branch ownership, stale-reference, injection-set, and pointer-stub checks so discoverability and SSOT routing cannot silently drift.
    status: pending
  - id: retire-legacy-paths
    content: Remove compatibility aliases only after zero-stale-reference, zero-orphan, and vendored/root verification gates pass; otherwise keep pointer-only stubs with a declared sunset.
    status: pending
isProject: false
---

# Repo-Wide Discoverability + Governance Branching

## Goal + Acceptance Criteria

- Make every first-class repo surface discoverable from a documented entrypoint instead of leaving hidden governance-adjacent artifacts implicit.
- Keep exactly one recorded-truth owner per discoverability responsibility:
  - repo-wide navigation
  - project-doc entrypoint
  - authority graph / tooling surface map
  - governance-doc navigation
  - placement / folder / index rules
  - machine-readable governance path registry
- Ensure every new governance doc or source-repo-only tooling artifact lands under a deterministic owner and does not create a shadow SSOT.
- Preserve source-repo usage, vendored `.governance/` usage, context injection, and validation during and after the migration.
- Make legacy paths and historical artifacts traceable without letting compatibility stubs become second authorities.

## Non-Goals

- Do not make `.cursor/**` the policy SSOT; those files stay adapters/plans that must trace back to canonical owners.
- Do not broaden manifest injection with blanket repo-wide recursive scans.
- Do not create speculative sub-branches before an authority boundary and growth pressure are both verified.
- Do not rewrite historical change records or archived plans by default just to chase moved paths.

## Model

- Inputs:
  - governance docs under `docs/agents/`
  - project docs under `docs/project/`
  - machine-readable routing in `agents-manifest.yaml`
  - validation scripts under `scripts/`
  - source-repo-only Cursor artifacts under `.cursor/agents/` and `.cursor/plans/`
  - vendored governance usage under `.governance/`
- Outputs:
  - one repo-wide discoverability map
  - one authority graph and tooling-surface map
  - one deterministic placement/index policy
  - one machine-readable governance layout contract
  - validators that prove discoverability, traceability, and safe path resolution
- Side effects:
  - doc moves
  - reference rewrites
  - validator changes
  - optional compatibility stubs / alias map during migration
- Boundaries:
  - `GovernanceRoot` owns governance docs, manifest, and scripts.
  - `RepoRoot` owns project docs and any source-repo-only tooling surfaces.
  - `.cursor/**` artifacts are never policy SSOT; they must trace back to canonical owners elsewhere.

## Verified Baseline

- `agents-manifest.yaml` still uses shallow governance globs such as `docs/agents/*.md`, `docs/agents/playbooks/*.md`, and `docs/agents/skills/*.md`.
- `docs/agents/00-principles.md` and `docs/agents/skills/00-skill-standards.md` still describe flat `docs/agents/*.md` ownership.
- `README.md` and `docs/project/architecture.md` do not currently document `.cursor/agents/` or `.cursor/plans/`, so repo-wide discoverability is incomplete.
- `scripts/check_docs_ssot.ps1` and `scripts/check_governance_core.py` hardcode `docs/agents/25-docs-ssot-policy.md` and exempt only `index.md` plus one-level `*/index.md`.
- `scripts/check_agents_manifest.ps1` currently proves only quoted path syntax + existence; it does not enforce leaf-only semantics, resolved containment, wildcard bans, or vendored-prefixed path bans.
- `scripts/check_docs_ssot.ps1` and `scripts/check_governance_core.py` walk `RepoRoot/docs/**`, so a downstream repo can validate `docs/project/**` while missing problems in `.governance/docs/agents/**`.
- `.cursor/agents/*.md` and `.cursor/plans/*.plan.md` already contain governance references to `AGENTS.md`, `agents-manifest.yaml`, and `docs/agents/**`, but no current repo doc claims those surfaces as discoverability owners.

## SSOT Map

- `AGENTS.md`: canonical policy and hard gates.
- `README.md`: repo-wide surface discoverability and top-level navigation only.
- `docs/project/index.md`: project-docs entrypoint only.
- `docs/project/architecture.md`: authority graph, tooling-surface map, and source-repo-only vs vendored classification.
- `docs/agents/index.md`: governance-doc navigation only.
- `docs/agents/25-docs-ssot-policy.md`: placement rubric, folder/index eligibility, pointer-stub contract, and doc-header/index rules.
- `docs/agents/skills/10-platform-adapters.md`: platform-specific adapter surface documentation, including `.cursor/agents/`.
- `agents-manifest.yaml`: machine-readable governance-doc routing and layout contract rooted at `GovernanceRoot`; it must not become the repo-wide surface map.
- `.cursor/plans/*.plan.md`: non-authoritative planning artifacts whose lifecycle/classification is recorded in `docs/project/architecture.md`.

## Repo-Wide Discoverability Contract

- `README.md` must expose every first-class repo surface, including source-repo-only hidden surfaces that materially affect governance work.
- `docs/project/index.md` must stay the project-docs entrypoint and point readers to `docs/project/architecture.md` for tooling-surface ownership.
- `docs/project/architecture.md` must classify each governed surface as `authoritative`, `supporting`, `adapter`, `planning-only`, `generated`, or `historical evidence`.
- `docs/agents/index.md` is the governance-doc hub only; it is not the repo-wide discoverability owner.
- Each non-index governance doc must have exactly one owning branch index; other indexes may cross-link it but must not co-own it.
- Hidden source-repo-only surfaces must have reverse traceability to canonical owners, not standalone policy language.

## Governance-Doc Branching Target

Use a small number of stable branch folders now, but make the hierarchy explicitly branchable so each area can grow into subfolders later without changing the discoverability model.

Base governance branch map:

- `docs/agents/index.md`
- `docs/agents/foundations/index.md`
  - `00-principles.md`
  - `05-context-retrieval.md`
  - `10-repo-discovery.md`
  - `15-stuck-in-loop-generate-fresh-restart-prompt.md`
- `docs/agents/ssot/index.md`
  - `20-sources-of-truth-map.md`
  - `25-docs-ssot-policy.md`
  - `35-authority-bounded-modules.md`
  - `40-config-constants.md`
- `docs/agents/runtime-safety/index.md`
  - `30-logging-errors.md`
  - `50-excel-com-lifecycle.md`
  - `60-gui-threading.md`
  - `70-io-data-integrity.md`
  - `80-testing-real-files.md`
- `docs/agents/workflows/index.md`
  - `85-dual-entry-template.md`
  - `workflow-registry.md`
  - `90-release-checklist.md`
- Existing roots also become registered branch indexes:
  - `docs/agents/playbooks/index.md`
  - `docs/agents/skills/index.md`
  - `docs/agents/automation/index.md`
  - `docs/agents/schemas/index.md`

Illustrative future scale path:

- `docs/agents/playbooks/debug/index.md`
- `docs/agents/playbooks/runtime-safety/index.md`
- `docs/agents/playbooks/governance/index.md`

Do not create all sub-branches up front. Create them only when the placement rubric below says they are warranted.

## Placement Rules

### Placement Algorithm

1. Identify the artifact's primary authority family.
2. If it is a governance doc, place it in the deepest registered branch whose `index.md` already claims that authority family.
3. If it is cross-cutting, place it under the branch that owns the primary invariant and cross-link it from other relevant indexes instead of duplicating it.
4. If it is a repo-surface discoverability concern, update the owning entrypoint doc instead of encoding the same map in multiple places.
5. If no existing owner fits cleanly, create a new owner or branch only when a distinct authority boundary and long-term growth pressure are both verified.

### Default Routing

- Canonical governance concepts and invariants -> closest authority branch under `docs/agents/<branch>/`
- Reusable task templates/checklists -> `docs/agents/playbooks/...`
- Platform adapters -> `docs/agents/skills/...`
- Automation loop runbooks -> `docs/agents/automation/...`
- Schemas/contracts/artifact definitions -> `docs/agents/schemas/...`
- Cursor prompt definitions -> `.cursor/agents/...` with ownership documented by `docs/agents/skills/10-platform-adapters.md`
- Planning artifacts -> `.cursor/plans/...` with ownership/lifecycle documented by `docs/project/architecture.md`

### New Folder / Index Rules

Create a new folder or subfolder only when at least one applies:

- the docs share a distinct authority family or invariant set that would otherwise make an existing folder ambiguous
- the area has a different change cadence from its parent branch
- the area needs its own placement guidance or sub-navigation to stay searchable
- two or more docs already exist, or one exists and near-term growth is clearly planned and specific

Do not create a new folder when:

- the artifact is a one-off and fits an existing branch cleanly
- the reason is only aesthetics or speculative flexibility
- the new folder would become a second authority for an existing concept

Branch/index rules:

- every registered branch must be linked from its parent `index.md`
- every non-index governance doc must be reachable from `docs/agents/index.md` through a continuous registered index chain
- only registered branch indexes are navigation-only and eligible for header exemption; an arbitrary nested `index.md` is still a normal doc

### Pointer Stub / History Rules

- Compatibility stubs, if needed, must be pointer-only: title, relocation note, canonical target, and sunset marker only.
- Any normative prose in a compatibility stub is a validation failure.
- Historical change records and archived plan artifacts remain immutable evidence unless an explicit migration step says otherwise.
- History-aware checks must either grandfather old path references through a temporary alias map or classify those files outside the active-path gate; do not silently mix the two models.

## Machine-Readable Path Contract

Extend `agents-manifest.yaml` with a scoped governance layout section, for example:

- `authority_paths`: canonical governance authority file mapping
- `branch_indexes`: registered branch index paths plus owned prefixes
- `scan_roots`: allowlisted inventory roots for governance docs vs project docs vs explicit source-repo-only surfaces
- `legacy_aliases`: temporary old-path -> canonical-path mapping with sunset metadata

Contract rules:

- `agents-manifest.yaml` may own machine-readable governance-doc routing and path metadata, but repo-wide surface ownership stays in `README.md` and `docs/project/architecture.md`.
- `default_inject`, `fallback_inject`, `profiles.*.inject`, and `authority_paths` must use governance-root-relative POSIX-style leaf file paths only.
- Reject `.` / `..`, leading slash/backslash, drive-letter paths, UNC paths, `.governance/`-prefixed values, wildcards, and non-leaf canonical targets.
- Path containment must be checked after canonical resolution, not just via string matching.
- Broad recursive inventory scans are acceptable for completeness checks, but profile `detect.file_globs` should stay branch-scoped and minimal.
- PowerShell and Python validators may have separate implementations, but they must share the same normalization and containment contract.

## Migration Phases

1. Inventory and classify every governed surface.
  - Search the repo for all references to current flat governance paths.
  - Classify each hit as `authority`, `governed consumer`, `historical artifact`, or `explicitly out of scope`.
  - Freeze that inventory before changing any paths.
2. Lock the owner split and discoverability contracts.
  - Update `README.md`, `docs/project/index.md`, `docs/project/architecture.md`, `docs/agents/index.md`, `docs/agents/25-docs-ssot-policy.md`, and `docs/agents/skills/10-platform-adapters.md`.
  - Document `.cursor/agents/` and `.cursor/plans/` as source-repo-only surfaces with explicit owner/lifecycle rules.
3. Add the machine-readable layout contract before moving docs.
  - Add `authority_paths`, `branch_indexes`, scan-scope rules, and temporary alias support to `agents-manifest.yaml`.
  - Do not change live doc locations yet.
4. Harden validators before path moves.
  - Refactor `scripts/check_agents_manifest.ps1`, `scripts/check_docs_ssot.ps1`, `scripts/check_governance_core.py`, and `scripts/check_change_records.ps1` to consume the contract.
  - Validate source-repo mode and vendored `.governance/` mode separately.
  - Add failure fixtures for path escapes, bad branch indexes, stale references, and hidden-surface orphaning before any cutover.
5. Move docs and update references atomically.
  - Move core docs into the new branch folders.
  - Create the registered branch indexes and wire the top-down governance navigation chain.
  - Update every governed consumer from the search-derived inventory, including docs, scripts, adapter prompts, and any still-live plan artifacts that are intended to remain active.
6. Add permanent discoverability and traceability guards.
  - Add governance graph completeness, branch ownership, local index presence, repo-surface completeness, hidden-surface reverse traceability, pointer-stub shape, injection-set, and zero-stale-reference checks.
7. Remove compatibility paths only after all gates pass.
  - Remove legacy paths only after zero stale references, zero orphan surfaces, source-root + vendored-root validation, and stub-contract checks pass.
  - If compatibility is still required, keep pointer-only stubs with an explicit sunset instead of open-ended dual ownership.

## Checks To Add

- Governance graph completeness: every non-index governance doc is reachable from `docs/agents/index.md` through registered branch indexes.
- Branch ownership: every non-index governance doc has exactly one owning branch index.
- Branch-index presence: every registered branch folder has a local `index.md`.
- Repo-surface completeness: every first-class repo surface is exposed by `README.md` or explicitly classified in `docs/project/architecture.md`.
- Hidden-surface reverse traceability: `.cursor/agents/**` and live `.cursor/plans/**` point back to canonical owners and do not self-define policy.
- Vendored governance docs coverage: downstream `.governance/docs/agents/**` is validated against the same rules as source-repo governance docs.
- Stale-reference scan: governed Markdown/YAML/JSON/PowerShell/Python/`.cursor/**` files fail if they still point at retired flat paths.
- Injection-set checks: representative manifest profiles prove they inject the intended files and do not silently over-inject branch indexes or unrelated docs.
- Pointer-stub checks: compatibility stubs fail if they contain normative prose or survive past their declared sunset.

## Invariants And Witnesses

### Data invariants

- `INV-D1`: each governance authority resolves to exactly one canonical file in the machine-readable layout contract.
  - Witness: authority-path uniqueness + existence check passes in both validator stacks.
- `INV-D2`: each first-class hidden source-repo surface has one owner and one lifecycle classification.
  - Witness: `docs/project/architecture.md` surface-map check passes for `.cursor/agents` and `.cursor/plans`.
- `INV-D3`: adapter prompts and live planning artifacts remain traceable to canonical owners instead of self-defining governance policy.
  - Witness: reverse-traceability scan passes for `.cursor/agents/**` and `.cursor/plans/**`.

### Ordering invariants

- `INV-O1`: owner split and path contract land before doc moves or broad recursive routing changes.
  - Witness: pre-move validator suite passes while docs are still at old paths.
- `INV-O2`: legacy flat paths are not removed until all governed consumers are updated or explicitly covered by alias/stub policy.
  - Witness: zero-stale-reference gate passes before removal.

### Lifecycle invariants

- `INV-L1`: compatibility stubs remain pointer-only and expire on an explicit sunset.
  - Witness: stub-shape + sunset check passes.
- `INV-L2`: historical change records and archived plan artifacts stay traceable without being forced into current-path conformance.
  - Witness: history-policy check passes, or temporary aliases remain in force until history is explicitly migrated.

### Observability invariants

- `INV-OBS1`: every non-index governance doc is discoverable from `docs/agents/index.md` through a registered branch-index chain.
  - Witness: governance graph completeness check passes.
- `INV-OBS2`: every first-class repo surface is discoverable from `README.md` or `docs/project/index.md`.
  - Witness: repo-surface completeness check passes.
- `INV-OBS3`: each non-index governance doc has exactly one owning branch index.
  - Witness: branch ownership check passes.

### Security / path invariants

- `INV-S1`: every manifest/layout path is normalized under `GovernanceRoot` and resolves to an allowed file.
  - Witness: negative fixtures fail for directory-valued paths, `..`, absolute paths, UNC/drive-relative paths, `.governance/`-prefixed values, wildcards, and resolved-path escapes.

## Council Summary

- `council_run_id`: `2026-03-06-governance-discoverability-prechange`
- `phase`: `pre_change`
- `intent_coverage`: `ssot_duplication`, `silent_error`, `edge_case`, `resource_security_perf`
- `reviewers`:
  - `ssot-reviewer`: reviewed owner splits, consumer inventory, stub retirement, and authority conflicts
  - `docs-reviewer`: reviewed repo-wide navigation, hidden surfaces, and documentation entrypoints
  - `edge-case-scanner`: reviewed vendored mode, historical artifacts, branch ownership, and silent failure modes
  - `security-perf-auditor`: reviewed path safety, scan scope, recursive glob precision, and validator rollout order
- `findings`:
  - High: the prior plan was too narrow because it solved `docs/agents/` branching but not repo-wide discoverability for `.cursor/agents/`, `.cursor/plans/`, `README.md`, and `docs/project/*`
  - High: the prior plan let `docs/agents/index.md`, `docs/project/architecture.md`, and docs-policy concerns drift toward co-owning the same branch-map responsibilities
  - High: validator hardening must cover vendored `GovernanceRoot`, registered branch indexes, and resolved-path containment before any move
  - Medium: hidden source-repo-only surfaces need explicit owner docs and non-authoritative classification
  - Medium: compatibility stubs and historical artifacts need a declared policy so traceability checks do not create silent drift or false failures
- `conflicts`: no blocking conflicts; one design tension was resolved by limiting `agents-manifest.yaml` to machine-readable governance-doc routing while `README.md` and `docs/project/architecture.md` stay the human repo-surface owners
- `reconciliation_decision`: replace the docs-only branching refactor with this repo-wide discoverability + governance-branching phased plan; direct cutover remains blocked
- `residual_risks`: validator churn across PowerShell/Python, stale references in archived artifacts, over-broad recursive globs, and hidden source-repo-only surfaces remaining undocumented
- `go_no_go`: `go` for the phased contract-first plan above; `hold` for moving docs before inventory + validator hardening
- `verification_links`:
  - `README.md`
  - `scripts/check_agents_manifest.ps1`
  - `scripts/check_docs_ssot.ps1`
  - `scripts/check_project_docs.ps1`
  - `scripts/check_change_records.ps1`
  - `scripts/check_governance_core.py`

## Verification

Implementation-phase checks stay anchored to the repo SSOT in `README.md`:

- `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/check_agents_manifest.ps1`
- `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/check_docs_ssot.ps1`
- `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/check_project_docs.ps1`
- `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/check_change_records.ps1`
- `python3 scripts/check_governance_core.py`

Manual validation already performed for this plan update:

- verified shallow manifest globs and flat-layout wording in `agents-manifest.yaml`, `docs/agents/00-principles.md`, and `docs/agents/skills/00-skill-standards.md`
- verified `README.md` and `docs/project/architecture.md` do not currently document `.cursor/agents/` or `.cursor/plans/`
- verified `.cursor/agents/*.md` and `.cursor/plans/*.plan.md` already reference canonical governance files but lack a documented discoverability owner
- merged pre-change council findings into the rewritten plan above

Failure-path fixtures to add during implementation:

- invalid inject path
- directory-valued inject path
- wildcard inject path
- absolute path
- UNC / drive-relative path
- `.governance/`-prefixed manifest value
- resolved-path escape after normalization
- missing registered branch `index.md`
- nested `index.md` that is not registered as a branch index
- stale flat-path reference in a governed file
- vendored `.governance/docs/agents/**` doc missing required header
- hidden surface present but unclassified / unowned in repo discoverability docs
