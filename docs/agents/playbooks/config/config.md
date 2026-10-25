---
doc_type: playbook
ssot_owner: docs/agents/playbooks/config/config.md
update_trigger: config or constants centralization, validation, repair, or config-driven selection rules change
---

# Config

Jurisdiction: constants centralization, the config authority package, validation, defaults, JSON repair, and config-driven workflow selection.

```yaml
baseline:
  interface: "the standard-library JSON reader (the standard-library TOML reader for a hand-edited, read-only file) over one app-owned config file"
  pattern: "one ConfigManager owner over one owner-declared config file grouped by jurisdiction; parse, validate, migrate by schema_version, default, normalize, revalidate, durable atomic write; validated snapshots to consumers"
  reason: "the standard-library parser is the direct, dependency-free interface; a settings framework or a second validator creates a parallel validation authority"
  exception: "a declarative settings library only when multi-source layering (file plus environment plus CLI) is a declared requirement, recorded as one supersession"
```

## Constants
- MUST centralize sheet names, headers, statuses, folder names, prefixes and patterns, and column identifiers in the constants owner.
- A literal used more than once for the same meaning MUST become a named constant.
- Business and source data MUST stay out of private runtime constants.

## Config
- MUST use config for values varying by user, machine, or environment.
- Examples: Excel quit/kill timeouts, log directories, UI refresh intervals, calculation waits.

## Config authority package
A created or changed config-owned data, defaults, or settings authority MUST declare each contract below in its own owner surface.

### Authority boundary
- MUST name the owning module, config file, schema, external artifact, or owned doc.
- MUST state which facts it owns.
- MUST state which surfaces are examples, local overrides, or consumers only.

### ConfigManager public contract
- Each config authority MUST expose exactly one public `ConfigManager` contract.
- `ConfigManager` is the required role for the owner-facing boundary; the Lexicon (ssot) defines the term.
- Concrete file, module, class, service, path, and lifecycle design are project-derived and declared once.
- Non-owner surfaces MUST only submit intent and consume validated outputs, metadata/view model, or failure outcomes.
- Non-owner surfaces MUST read owned config artifacts only through the `ConfigManager`.
- The `ConfigManager` MUST be the only config facade.
- A project with exactly one live config owner MUST declare that owner as the `ConfigManager` instead of adding a wrapper.
- Other facades MUST be routed through it or pruned, leaving at most one wrapper.

### App identity and filename contract
- The config owner MUST declare filename derivation from the app identity owner or authoritative external format.
- `<APP_NAME>.json` is an example, not a default.
- The owner MUST declare identity consumption, filename, runtime-root derivation, and development/packaged location rules.
- Consumers MUST take location rules only from that contract (extends FP-10).

### JSON jurisdiction structure
- JSON config roots MUST be objects unless the owner declares another root shape.
- Top-level sections MUST be jurisdiction groups, not arbitrary buckets.
- Values that change or validate together MUST share a group or a declared child owner.
- Grouped scope covers activation/user intent, modes, paths, templates, limits, timeouts, validation knobs, output/report settings, and owned UI presentation settings.
- A flat one-field config is permitted only while no dependent decision-critical field exists.

### Customizable value routing
- User-tunable, machine/environment-specific, customer/source-specific, and configurable user-facing values MUST come from the declared config/data authority.
- Runtime code MUST obtain those values from that authority instead of hardcoding them.
- A stable internal constant is permitted in a constants owner only while it does not vary by user, machine, environment, customer, or source.
- An input artifact, schema, sample artifact, external system, or project data-truth owner is permitted to own business/source truth only when it is declared as the data authority.
- Runtime code MUST consume the validated owner value directly, keeping no private copy.

### Key contract
- MUST declare key identifiers and stable dot-paths.
- MUST declare type/shape and allowed values when enum-like.
- MUST classify each key required, optional, or defaultable.
- MUST declare defaults or declared migrations.
- Mutable runtime config MUST carry a monotonically increasing `schema_version` at the root. The loader MUST declare the highest `schema_version` it supports and return `FAILED_VALIDATION` for any higher one.
- Unknown keys MUST be rejected or preserved and round-tripped. Deprecated-key handling MUST be declared. A dropped key MUST be dropped visibly, never silently.

### Type and vocabulary contract
- Booleans MUST represent true binary facts only.
- `enabled` means persisted user intent only when the config owner declares that meaning.
- String enums MUST represent modes or states with more than two values.
- Durations and counts MUST use unit-bearing keys or an owner-declared unit.
- Path strings MUST declare path kind, resolution root, and existence requirement.
- Arrays MUST be homogeneous unless a tuple or object shape is declared.
- Objects MUST represent authority groups.
- `null` is valid only for an explicitly optional or cleared state.
- Mixed-type sentinel values and string-encoded lists are permitted only when the owner declares and validates that wire format.

### Examples and hints contract
- Runtime JSON MUST store runtime values only: declared defaults, migrations, unconfigured markers, user-provided values.
- Runtime JSON MUST exclude `_note`, `example`, `hint`, `description`, and similar keys.
- They are allowed only when declared as non-runtime metadata keys and validated or ignored deterministically.
- Examples MUST live in schema/metadata, sample config artifacts, or `ConfigManager`-owned GUI/CLI view-model metadata.
- GUI placeholders, faded helper text, tooltips, and CLI help are permitted to display those examples only when the examples come from that declared metadata.
- Placeholders MUST stay display-only: they are never persisted as real values and never count as validation success.

### Data-truth boundary
- Business/source data, source records, portal fields, user-facing mappings, workbook/sheet/header truth, thresholds, machine-specific paths, and external fields MUST route to their declared data authority.
- The Lexicon (ssot) defines the term declared data authority.

