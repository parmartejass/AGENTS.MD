---
doc_type: reference
ssot_owner: AGENTS.md
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
- Governance SSOT: `AGENTS.md`
- Assigned-lead and subagent authority-routing manifest: `agents-manifest.yaml`
- Docs branch entrypoint: `docs/docs_index.md`
- Supporting governance docs: `docs/agents/agents_index.md`
- Validation scripts: `scripts/`

## SSOT pointers (concept -> owner)
- Governance rules: `AGENTS.md`
- Root authorities and role boundary: `AGENTS.md`
- Assigned-lead and subagent task-authority routing: `agents-manifest.yaml`
- Docs policy and headers: `docs/agents/25-docs-ssot-policy/docs-ssot-policy.md`
- Bounded project authority memory policy/detail: `docs/agents/25-docs-ssot-policy/docs-ssot-policy.md`
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
- `AGENTS.md` -> always-on governance hard gates, including the coding hard-gate trigger for implementation code and docs modularity for `docs/`; supporting docs, project docs, and checks must not weaken or fork it.
- `AGENTS.md` -> root/main versus assigned-lead boundary and canonical delegation line; the root/main retains complete intent, delegates once, receives only a terminal summary, and does not enter task-specific context or council work.
- `AGENTS.md` -> exact root authority membership, root/main versus assigned-lead SRP, canonical delegation line, and terminal-return boundary.
- `agents-manifest.yaml` -> assigned-lead/subagent task-profile and fallback authority routing used only inside the assigned-lead subtree.
- Assigned lead -> complete Mandatory Execution Loop, authority routing, council coordination/merge, implementation, verification, closure evidence, and terminal summary returned to the root/main.
- `docs/agents/25-docs-ssot-policy/docs-ssot-policy.md` -> docs validation reached through `scripts/check_governance_core/check_governance_core_main.py`
- `docs/agents/25-docs-ssot-policy/docs-ssot-policy.md` -> bounded project authority-memory policy/detail; project-doc leaves own the routed records declared by that policy
- `docs/agents/35-coding-principles/coding-principles.md` -> single delegated coding-principles and runtime-code authority-design mechanics jurisdiction under the `AGENTS.md` coding hard-gate trigger; the governance-core public contract enforces its checker-readable structural subset.
- `scripts/check_governance_core/check_governance_core_main.py` -> single public plain-data API and CLI; its public-contract tests cover docs routing, repository structure, and Python safety without external private imports.
- `scripts/check_governance_core/check_governance_core_main.py` -> sole public governance-core boundary; one private registry/engine composes cached document parsing, strict manifest parsing, docs/project checks, governance checks, bounded repository inventory, repository hygiene/structure, and Python safety. Private module names are not consumer contracts.
- `docs/agents/agents_index.md` router topology -> complete ordered governance research corpus exposed by `resolve_documents`; `agents-manifest.yaml` remains task-routing data and does not define corpus membership.
- `docs/agents/skills/` -> reusable skill bundles
- `docs/agents/settings/` -> shared settings examples and local-secret boundary
- `docs/agents/mcp/` -> canonical non-secret MCP payloads
- `docs/agents/22-ssot-authority-decisions/ssot-authority-decisions.md` `SSOT-DEC-004` -> project-local docs route durable facts into declared `docs/project/` owner docs; `docs/project/changelog/changelog.md` owns tracked closure-record facts after owner promotion; working evidence and mirror closure evidence remain non-owner evidence unless promoted into the declared owner.
- `docs/agents/22-ssot-authority-decisions/ssot-authority-decisions.md` -> allows `X-Bookmarks Import/` as a non-owner workspace exception without making it a canonical governance root

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
- A vendored governance pack under `.governance/` in downstream repos, with project docs under `docs/project/` and governance docs under `.governance/docs/agents/`.
- Repo-owned source assets under `docs/agents/skills/`, `docs/agents/settings/`, and `docs/agents/mcp/`; runtime installation is consumer-owned and not a tracked repo output.
