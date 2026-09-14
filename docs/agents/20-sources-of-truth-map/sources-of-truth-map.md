---
doc_type: reference
ssot_owner: AGENTS.md
update_trigger: AGENTS.md or Orchestration.md responsibilities change OR repo adopts new SSOT layout
---

# 20 — Sources of Truth Map (Concept → Owner)

This reference maps concepts to owners; it does not define their policy. `AGENTS.md` owns the Fundamental Principles. Concrete project owners resolve through `docs/project/architecture/architecture.md` and their declared public contracts.
Use `docs/agents/22-ssot-authority-decisions/ssot-authority-decisions.md` for governance-level authority decisions, migration contracts, and allowed non-owner locations when this conceptual map is not specific enough.

## File/Folder Structure Rule
This map follows the file/folder SSOT rule in `AGENTS.md`.
Use the sections below to identify the current SSOT jurisdiction and parent for a concept; keep the jurisdiction, duplication-pruning, and enforcement wording in `AGENTS.md`.

## Constants (literals)
Owner: the declared constants authority; centralization mechanics are in `docs/agents/40-config-constants/config-constants.md`.
- sheet names, headers, statuses
- folder names, prefixes/patterns
- column identifiers/keys

## Data-facing truth / business data
Owner: the input artifact, external system, declared config/constants owner, or dedicated data authority.
- workbook/sheet/header truth, portal fields, user-facing mappings, source records, and machine-specific paths
- permitted fact owners: `docs/agents/25-docs-ssot-policy/docs-ssot-policy.md` Rule: Declared owners own facts; its Bounded Project Authority Memory / Baseline placement identifies data-truth categories and record placement.
- actual source values stay in the declared input, external, config, schema, sample, workbook, or other data owner; project ownership/provenance/validation records route through `docs/project/data-truth/data-truth.md` only within that branch's declared scope.

## Config (user-tunable)
Owner: the declared config authority exposed through `docs/agents/40-config-constants/config-constants.md` Config authority package.
- keys + defaults + schema
- loader, normalization, deterministic repair behavior, and repair outcomes consistent with repo conventions
- each key classified as defaultable or required-without-default by the config owner

## Schema / types / data model
Owner: exactly one place.
- data shape and type definitions shared across modules
- validation rules remain in Rules / conditions / validations
- permitted owner forms and explicit doc-owned authority conditions: `docs/agents/25-docs-ssot-policy/docs-ssot-policy.md` Rule: Declared owners own facts and Bounded Project Authority Memory; config-owned schemas additionally resolve through `docs/agents/40-config-constants/config-constants.md` Config authority package.
- concrete schema owner and consumer routes: `docs/project/architecture/architecture.md`; provenance and validation expectations: the declared data owner or its project data-truth record. A project routing record does not replace an existing schema artifact owner.

## Rules / conditions / validations
Owner: exactly one place.
- `is_*` predicates, `require_*` requirements, `validate_*` validators
- consumer boundaries: `docs/agents/35-coding-principles/coding-principles.md`

## Workflows (orchestration)
Owner: one module or cohesive package.
- runtime composition and child authority boundaries: `docs/agents/35-coding-principles/coding-principles.md` Orchestration Boundaries
- selected-stage inputs: `docs/agents/40-config-constants/config-constants.md` Config-driven workflow selection
- run/stage outcomes: `docs/agents/30-logging-errors/logging-errors.md`

## Runtime path / backend selection
Owner: the workflow entrypoint owns the selected-path record unless the repo declares a dedicated config SSOT for that workflow; backend-selection rules remain owned by their rule/config authority.
- selected runtime path, backend, library, or execution mode
- selection must be recorded before execution and referenced by owner path
- failure/cleanup behavior: `docs/agents/35-coding-principles/coding-principles.md` No Fallback or Legacy Runtime Paths

## Coding principles / module boundaries + contracts
Owner by decision-critical fact.
- coding hard-gate trigger and precedence: `AGENTS.md`
- delegated coding-principles and runtime-code authority-design mechanics: `docs/agents/35-coding-principles/coding-principles.md`
- SSOT jurisdiction and post-diff purification mechanics for implementation code: `docs/agents/35-coding-principles/coding-principles.md`
- Repository structure and Python script public-entrypoint enforcement: `scripts/check_governance_core/check_governance_core_main.py` public contract
- authority boundaries recorded in `docs/project/architecture/architecture.md` (project root)
- module contracts defined in the authority module entrypoint

## SSOT jurisdiction and purification
Owner by decision-critical fact.
- always-on jurisdiction hard-gate trigger and precedence: `AGENTS.md`
- implementation-code jurisdiction mechanics, drift ledgers, source-level fix points, deletion/reroute plans, and post-diff purification mechanics: `docs/agents/35-coding-principles/coding-principles.md`
- docs placement and non-owner doc boundaries: `docs/agents/25-docs-ssot-policy/docs-ssot-policy.md`
- task-signal routing for jurisdiction/purification work: `agents-manifest.yaml`
- project-local owner graph records: `docs/project/architecture/architecture.md`

## Authority routing
Owner by decision-critical fact.
- Fundamental Principles, constitutional hard gates, Mandatory Foundations membership, and conflict precedence: `AGENTS.md`
- Foundation loading/application, parent accountability, Main and subagent roles, source/mutation/delegation boundaries, planning, council separation, execution, review, correction, and terminal workflow: `Orchestration.md`
- Governance Agent task signal -> governance-authority routing: `agents-manifest.yaml`
- role-bounded retrieval guidance and evidence: `docs/agents/05-context-retrieval/context-retrieval.md`

