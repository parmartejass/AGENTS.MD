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

- Reusable governance assets MUST NOT use secret-bearing roots as canonical SSOT parents.
- Reusable governance assets MUST NOT use generated-data or machine-local roots as canonical SSOT parents.
- A mixed domain MAY hold a non-owner workspace root only when this register records its canonical owner, allowed non-owner paths, and forbidden duplicates; witness: the recorded decision entry.
- That permission is hierarchical authority; parallel authority is Prohibited.
- A canonical-owner change MUST update its coordinated set in one change.
- Prohibited: migrating docs first and tooling later.

## SSOT-DEC-001 - Reusable X skill authority vs X workspace

- Decision ID: SSOT-DEC-001
- Status: active
- Scope: reusable X API skill guidance as canonical authority, plus adjacent X research, data, and import workspace content as a separate non-owner zone
- Canonical owner: `docs/agents/governance/skills/x-api-data-access/`
- Allowed non-owner location: `X-Bookmarks Import/` may hold bookmark exports, research notes, import or fetch scripts, and workspace-only experiments
- Allowed non-owner location: workspace-local X skill experiments are not canonical until migrated into `docs/agents/governance/skills/<skill-name>/` and linked through the standard skill owners and tooling
- Allowed non-owner location: secret-bearing files such as `.x_token.json` MUST remain untracked and MUST NOT define canonical guidance
- Forbidden duplicate: any tracked second `x-api-data-access/SKILL.md` outside `docs/agents/governance/skills/x-api-data-access/`
- Forbidden duplicate: docs or tooling pointing at `X-Bookmarks Import/` as the canonical reusable skill root
- Coordinated update set: `docs/agents/governance/skills/skills.md`
- Coordinated update set: `docs/agents/agents_index.md`
- Coordinated update set: `README.md`
- Coordinated update set: `agents-manifest.yaml`
- Coordinated update set: `scripts/check_governance_core/check_governance_core_main.py`
- Verification witness: `python3 scripts/check_governance_core/check_governance_core_main.py` passes
- Verification witness: `docs/agents/agents_index.md` and `README.md` reference `docs/agents/governance/skills/` as the canonical reusable skill root
- Verification witness: the tracked canonical X API skill bundle exists under `docs/agents/governance/skills/x-api-data-access/`
- Review trigger: any proposal to move canonical X skill ownership away from `docs/agents/governance/skills/`
- Review trigger: any proposal to treat `X-Bookmarks Import/` as a tracked governance asset root

## SSOT-DEC-003 - Docs router authority vs canonical narrative leaf docs

