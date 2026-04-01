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

## Config (user-tunable)
Owner: exactly one place.
- keys + defaults + schema
- loader mechanism consistent with repo conventions

## Schema / types / data model
Owner: exactly one place.
- data shape and type definitions shared across modules
- validation rules remain in Rules / conditions / validations
- schema SSOT must be a single code location (module or generated schema); docs reference it only

## Rules / conditions / validations
Owner: exactly one place.
- `is_*` predicates, `require_*` requirements, `validate_*` validators
- workflows/UI do not repeat the same business logic

## Workflows (orchestration)
Owner: one module or cohesive package.
- compose constants/config/rules
- call I/O adapters
- emit run outcomes (report/logs)

## Module boundaries + contracts
Owner: exactly one place.
- authority boundaries recorded in `docs/project/architecture/architecture.md` (project root)
- module contracts defined in the authority module entrypoint (see `docs/agents/35-authority-bounded-modules/authority-bounded-modules.md`)

## Context injection (supporting docs selection)
Owner: `agents-manifest.yaml`
- task signal → which supporting docs/playbooks to load alongside `AGENTS.md`

## Cross-project SSOT authority decisions
Owner: `docs/agents/22-ssot-authority-decisions/ssot-authority-decisions.md`
- governance-level authority choices that apply across repos using this pack
- canonical owner + allowed non-owner locations + forbidden duplicates + coordinated migration or update set
- project-local adoption details remain in `docs/project/architecture/architecture.md`

## Platform assets (skills, settings, subagents, MCP, ACP)
Owner: `docs/agents/skills/00-skill-standards/skill-standards.md`, `docs/agents/settings/00-settings-standards/settings-standards.md`, `docs/agents/subagents/00-subagent-standards/subagent-standards.md`, `docs/agents/mcp/00-mcp-standards/mcp-standards.md`, `docs/agents/acp/00-acp-standards/acp-standards.md`
- repo-owned reusable platform assets and compatibility expectations
- runtime projection via `docs/agents/link_repo_assets.ps1`
- platform-specific guidance without policy duplication

## Concrete runtime path + support-level mapping
Owner: `docs/agents/platforms/runtime-projections.json`
- one concrete table for runtime targets, scope, support level, and projection mode
- canonical source paths resolve from the governance root; runtime targets resolve from the project root
- consumed by `docs/agents/link_repo_assets.ps1`
- justified by dated notes under `docs/agents/platforms/`

## Excel COM lifecycle
Owner: exactly one implementation.
- start/open, PID, quit, verify, bounded kill fallback

## GUI queue/drain + cancellation
Owner: exactly one implementation.
- worker posts to queue; UI drains via `after(...)`
- shutdown/cancel event enforced

## Agent instructions / prompt configuration
Owner: `AGENTS.md` + `agents-manifest.yaml`
- agent behavioral rules, constraints, and execution loops
- prompt/instruction content must not be scattered across ad-hoc files; consolidate in the governance root
- context injection manifest is the single map from task signals to supporting docs

## Run outcomes / reporting
Owner: exactly one place.
- per-item outcome: `EXECUTED` / `SKIPPED` / `FAILED` + reason
- output location policy centralized
