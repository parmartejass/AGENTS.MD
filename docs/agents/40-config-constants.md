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

## Config
Use config for values that may vary by user/machine/environment:
- timeouts (Excel quit/kill)
- log directories
- UI refresh intervals
- calculation waits

Rule: keys/defaults/schema must have a single owner; docs reference keys by identifier and point to the owner.

### Enum-like config values
- Allowed values and defaults live in one lightweight owner.
- Config validation and runtime logic must import from that owner; no duplicated lists.

### Validation + fallback
- Invalid config values are handled by the config SSOT (reject or coerce).
- Runtime fallback must use the config SSOT default and log key + value + fallback.

### Dependency boundaries
- Config/constant owners must remain dependency-light; avoid importing runtime/UI modules.
- Use shared lightweight modules for enums/constants to prevent circular imports.