- Decision ID: SSOT-DEC-003
- Status: active
- Scope: folder-owned public contract naming for runtime code and docs, with docs-specific router and public-leaf behavior under `docs/`
- Canonical owner: code and docs modularity hard gate -> `AGENTS.md`
- Canonical owner: docs-family behavior policy -> `docs/agents/governance/documentation/documentation.md`
- Canonical owner: coding-principles and runtime-code family mechanics -> `docs/agents/governance/coding/coding.md`
- Canonical owner: docs router and public-leaf validation facts -> `scripts/check_governance_core/check_governance_core_main.py`
- Canonical owner: Python script entrypoint filename enforcement -> `scripts/check_governance_core/check_governance_core_main.py`
- Allowed non-owner location: router-linked public leaf markdown docs inside the same docs folder authority
- Allowed non-owner location: router-only docs folders that are artifact-first and catalog only payload children such as JSON, TOML, generated outputs, or dated evidence subfolders
- Allowed non-owner location: deeper runtime identity contracts such as `SKILL.md` and `mcp.json`, owned by their existing authorities and out of scope for this naming contract
- Forbidden duplicate: reintroducing `index.md` as the universal docs router contract
- Forbidden duplicate: keeping `scripts/migrated_router_leaves.json` or any replacement leaf-name registry once filename derivation is handled by the governance-core public contract
- Forbidden duplicate: hardcoding runtime or docs contract filenames independently in validators, README guidance, templates, or policy docs
- Forbidden duplicate: competing public contract files inside one folder authority without an explicit contract-family exception
- Coordinated update set: `AGENTS.md`
- Coordinated update set: `docs/agents/governance/documentation/documentation.md`
- Coordinated update set: `docs/agents/governance/coding/coding.md`
- Coordinated update set: `docs/agents/governance/documentation/project-docs-template/project-docs-template.md`
- Coordinated update set: `docs/agents/governance/coding/workflow-registry/workflow-registry.md`
- Coordinated update set: `docs/project/architecture/architecture.md`
- Coordinated update set: `agents-manifest.yaml`
- Coordinated update set: `README.md`
- Coordinated update set: `scripts/check_governance_core/check_governance_core_main.py`
- Coordinated update set: public-contract regression tests under `scripts/check_governance_core/`
- Verification witness: `python3 -m unittest discover -s scripts/check_governance_core -p "test*.py" -v` passes, including negative docs-router, repository-structure, and Python-safety cases
- Verification witness: `python3 scripts/check_governance_core/check_governance_core_main.py` passes
- Review trigger: any proposal to change a docs router or public-leaf filename pattern without updating the governance-core public contract and its regression fixtures
- Review trigger: any proposal to change Python script entrypoint filename enforcement without updating that public contract
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
- Allowed non-owner location: `docs/project/goal/goal.md` owns durable project intent, objective, acceptance criteria, non-goals, verification intent
- Allowed non-owner location: other `docs/project/` owner docs own their declared durable project truth
- Allowed non-owner location: `docs/project/changelog/changelog.md` holds closure-record facts only, in the release jurisdiction's field order
- Allowed non-owner location: local planning notes, PR and review evidence, git history, task coordination artifacts, working evidence, and closure evidence are evidence only until durable facts are promoted or closure facts recorded
- Allowed non-owner location: valid Changelog mirror surfaces are final agent reports, PR or release descriptions, and release or checklist outputs, after promotion and after the tracked Changelog is updated or marked `N/A + reason`
- Forbidden duplicate: requiring, routing, scaffolding, or recreating a separate project-doc truth owner outside the docs SSOT declared owner-doc path
- Forbidden duplicate: using Changelog as owner for behavior, invariants, project intent, architecture, rules, data truth, reusable governance policy, implementation rationale, active work, raw prompts, transcripts, or unpromoted evidence
- Forbidden duplicate: closure records in per-change tracked changelog files by default, `docs/project/learning/changelog.md`, restored `docs/project/change-records/`, restored change-record schemas, or restored checker flags
- Forbidden duplicate: raw prompts containing secrets, credentials, PII, customer data, or oversized pasted artifacts in tracked docs
- Forbidden duplicate: treating non-owner working evidence as project truth
- Coordinated update set: `AGENTS.md`
- Coordinated update set: `README.md`
- Coordinated update set: `agents-manifest.yaml`
- Coordinated update set: `docs/agents/governance/ssot/ssot.md`
- Coordinated update set: `docs/agents/governance/documentation/documentation.md`
- Coordinated update set: `docs/agents/governance/release/release.md`
- Coordinated update set: `docs/agents/governance/documentation/project-docs-template/project-docs-template.md`
- Coordinated update set: `docs/project/project_index.md`
- Coordinated update set: `docs/project/architecture/architecture.md`
- Coordinated update set: `docs/project/changelog/changelog_index.md`
- Coordinated update set: `docs/project/changelog/changelog.md`
- Coordinated update set: `docs/project/goal/goal_index.md`
- Coordinated update set: `docs/project/goal/goal.md`
- Coordinated update set: `docs/project/learning/learning.md`
- Coordinated update set: `scripts/check_governance_core/check_governance_core_main.py` public project-doc validator contract and public-API regression tests
- Verification witness: project-doc checks pass with durable truth routed through declared owner docs
- Verification witness: tracked Changelog closure records reference owner-promotion targets or `N/A + reason`
- Verification witness: active docs route material future-decision knowledge to declared owner docs
- Verification witness: new project truth docs are accepted only through the docs SSOT declared-owner path
- Verification witness: docs router validation has no active route to a non-owner project-truth surface
- Verification witness: retired change-record files and directories remain absent, retired checker flags remain absent from public command surfaces, and no per-change tracked changelog-file tree exists
- Verification witness: text audit confirms active project docs define no duplicate project-truth authority
- Review trigger: any proposal to add a separate project truth owner outside the docs SSOT declared-owner path
- Review trigger: any proposal to move durable project intent out of `goal.md`, weaken owner-doc promotion, or treat non-owner evidence as project-truth authority
- Review trigger: any proposal to add Changelog storage outside the tracked owner and valid mirror surface set, copy the release-checklist field template into non-owner docs, or restore retired change-record contracts
