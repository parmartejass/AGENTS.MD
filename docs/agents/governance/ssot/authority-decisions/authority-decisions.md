---
doc_type: decision
ssot_owner: docs/agents/governance/ssot/authority-decisions/authority-decisions.md
update_trigger: cross-project SSOT authority decisions change OR migration contracts are added or updated
---

# Authority Decisions

Jurisdiction: cross-repo governance authority decisions and their migration contracts.

- Content MUST be limited to decision records and migration contracts.

## Entry contract

Each active decision record MUST include:

```text
- Decision ID:
- Status:
- Scope:
- Canonical owner:
- Allowed non-owner locations:
- Forbidden duplicates:
- Coordinated update set:
- Verification witness:
- Review trigger:
```

## Guardrails

- Reusable governance assets MUST keep canonical SSOT parents outside secret-bearing roots.
- Reusable governance assets MUST keep canonical SSOT parents outside generated-data and machine-local roots.
- A mixed domain MAY hold a non-owner workspace root only when this register records its canonical owner, allowed non-owner paths, and forbidden duplicates. Witness: the recorded decision entry.
- That permission is hierarchical: this register stays the single parent authority, with no parallel authority beside it.
- A canonical-owner change MUST update its coordinated set in one change.
- Docs and tooling MUST migrate together in that one change.

## SSOT-DEC-001 - Reusable X skill authority vs X workspace

- Decision ID: SSOT-DEC-001
- Status: active
- Scope: reusable X API skill guidance as canonical authority, plus adjacent X research, data, and import workspace content as a separate non-owner zone
- Canonical owner: `docs/agents/governance/skills/x-api-data-access/`
- Allowed non-owner location: `X-Bookmarks Import/` may hold bookmark exports, research notes, import or fetch scripts, and workspace-only experiments
- Allowed non-owner location: workspace-local X skill experiments are not canonical until migrated into `docs/agents/governance/skills/<skill-name>/` and linked through the standard skill owners and tooling
- Allowed non-owner location: secret-bearing files such as `.x_token.json`, which MUST stay untracked and carry no canonical guidance
- Forbidden duplicate: a tracked second `x-api-data-access/SKILL.md` outside `docs/agents/governance/skills/x-api-data-access/`
- Forbidden duplicate: docs or tooling that name `X-Bookmarks Import/` as the canonical reusable skill root
- Coordinated update set: `docs/agents/governance/skills/skills.md`
- Coordinated update set: `docs/agents/agents_index.md`
- Coordinated update set: `README.md`
- Coordinated update set: `agents-manifest.yaml`
- Coordinated update set: the governance-core package `scripts/check_governance_core/`
- Verification witness: the README Checks full governance-core command passes
- Verification witness: `docs/agents/agents_index.md` and `README.md` reference `docs/agents/governance/skills/` as the canonical reusable skill root
- Verification witness: the tracked canonical X API skill bundle exists under `docs/agents/governance/skills/x-api-data-access/`
- Review trigger: any proposal to move canonical X skill ownership away from `docs/agents/governance/skills/`
- Review trigger: any proposal to treat `X-Bookmarks Import/` as a tracked governance asset root

## SSOT-DEC-003 - Docs router authority vs canonical narrative leaf docs

