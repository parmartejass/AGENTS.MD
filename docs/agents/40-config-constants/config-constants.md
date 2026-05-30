---
doc_type: policy
ssot_owner: AGENTS.md
update_trigger: config/constants centralization rules change
---

# 40 — Config & Constants

## Constants
Centralize all shared literals:
- sheet names, headers, statuses
- folder names
- prefixes/patterns
- column identifiers

Rule: if a literal appears more than once for the same meaning, it must become a named constant in the constants owner.

Business/source data is not a private runtime constant. User-facing mappings, workbook/sheet/header truth, portal fields, source records, and machine-specific paths must come from the input artifact, external system, declared config/constants owner, project data-truth owner, or other owning data authority.

## Config
Use config for values that may vary by user/machine/environment:
- timeouts (Excel quit/kill)
- log directories
- UI refresh intervals
- calculation waits

Rule: keys/defaults/schema must have a single owner. Non-owner docs reference keys by identifier and point to the owner; docs or doc-owned artifacts may own keys/defaults/schema only when explicitly declared as that authority and paired with validation.

### Enum-like config values
- Allowed values and defaults live in one lightweight owner.
- Config validation and runtime logic must import from that owner; no duplicated lists.

### Validation + defaults
- Invalid config values are handled by the config SSOT (reject or coerce).
- Defaults are allowed only when declared by the config SSOT and applied before runtime path selection; missing or invalid required values must fail or be skipped explicitly with key + reason recorded.
- Config drift detection: when config values can become stale relative to runtime conditions (e.g., thresholds, timeouts, external API parameters), the config owner should expose a staleness witness (last-updated timestamp or validation check) so drift is surfaced explicitly rather than causing silent misbehavior.

### JSON config create/normalize/repair
- Only the config owner/loader may create, normalize, or repair owned non-secret config JSON.
- Repair runs before runtime workflow/path selection and the repaired config must be revalidated before use.
- Each config key must be classified by the config SSOT as defaultable or required-without-default.
- Defaultable missing/invalid keys may be filled only with declared defaults or declared migrations.
- Required-without-default values must never be invented; they produce `FAILED_VALIDATION` or `SKIPPED + key + reason`.
- Successful config mutation records `REPAIRED_CONFIG + keys/reasons`.
- Failed config mutation records terminal `FAILED_CONFIG_REPAIR + keys/reasons`.
- Repair writes must be deterministic and idempotent; avoid rewriting already-normalized files.
- Preserve or quarantine corrupt originals with enough evidence to diagnose the source path and reason.
- Use bounded writes and atomic replace where repo conventions/platform support it; cleanup failure must be explicit.
- Config repair must not repair business/source data, infer business rules, select substitute runtime paths, or convert invalid runtime input into successful continuation.

### Config-driven workflow selection
- Checkbox/config values may select stages or modes only after config SSOT validation/default application.
- Defaults for stage selection live only in the config SSOT.
- A selected stage remains owned by its stage/rule authority; config selection does not transfer business-rule ownership to the workflow.
- Missing or invalid required config for a selected stage must be reported with key + reason; runtime code must not infer an alternate stage, backend, or business-rule outcome.

### Dependency boundaries
- Config/constant owners must remain dependency-light; avoid importing runtime/UI modules.
- Use shared lightweight modules for enums/constants to prevent circular imports.
