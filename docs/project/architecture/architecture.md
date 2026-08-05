---
doc_type: reference
ssot_owner: AGENTS.md
update_trigger: repo layout, injection profiles, or validation scripts change
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
- Governance SSOT: `AGENTS.md`
- Context injection manifest: `agents-manifest.yaml`
- Docs branch entrypoint: `docs/docs_index.md`
- Supporting governance docs: `docs/agents/agents_index.md`
- Validation scripts: `scripts/`

## SSOT pointers (concept -> owner)
- Governance rules: `AGENTS.md`
- Context injection routing: `agents-manifest.yaml`
- Docs policy and headers: `docs/agents/25-docs-ssot-policy/docs-ssot-policy.md`
- Bounded project authority memory policy/detail: `docs/agents/25-docs-ssot-policy/docs-ssot-policy.md`
- Project truth authority, tracked closure records, and non-owner evidence surfaces: `SSOT-DEC-004` in `docs/agents/22-ssot-authority-decisions/ssot-authority-decisions.md`
- Changelog closure records: `docs/project/changelog/changelog.md` owns tracked closure-record facts; `SSOT-DEC-004` owns valid/invalid closure-record surfaces; `docs/agents/90-release-checklist/release-checklist.md` owns field template/order.
- Durable project intent, objective, acceptance criteria, non-goals, and verification intent: `docs/project/goal/goal.md`
- Protected behavior records: branch-local architecture subdoc when concrete observable protected behavior exists.
- Project data-truth records: `docs/project/data-truth/data-truth.md`
- Durable operational learnings: `docs/project/learning/learning.md`
- Docs router/public-leaf filename contract: `scripts/check_governance_core/_docs_routes.py`
- Python script public entrypoint enforcement: `scripts/check_folder_architecture/check_folder_architecture_main.py`
- Docs SSOT/router validator: `scripts/check_governance_core/_manifest_and_docs.py`
- Project authority-doc validator owner: `scripts/check_governance_core/_project_authority_docs.py`
- Folder-architecture Python scope registry: `scripts/check_folder_architecture/scope.json`
- Repo-owned reusable assets: `docs/agents/skills/`, `docs/agents/settings/`, `docs/agents/mcp/`
- Runtime config and local-secret boundary: `docs/agents/settings/00-settings-standards/settings-standards.md`

## Authority graph (owners -> dependents)
- `AGENTS.md` -> always-on governance hard gates, including the coding hard-gate trigger for implementation code and docs modularity for `docs/`; supporting docs, project docs, and checks must not weaken or fork it.
- `agents-manifest.yaml` -> context injection procedure in `AGENTS.md` and supporting retrieval guidance
- `docs/agents/25-docs-ssot-policy/docs-ssot-policy.md` -> `scripts/check_governance_core/_manifest_and_docs.py`
- `docs/agents/25-docs-ssot-policy/docs-ssot-policy.md` -> bounded project authority-memory policy/detail; project-doc leaves own the routed records declared by that policy
- `docs/agents/35-coding-principles/coding-principles.md` -> single delegated coding-principles and runtime-code authority-design mechanics jurisdiction under the `AGENTS.md` coding hard-gate trigger; `scripts/check_folder_architecture/check_folder_architecture_main.py` enforces the current checker-readable subset from `scripts/check_folder_architecture/scope.json`
- `scripts/check_governance_core/_docs_routes.py` -> docs router/primary-leaf derivation in `scripts/check_governance_core/_manifest_and_docs.py`; `scripts/check_docs_router_contract/check_docs_router_contract_main.py` is the contract-test surface.
- `scripts/check_folder_architecture/check_folder_architecture_main.py` -> Python script public-entrypoint filename enforcement for direct `scripts/<feature>/` feature folders.
- `scripts/check_governance_core/` -> project-doc, manifest/docs, and governance marker checks in `scripts/check_governance_core/check_governance_core_main.py`, `_project_authority_docs.py`, `_manifest_and_docs.py`, and `_repo_and_governance.py`
- `scripts/check_folder_architecture/scope.json` -> declared Python roots/exceptions, script entrypoint folders, folder contract paths, text contracts, and Python import-tree boundaries enforced by `scripts/check_folder_architecture/check_folder_architecture_main.py`; non-Python modularity needs a separate declared witness before language-general coverage is claimed
- `docs/agents/skills/` -> reusable skill bundles
- `docs/agents/settings/` -> shared settings examples and local-secret boundary
- `docs/agents/mcp/` -> canonical non-secret MCP payloads
- `docs/agents/22-ssot-authority-decisions/ssot-authority-decisions.md` `SSOT-DEC-004` -> project-local docs route durable facts into declared `docs/project/` owner docs; `docs/project/changelog/changelog.md` owns tracked closure-record facts after owner promotion; working evidence and mirror closure evidence remain non-owner evidence unless promoted into the declared owner.
- `docs/agents/22-ssot-authority-decisions/ssot-authority-decisions.md` -> allows `X-Bookmarks Import/` as a non-owner workspace exception; `scripts/check_folder_architecture/scope.json` records that exception for checker scope without making it a canonical governance root

## Current Modularity Witness Boundary
- Enforced now: checker owners validate the declared docs, folder, manifest, and code-change witness contract facts above.
- Not claimed: language-general import enforcement, broad hardcoded decision-fact scanning, typed config boundary scanning, or selector runtime witnesses without separate structured owners.

## Retired Checker Contracts
- Retired change-record checker surfaces are governed by `SSOT-DEC-004`.
- Replacement verification path: route durable facts through the owning project docs and run the README "Checks" project-doc, docs-router, and governance-core commands.
- Downstream callers must use the current README "Checks" command list.

## Outputs
- A vendored governance pack under `.governance/` in downstream repos, with project docs under `docs/project/` and governance docs under `.governance/docs/agents/`.
- Repo-owned source assets under `docs/agents/skills/`, `docs/agents/settings/`, and `docs/agents/mcp/`; runtime installation is consumer-owned and not a tracked repo output.
