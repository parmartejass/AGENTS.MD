---
doc_type: decision
ssot_owner: docs/agents/governance/ssot/authority-decisions/authority-decisions.md
update_trigger: cross-project SSOT authority decisions change OR migration contracts are added or updated
---

# Authority Decisions

Jurisdiction: cross-repo governance authority decisions and their migration contracts.

- Each decision record MUST make its owner, permitted exceptions, forbidden duplicates, coordinated update set, witness, and review trigger verifiable.
- Reusable governance assets MUST NOT use secret-bearing, generated-data, or machine-local roots as canonical SSOT parents.
- A mixed domain MAY hold a non-owner workspace root only when a record here names its canonical owner, allowed non-owner paths, and forbidden duplicates.

## SSOT-DEC-001 - Reusable X skill authority vs X workspace

- Status: active
- Scope: reusable X API skill guidance as canonical authority; adjacent X research, data, and import workspace content as a separate non-owner zone
- Canonical owner: `docs/agents/governance/skills/x-api-data-access/`
- Allowed non-owner location: `X-Bookmarks Import/` may hold bookmark exports, research notes, import or fetch scripts, and workspace-only experiments
- Allowed non-owner location: workspace-local X skill experiments are not canonical until migrated into `docs/agents/governance/skills/<skill-name>/` and linked through the skill owners and tooling
- Allowed non-owner location: secret-bearing files such as `.x_token.json` MUST remain untracked and MUST NOT define canonical guidance
- Forbidden duplicate: any tracked second `x-api-data-access/SKILL.md` outside `docs/agents/governance/skills/x-api-data-access/`
- Forbidden duplicate: docs or tooling pointing at `X-Bookmarks Import/` as the canonical reusable skill root
- Coordinated update set: `docs/agents/governance/skills/skills.md`, `docs/agents/agents_index.md`, `README.md`, `agents-manifest.yaml`, `scripts/check_governance_core/`
- Verification witness: the README Checks full governance-core command passes; `docs/agents/agents_index.md` and `README.md` reference `docs/agents/governance/skills/` as the canonical skill root; the X API skill bundle exists under `docs/agents/governance/skills/x-api-data-access/`
- Review trigger: any proposal to move canonical X skill ownership away from `docs/agents/governance/skills/` or to treat `X-Bookmarks Import/` as a tracked governance asset root

## SSOT-DEC-003 - Docs router authority vs canonical narrative leaf docs

- Status: active
- Scope: packaged-folder public entrypoints for runtime code (the language-native package entry) and docs (the folder router), with docs router and public-leaf behavior under `docs/`
- Canonical owner: packaged-folder contract -> `AGENTS.md` Jurisdictional Decomposition; docs mechanics, code mechanics, and validation -> the owners routed by `docs/agents/governance/ssot/ssot.md`
- Allowed non-owner location: router-linked public leaf docs inside the same docs folder
- Allowed non-owner location: router-only artifact-first docs folders cataloging only payload children such as JSON, TOML, generated outputs, or dated evidence subfolders
- Allowed non-owner location: runtime identity contracts such as `SKILL.md` and `mcp.json`, owned by their existing authorities
- Forbidden duplicate: reintroducing `index.md` as the universal docs router contract
- Forbidden duplicate: `scripts/migrated_router_leaves.json` or any replacement leaf-name registry
- Coordinated update set: the constitution, the docs and coding owners, the project architecture record, `agents-manifest.yaml`, `README.md`, the governance-core package with its regression tests, and its public-API consumers
- Verification witness: the README Checks full governance-core command and core regression tests pass, including negative docs-router, repository-structure, and Python-safety cases
- Review trigger: any proposal to change a docs router or public-leaf filename pattern, or Python packaged-folder enforcement, without updating the governance-core public contract, its regression fixtures, and the coding Python table
- Review trigger: any user decision revisiting the `<authority>_index.md` docs-router name, the custom entry-file exception retained by the 2026-10-03 user decision in this repository's `docs/project/goal/goal.md`
- Review trigger: any proposal to rename or repurpose `SKILL.md` or `mcp.json` under this contract family

## SSOT-DEC-004 - Project truth authority, closure records, and non-owner evidence

- Status: active
- Scope: project-doc truth ownership, tracked Changelog closure-record ownership, evidence boundaries, and non-owner mirror surfaces
- Canonical owner: authority-boundary decision -> this record
- Canonical owner: admission, maintenance, safe supersession, required project-doc branches -> `docs/agents/governance/documentation/documentation.md`
- Canonical owner: project-local closure records -> `docs/project/changelog/changelog.md`
- Canonical owner: closure-record shape -> `docs/agents/governance/release/release.md`
- Allowed non-owner location: `docs/project/goal/goal.md` and other `docs/project/` owner docs own their declared durable project truth
- Allowed non-owner location: `docs/project/changelog/changelog.md` holds closure-record facts only
- Allowed non-owner location: planning notes, PR and review evidence, git history, task coordination artifacts, and working or closure evidence are evidence only until durable facts are promoted
- Allowed non-owner location: valid Changelog mirror surfaces are final agent reports, PR or release descriptions, and release or checklist outputs, after promotion and after the tracked Changelog is updated or marked `N/A + reason`
- Forbidden duplicate: a separate project-doc truth owner outside the declared owner-doc path
- Forbidden duplicate: using Changelog as owner for behavior, invariants, project intent, architecture, rules, data truth, reusable governance policy, implementation rationale, active work, raw prompts, transcripts, or unpromoted evidence
- Forbidden duplicate: per-change tracked changelog files, `docs/project/learning/changelog.md`, restored `docs/project/change-records/`, change-record schemas, or checker flags
- Forbidden duplicate: treating non-owner working evidence as project truth
- Coordinated update set: the constitution, the documentation and release owners, the project docs, `README.md`, `agents-manifest.yaml`, and the governance-core project-doc validator with its regression tests
- Verification witness: the README Checks project-doc command passes; tracked Changelog records reference owner-promotion targets or `N/A + reason`; retired change-record files, checker flags, and per-change changelog trees remain absent; manual review confirms no duplicate project-truth authority
- Review trigger: any proposal to add a separate project truth owner, move durable project intent out of `goal.md`, weaken owner-doc promotion, or treat non-owner evidence as project truth
- Review trigger: any proposal to add Changelog storage outside the tracked owner and mirror surface set, copy the closure-record shape into non-owner docs, or restore retired change-record contracts