### Validation layers
- Schema and type validation MUST apply to every present key and every required key.
- Activation validation MUST apply when an `enabled`, selected, or mode-bearing group is active.
- Skipping activation-only requirements for a disabled group is permitted only when the config owner declares that behavior.
- Re-enabling or selecting a group MUST revalidate its required paths, templates, modes, and dependent values before runtime use.
- Disabled, hidden, stale, or unreachable values MUST become workflow input only through explicit validation.

### Loader lifecycle
- MUST declare order: parse, validate, normalize, default, migrate, repair, persist.
- MUST declare repair scope and missing-file creation behavior.
- MUST declare corrupt-original preservation or quarantine.
- MUST declare idempotent writes, atomic or bounded writes where supported, cleanup, and failure outcomes.
- Creating missing app-owned runtime JSON is permitted only at the owner-declared runtime path.
- That creation MUST use declared defaultable values plus owner-declared unconfigured markers only.

### Runtime location and name authority
- MUST declare the owner or derivation rule for config path, filename, and runtime root.
- Config ownership of these facts is permitted only when that is its declared jurisdiction.
- Otherwise config MUST consume the owning runtime-path authority.

### Consumer contract
- Consumption by workflow, GUI, CLI, tests, and docs is permitted only through validated snapshots or owner identifiers.
- They MUST leave defaults, missing required values, config repair, key meaning, and config-driven business rules to the config owner.

### GUI and CLI live-sync contract
- GUI controls and CLI flags MUST submit intent or presentation input only.
- They MUST call the same `ConfigManager` loader, validator, or runtime option resolver.
- They MUST call the same owning request-plan builder when request planning is a separate authority.
- Live enable/disable state MUST derive from one owner-backed snapshot, view model, or adapter.
- Disabled controls MUST leave persisted settings and dependent values unchanged.
- Disabled controls MUST leave selected workflow work in place and MUST leave invalid selected work with its non-success outcome.
- A UI preference write MUST go through the `ConfigManager` and return a revalidated snapshot or explicit failure.

### External reload contract
- Out-of-app config edits MUST be reloaded explicitly or by signature/version.
- Reload MUST run through the config owner.
- Reload MUST fail visibly on invalid, stale, unknown, or partially written JSON before updating controls or runtime plans.

### Observability and witnesses
- MUST emit logs or reports for config mutation or failure.
- MUST record key, path, and reason outcome records.
- Deterministic checks MUST cover default application, required-without-default failure, invalid or corrupt JSON, unknown and deprecated keys, grouped-section and activation validation, disabled-group non-execution, re-enable validation, GUI/CLI snapshot parity, save/reload failure visibility, idempotent no-rewrite, and runtime path and name derivation.

## Scope boundaries
- Repo-owned shared platform settings belong to the settings owner.

## Enum-like config values
- Allowed values and defaults MUST live in one lightweight owner.
- Config validation and runtime logic MUST import allowed values and defaults from that owner (extends the coding owner's No Duplicates rule).

## Validation and defaults
- The config SSOT MUST handle invalid values by reject or coerce.
- Defaults are allowed only when declared by the config SSOT.
- Defaults MUST be applied before runtime path selection.
- Missing or invalid required values MUST return an explicit failed or skipped outcome that records the key and reason (extends FP-29).
- Config that becomes stale relative to runtime conditions MUST expose a staleness witness.
- Workflow gates, mandatory flags, and processing limits MUST be declared config keys with declared defaults. The operator MUST be able to clear every stop by a config edit.

## JSON create, normalize, repair
- Creating, normalizing, or repairing owned non-secret config JSON is permitted only in the config owner or loader.
- The location MUST follow one declared mode. Installed mode resolves through the platform user-config directory. Portable mode resolves beside the executable. One declared predicate selects the active mode.
- The path rule MUST be declared once and reused by GUI, CLI, tests, and packaging.
- Repair MUST run before runtime workflow or path selection.
- Repaired config MUST be revalidated before use.
- The config SSOT MUST classify each key defaultable or required-without-default.
- Filling a defaultable missing or invalid key is permitted only with declared defaults or declared migrations.
- Required-without-default values, especially machine-specific file and folder paths, MUST be supplied, never invented.
- Starter JSON is permitted an owner-declared blank or unconfigured marker for them only while the marker is invalid for runtime use, produces `FAILED_VALIDATION` or `SKIPPED + key + reason`, and comes with GUI/CLI hints from the config owner metadata.
- Successful config mutation MUST record `REPAIRED_CONFIG + keys/reasons`.
- Failed config mutation MUST record the terminal outcome `FAILED_CONFIG_REPAIR + keys/reasons` (extends FP-29).
- Repair writes MUST be deterministic and idempotent.
- Already-normalized files MUST stay untouched.
- Corrupt originals MUST be preserved or quarantined with evidence of source path and reason.
- Writes MUST follow the filesystem two-phase commit.
- Config repair MUST change config values only, leaving business and source data untouched.
- Config repair MUST leave business rules to their owners and keep the single current runtime path (extends the coding owner's No Fallback or Legacy Runtime Paths rule).
- After config repair, invalid runtime input MUST still stop with a non-success outcome.

## Config-driven workflow selection
- Stage or mode selection by checkbox and config values is permitted only after SSOT validation and default application.
- Stage-selection defaults MUST live only in the config SSOT.
- A selected stage stays owned by its stage or rule authority.
- Business-rule ownership MUST stay with its rule authority after config selection.
- Missing or invalid required config for a selected stage MUST be reported with key and reason.
- Runtime code MUST run only the stage, backend, and business-rule outcome that their owners resolved.

## Dependency boundaries
- Config and constant owners MUST stay dependency-light, importing no runtime or UI modules.
- Enums and constants MUST live in shared lightweight modules. Their imports MUST stay acyclic.
