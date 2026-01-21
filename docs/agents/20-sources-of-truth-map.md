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

## Rules / conditions / validations
Owner: exactly one place.
- `is_*` predicates, `require_*` requirements, `validate_*` validators
- workflows/UI do not repeat the same business logic

## Workflows (orchestration)
Owner: one module or cohesive package.
- compose constants/config/rules
- call I/O adapters
- emit run outcomes (report/logs)

## Context injection (supporting docs selection)
Owner: `agents-manifest.yaml`
- task signal → which supporting docs/playbooks to load alongside `AGENTS.md`

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
