---
doc_type: reference
ssot_owner: AGENTS.md
update_trigger: responsibilities list changes OR repo adopts new SSOT layout
---

# 20 — Sources of Truth Map (Concept → Owner)

This is a conceptual map. In any given repo, the “owner” may be a module, package, or doc index.

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
- authority boundaries recorded in `docs/project/architecture.md` (project root)
- module contracts defined in the authority module entrypoint (see `docs/agents/35-authority-bounded-modules.md`)

## Context injection (supporting docs selection)
Owner: `agents-manifest.yaml`
- task signal → which supporting docs/playbooks to load alongside `AGENTS.md`

## Skills (platform adapters + standards)
Owner: `docs/agents/skills/00-skill-standards.md`
- skill standards and compatibility expectations
- platform-specific adapter guidance (no policy duplication)

## Excel COM lifecycle
Owner: exactly one implementation.
- start/open, PID, quit, verify, bounded kill fallback

## GUI queue/drain + cancellation
Owner: exactly one implementation.
- worker posts to queue; UI drains via `after(...)`
- shutdown/cancel event enforced

## Run outcomes / reporting
Owner: exactly one place.
- per-item outcome: `EXECUTED` / `SKIPPED` / `FAILED` + reason
- output location policy centralized
