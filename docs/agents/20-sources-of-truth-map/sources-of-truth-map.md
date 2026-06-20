---
doc_type: reference
ssot_owner: AGENTS.md
update_trigger: responsibilities list changes OR repo adopts new SSOT layout
---

# 20 — Sources of Truth Map (Concept → Owner)

This is a conceptual map. In any given repo, the “owner” may be a module, package, or doc index.
Use `docs/agents/22-ssot-authority-decisions/ssot-authority-decisions.md` for governance-level authority decisions, migration contracts, and allowed non-owner locations when this conceptual map is not specific enough.

## File/Folder Structure Rule
This map follows the file/folder SSOT rule in `AGENTS.md`.
Use the sections below to identify the current SSOT parent for a concept; keep the full policy and enforcement wording in `AGENTS.md`.

## Constants (literals)
Owner: exactly one place.
- sheet names, headers, statuses
- folder names, prefixes/patterns
- column identifiers/keys

## Data-facing truth / business data
Owner: the input artifact, external system, declared config/constants owner, or dedicated data authority.
- workbook/sheet/header truth, portal fields, user-facing mappings, source records, and machine-specific paths
- business/workflow logic consumes validated owner-provided values; it must not embed private copies of changing data-facing truth
- docs and scripts reference the owner by identifier unless a doc or doc-owned artifact is explicitly declared as the data authority
- data-facing truths include business/source data, mappings, workbook/sheet/header truth, schemas, portal fields, thresholds, settings, machine paths, config defaults, constants, sample artifacts, and external fields
- permitted owners include input artifacts, external systems, declared config/default files, constants modules, schemas, sample data, project docs explicitly marked as owner, and other declared data authorities

## Config (user-tunable)
Owner: exactly one place.
- keys + defaults + schema
- loader, normalization, deterministic repair behavior, and repair outcomes consistent with repo conventions
- each key classified as defaultable or required-without-default by the config owner

## Schema / types / data model
Owner: exactly one place.
- data shape and type definitions shared across modules
- validation rules remain in Rules / conditions / validations
- schema SSOT must be a single declared owner (module, generated schema/artifact, external schema, workbook/source artifact, or explicitly owned project doc); non-owner docs reference it only

## Rules / conditions / validations
Owner: exactly one place.
- `is_*` predicates, `require_*` requirements, `validate_*` validators
- workflows/UI do not repeat the same business logic

## Workflows (orchestration)
Owner: one module or cohesive package.
- coordinate runtime execution only: validated plan, stage order, child contract calls, I/O/lifecycle adapter calls, and run outcomes
- compose constants/config/rules by calling their owners; do not define, duplicate, or reinterpret business rules, predicates, validation logic, constants, schema, config keys/defaults, backend-selection rules, lifecycle policy, or UI control semantics
- checkbox/config-selected stages are runtime plan inputs; selected child stages own their own eligibility checks, validation, transformations, output contracts, and terminal outcomes
- record selected runtime path/backend before execution when selection is in scope
- emit per-run and per-stage outcomes (`EXECUTED` / `SKIPPED` / `FAILED` + reason)
- stop the affected branch/item after validation, execution, commit, or cleanup failure; do not continue that branch/item through substitute paths

## Runtime path / backend selection
Owner: the workflow entrypoint owns the selected-path record unless the repo declares a dedicated config SSOT for that workflow; backend-selection rules remain owned by their rule/config authority.
- selected runtime path, backend, library, or execution mode
- selection must be recorded before execution and referenced by owner path
- failure after selection produces a terminal outcome; runtime code must not switch to a substitute path
- Python-backed PowerShell script interpreter resolution owner: `scripts/_python_check_runner.ps1` (`-PythonExe`, otherwise `python3`, then `python`, Python 3.11+ required, selected path printed before execution). This covers checker wrappers and runtime-projection TOML validation.

## Coding principles / module boundaries + contracts
Owner by decision-critical fact.
- coding hard-gate trigger and precedence: `AGENTS.md`
- delegated coding-principles and runtime-code authority-design mechanics: `docs/agents/35-coding-principles/coding-principles.md`
- SSOT jurisdiction and post-diff purification mechanics for implementation code: `docs/agents/35-coding-principles/coding-principles.md`
- public contract filename pattern facts: `scripts/entrypoint_contracts.json`
- authority boundaries recorded in `docs/project/architecture/architecture.md` (project root)
- module contracts defined in the authority module entrypoint