- Decision ID: SSOT-DEC-003
- Status: active
- Scope: packaged-folder public entrypoints for runtime code (the language-native package entry) and docs (the folder router), with docs-specific router and public-leaf behavior under `docs/`
- Canonical owner: packaged-folder contract for code and docs -> `AGENTS.md` Jurisdictional Decomposition
- Canonical owner: docs mechanics, code mechanics, and validation facts -> the owners routed by `docs/agents/governance/ssot/ssot.md` Docs modularity and Coding principles
- Allowed non-owner location: router-linked public leaf markdown docs inside the same docs folder authority
- Allowed non-owner location: router-only docs folders that are artifact-first and catalog only payload children such as JSON, TOML, generated outputs, or dated evidence subfolders
- Allowed non-owner location: deeper runtime identity contracts such as `SKILL.md` and `mcp.json`; their existing authorities own them, outside this naming contract
- Forbidden duplicate: reintroducing `index.md` as the universal docs router contract
- Forbidden duplicate: runtime or docs contract filenames hardcoded independently in validators, README guidance, templates, or policy docs
- Forbidden duplicate: competing public contract files inside one folder authority without an explicit contract-family exception
- Coordinated update set: the constitution
- Coordinated update set: the owners routed by `docs/agents/governance/ssot/ssot.md` Docs modularity and Coding principles
- Coordinated update set: the project architecture record
- Coordinated update set: `agents-manifest.yaml`
- Coordinated update set: `README.md`
- Coordinated update set: the governance-core package with its regression tests and its public-API consumers
- Verification witness: the README Checks full governance-core command and core regression tests pass, including negative docs-router, repository-structure, and Python-safety cases
- Review trigger: any proposal to change a docs router or public-leaf filename pattern without updating the governance-core public contract and its regression fixtures
- Review trigger: any proposal to change Python packaged-folder enforcement without updating that public contract and the coding native-package table
- Review trigger: any user decision revisiting the `<authority>_index.md` docs-router name. That name is the custom entry-file exception to the packaged-folder contract, kept by the 2026-10-03 user decision in this governance source repository's `docs/project/goal/goal.md`
- Review trigger: any proposal to reintroduce `index.md` as the universal docs router contract
- Review trigger: any proposal to rename or repurpose `SKILL.md` or `mcp.json` under this contract family

## SSOT-DEC-004 - Project truth authority, closure records, and non-owner evidence

- Decision ID: SSOT-DEC-004
- Status: active
- Scope: project-doc truth ownership, tracked Changelog closure-record ownership, evidence boundaries, and non-owner mirror surfaces
- Canonical owner: authority-boundary decision -> this record
- Canonical owner: constitutional required-doc and owner-maintenance trigger -> `AGENTS.md`
- Canonical owner: baseline declarations, material-knowledge admission, placement, maintenance, safe supersession -> `docs/agents/governance/documentation/documentation.md`
- Canonical owner: project-doc scaffold shape -> `docs/agents/governance/documentation/project-docs-template/project-docs-template.md`
- Canonical owner: project-local tracked closure records -> `docs/project/changelog/changelog.md`
- Canonical owner: Changelog closure-record field template and order -> `docs/agents/governance/release/release.md`
- Canonical owner: supersession history -> `docs/project/changelog/changelog.md`
- Allowed non-owner location: `docs/project/goal/goal.md` (durable project intent)
- Allowed non-owner location: other `docs/project/` owner docs own their declared durable project truth
- Allowed non-owner location: `docs/project/changelog/changelog.md` holds only closure-record facts, in the release jurisdiction's field order, and supersession history
- Allowed non-owner location: local planning notes, PR and review evidence, git history, task coordination artifacts, working evidence, and closure evidence. They stay evidence only until durable facts are promoted or closure facts recorded
- Allowed non-owner location: Changelog mirror surfaces: final agent reports, PR or release descriptions, and release or checklist outputs. They are valid after promotion and after the tracked Changelog is updated or marked `N/A + reason`
- Forbidden duplicate: a separate project-doc truth owner outside the docs SSOT declared owner-doc path, whether required, routed, scaffolded, or recreated
- Forbidden duplicate: Changelog as owner of behavior, invariants, project intent, architecture, rules, data truth, reusable governance policy, implementation rationale, active work, raw prompts, transcripts, or unpromoted evidence; it owns closure records and supersession history
- Forbidden duplicate: non-owner working evidence used as project truth
- Coordinated update set: the constitution
- Coordinated update set: the owners routed by `docs/agents/governance/ssot/ssot.md` Bounded project authority memory
- Coordinated update set: the release owner
- Coordinated update set: `README.md`
- Coordinated update set: `agents-manifest.yaml`
- Coordinated update set: the governance-core project-doc validator with its regression tests
- Verification witness: the README Checks project-doc command passes
- Verification witness: tracked Changelog records reference owner-promotion targets or `N/A + reason`
- Verification witness: manual review confirms active project docs define no duplicate project-truth authority
- Review trigger: any proposal to add a separate project truth owner outside the docs SSOT declared-owner path
- Review trigger: any proposal to move durable project intent out of `goal.md`, weaken owner-doc promotion, or treat non-owner evidence as project-truth authority
- Review trigger: any proposal to add Changelog storage outside the tracked owner and valid mirror surface set, or copy the release-checklist field template into non-owner docs