## Docs modularity / docs folder contracts
Owner by decision-critical fact.
- docs-modularity hard gate: `AGENTS.md`
- delegated docs-family mechanics: `docs/agents/25-docs-ssot-policy/docs-ssot-policy.md`
- docs router and public leaf validation facts: `scripts/check_governance_core/check_governance_core_main.py` public contract

## Bounded project authority memory
Owner of material-knowledge admission, automatic maintenance, safe supersession, and concise recursive structure: `docs/agents/25-docs-ssot-policy/docs-ssot-policy.md`. Records include consequential uncertainty and attributed agent decisions; they do not self-verify or self-authorize.

Owner: the existing `docs/project/` branch authorities, routed from `docs/project/project_index.md`.
- `docs/project/goal/goal.md` owns durable project intent, objective, acceptance criteria, non-goals, and verification intent.
- Explicit prompt-originated user decisions that change durable project intent, objective, acceptance criteria, non-goals, or verification intent route to `docs/project/goal/goal.md` after classification under `AGENTS.md`.
- `docs/project/rules/` owns project-specific protected boundaries.
- `docs/project/architecture/` owns authority pointers, verified behavior references, implementation rationale, accepted tradeoffs, and protected behavior invariants.
- `docs/project/data-truth/` owns project data-truth ownership, provenance, validation expectations, and routing to source artifacts, config/default/constant owners, schemas, samples, workbooks, and external systems.
- Durable user-provided data-truth assertions route to `docs/project/data-truth/` only when no more specific data owner holds the fact; record provenance, validation expectation, and supersession trigger.
- `docs/project/changelog/` owns tracked closure-record facts for completed non-trivial work after durable facts are promoted to their owners.
- `docs/project/learning/` owns reusable operational learnings only; change-specific what/how/why and supersession truth belongs in the highest owner doc for that fact.
- Working evidence is not a project-memory owner by default; promote only durable facts into the owning SSOT docs.

## Cross-project SSOT authority decisions
Owner: `docs/agents/22-ssot-authority-decisions/ssot-authority-decisions.md`
- governance-level authority choices that apply across repos using this pack
- canonical owner + allowed non-owner locations + forbidden duplicates + coordinated migration or update set
- project-local adoption details remain in `docs/project/architecture/architecture.md`

## Repo-owned agent source assets
Owner: source asset roots under `docs/agents/`
- `docs/agents/skills/` owns reusable skill bundles.
- `docs/agents/settings/` owns shared non-secret settings payloads.
- `docs/agents/mcp/` owns shared non-secret MCP payloads.
- Runtime installation is consumer-owned; tracked root runtime copies and repo-owned projection mappings are retired.

## Runtime config and secret boundary
Owner: `docs/agents/settings/00-settings-standards/settings-standards.md`
- repo-owned settings examples must be non-secret
- MCP credentials, tokens, and machine identities remain user-owned and ignored
- shared settings source files must stay non-secret and parseable by their owning format

## Excel COM lifecycle
Owner: exactly one implementation.
- start/open, PID, quit, verify, bounded PID-scoped forced termination after verified graceful-quit failure

## GUI queue/drain + cancellation
Owner: exactly one implementation.
- worker posts to queue; UI drains via `after(...)`
- shutdown/cancel event enforced

## Agent instructions / prompt configuration
Owner by decision-critical fact: `AGENTS.md` + `Orchestration.md` + `agents-manifest.yaml`
- constitutional agent principles, hard gates, and conflict precedence: `AGENTS.md`
- automatic constitutional application, preservation of complete binding user intent, user-decision precedence, and durable-record retrieval and maintenance duties: `AGENTS.md`
- agent lifecycle, roles, plan contract, council separation, execution, review, correction, and terminal decisions: `Orchestration.md`
- instruction derivation rules for prompts, plans, checklists, generated artifacts, and downstream scaffolds: `AGENTS.md` Instruction Derivation Gate
- reusable prompt/instruction policy: its declared governance owner; prompt scaffolds: `docs/agents/playbooks/ai-coding-prompt-template/ai-coding-prompt-template.md`; skill/settings source formats and placement: the Repo-owned agent source assets and Runtime config and secret boundary sections above.
- durable prompt-originated project intent: `docs/project/goal/goal.md`; other durable project facts: docs-policy Bounded Project Authority Memory / Baseline placement. Temporary prompt context remains non-authoritative unless promoted through that owner.
- `agents-manifest.yaml` is the single map from Governance Agent task signals to routed governance authorities
- Main's controlling-intent handling is owned by `Orchestration.md`; durable project truth is owned by the appropriate `docs/project/` owner doc

## Run outcomes / reporting
Owner: exactly one place.
- per-item outcome: `EXECUTED` / `SKIPPED` / `FAILED` + reason
- output location policy centralized
- known work reconciliation: `planned`, `eligible`, `executed`, `skipped`, `failed`
- feedback and reconciliation mechanics: `docs/agents/30-logging-errors/logging-errors.md`; foundational outcome obligation: `AGENTS.md` FP-29
- `Changelog` closure records: tracked project owner and valid mirror surfaces owned by `SSOT-DEC-004`; field template/order owned by `docs/agents/90-release-checklist/release-checklist.md`