## SSOT jurisdiction and purification
Owner by decision-critical fact.
- always-on jurisdiction hard-gate trigger and precedence: `AGENTS.md`
- implementation-code jurisdiction mechanics, drift ledgers, source-level fix points, deletion/reroute plans, and post-diff purification mechanics: `docs/agents/35-coding-principles/coding-principles.md`
- docs placement and non-owner doc boundaries: `docs/agents/25-docs-ssot-policy/docs-ssot-policy.md`
- task-signal routing for jurisdiction/purification work: `agents-manifest.yaml`
- project-local owner graph records: `docs/project/architecture/architecture.md`

## Context injection (supporting docs selection)
Owner: `agents-manifest.yaml`
- task signal → which supporting docs/playbooks to load alongside `AGENTS.md`

## Docs modularity / docs folder contracts
Owner by decision-critical fact.
- docs-modularity hard gate: `AGENTS.md`
- delegated docs-family mechanics: `docs/agents/25-docs-ssot-policy/docs-ssot-policy.md`
- docs router and public leaf filename pattern facts: `scripts/entrypoint_contracts.json`

## Bounded project authority memory
Owner: the existing `docs/project/` branch authorities, routed from `docs/project/project_index.md`.
- `docs/project/goal/goal.md` owns durable project intent, objective, acceptance criteria, non-goals, and verification intent.
- `docs/project/rules/` owns project-specific protected boundaries.
- `docs/project/architecture/` owns authority pointers, verified behavior references, implementation rationale, accepted tradeoffs, and protected behavior invariants.
- `docs/project/data-truth/` owns project data-truth ownership, provenance, validation expectations, and routing to source artifacts, config/default/constant owners, schemas, samples, workbooks, and external systems.
- `docs/project/learning/` owns reusable operational learnings only; change-specific what/how/why and supersession truth belongs in the highest owner doc for that fact.
- Working evidence is not a project-memory owner by default; promote only durable facts into the owning SSOT docs.

## Cross-project SSOT authority decisions
Owner: `docs/agents/22-ssot-authority-decisions/ssot-authority-decisions.md`
- governance-level authority choices that apply across repos using this pack
- canonical owner + allowed non-owner locations + forbidden duplicates + coordinated migration or update set
- project-local adoption details remain in `docs/project/architecture/architecture.md`

## Repo-owned agent assets and runtime projections
Owner: `docs/agents/platforms/runtime-projections.json` + source asset roots under `docs/agents/`
- source roots own reusable skills, shared settings, and MCP payloads
- runtime projection targets are declared once in `docs/agents/platforms/runtime-projections.json`
- projected dotpaths are non-owner runtime surfaces; do not treat them as canonical source roots

## Runtime config and secret boundary
Owner: `docs/agents/settings/00-settings-standards/settings-standards.md`
- repo-owned settings examples must be non-secret
- MCP credentials, tokens, and machine identities remain user-owned and ignored
- projected settings files must stay non-secret and derive from the declared source owners

## Excel COM lifecycle
Owner: exactly one implementation.
- start/open, PID, quit, verify, bounded PID-scoped forced termination after verified graceful-quit failure

## GUI queue/drain + cancellation
Owner: exactly one implementation.
- worker posts to queue; UI drains via `after(...)`
- shutdown/cancel event enforced

## Agent instructions / prompt configuration
Owner: `AGENTS.md` + `agents-manifest.yaml`
- agent behavioral rules, constraints, and execution loops
- instruction derivation rules for prompts, plans, checklists, generated artifacts, and downstream scaffolds
- prompt/instruction content must not be scattered across ad-hoc files; consolidate in the governance root
- context injection manifest is the single map from task signals to supporting docs
- controlling-intent handling is owned by `AGENTS.md`; durable project truth is owned by the appropriate `docs/project/` owner doc

## Run outcomes / reporting
Owner: exactly one place.
- per-item outcome: `EXECUTED` / `SKIPPED` / `FAILED` + reason
- output location policy centralized
- known work reconciliation: `planned`, `eligible`, `executed`, `skipped`, `failed`
- user-visible status/reporting consumes workflow outcomes and reason codes; UI/CLI/report surfaces must not redefine success, failure, skip, or no-op semantics
- user-facing summaries include accepted input/scope, progress/current phase for long work, terminal result, produced artifacts, skip/failure reason, required user action, and run/report/log pointer when applicable
- `Changelog` closure witness: valid/invalid surfaces owned by `SSOT-DEC-004`; field template/order owned by `docs/agents/90-release-checklist/release-checklist.md`
