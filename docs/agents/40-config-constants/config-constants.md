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

### Config authority package
When a config-owned data, defaults, or settings authority is created or changed, the owner must declare the package contract in its own owner surface. The contract must include:
- Authority boundary: the owning module, config file, schema, external artifact, or explicitly owned doc; which facts it owns; and which surfaces are examples, projections, local overrides, or consumers only.
- ConfigManager public contract: every config-owned data, defaults, or settings authority must expose exactly one public `ConfigManager` contract. `ConfigManager` is the required role and term for the owner-facing boundary; its concrete file, module, class, service, artifact path, and internal lifecycle design are project-derived and declared once by that owner. Non-owner surfaces may submit intent and consume the `ConfigManager`'s validated outputs, metadata/view model, or explicit failure outcomes; they must not directly interpret owned config artifacts or create parallel config facades. Existing projects with one live config owner may adopt that owner as the `ConfigManager` by declaring it and routing or pruning other config facades through it, not by adding a second wrapper.
- App identity and filename contract: app-owned runtime JSON should derive its filename from one app identity owner when no external format dictates the name, conventionally `<APP_NAME>.json`. The config owner owns `APP_NAME` consumption, `CONFIG_FILENAME`, runtime path derivation, and whether development uses the project/main root while packaged apps use the executable folder. Do not hardcode "beside `main.py`" or "beside the executable" outside the owner-declared path rule.
- JSON jurisdiction structure: JSON config roots must be objects unless the owner explicitly declares a different root shape. Top-level sections are jurisdiction groups, not arbitrary buckets. Related values that change or validate together must live in the same group or in a declared child owner: activation/user intent, modes, paths, templates, limits, timeouts, validation knobs, output/report settings, and UI presentation settings when config owns them. A tiny one-field config may stay flat only while no dependent decision-critical field exists.
- Customizable value routing: user-tunable, machine/environment-specific, customer/source-specific, and configurable user-facing values must be supplied by the declared config/data authority instead of hardcoded in runtime code. Stable internal constants may remain in a constants owner; business/source truth may instead be owned by input artifacts, schemas, sample artifacts, external systems, or project data-truth owners. Runtime code must consume the validated owner value and must not keep a private copy for convenience.
- Key contract: key identifiers, stable dot-paths, type/shape, allowed values when enum-like, required/optional/defaultable classification, declared defaults or declared migrations, schema version or equivalent migration witness for mutable packages, and unknown/deprecated-key handling.
- Type and vocabulary contract: booleans are for true binary facts only; `enabled` means persisted user intent only when the config owner declares that meaning; string enums represent modes/states with more than two values; durations and counts must use unit-bearing keys or an owner-declared unit; path strings must declare path kind, resolution root, and existence requirement; arrays must be homogeneous unless a tuple/object shape is declared; objects represent authority groups; `null` is valid only for an explicitly optional or cleared state. Mixed-type sentinel values and encoded lists in strings are prohibited unless the owner declares and validates that wire format.
- Examples and hints contract: runtime JSON stores runtime values only: declared defaults, migrations, explicit unconfigured markers, and user-provided values. Do not add `_note`, `example`, `hint`, `description`, or similar documentation fields to runtime JSON unless the config owner declares them as non-runtime metadata keys and validates or ignores them deterministically. Preferred examples live in schema/metadata, sample config artifacts, or GUI/CLI view-model metadata owned by the `ConfigManager`. GUI placeholders, faded helper text, tooltips, and CLI help may display those examples, but placeholders must not be persisted as real values or treated as validation success.
- Data-truth boundary: business/source data, user-facing mappings, workbook/sheet/header truth, thresholds, machine-specific paths, and external fields must route to the input artifact, external system, project data-truth owner, declared config/constants owner, or other declared data authority that owns them.
- Validation layers: schema/type validation applies to every present key and every required key. Activation validation applies when an `enabled`, selected, or mode-bearing group is active. A disabled group may skip activation-only requirements only when the config owner declares that behavior; re-enabling or selecting the group must revalidate its required paths, templates, modes, and dependent values before runtime use. Disabled, hidden, stale, or currently unreachable values must not silently become valid workflow input.
- Loader lifecycle: parse, validate, normalize, default, migrate, repair, and persist order; repair scope; missing-file creation behavior; corrupt-original preservation or quarantine; idempotent writes; atomic replace or bounded-write behavior where supported; cleanup and failure outcomes. Missing app-owned runtime JSON may be created only at the owner-declared runtime path and only from declared defaultable values plus owner-declared unconfigured markers. Repo-owned config JSON must not contain secrets; mutation/failure logs must redact sensitive key names and summarize large payloads.
- Runtime location/name authority: the owner or derivation rule for config path, filename, runtime root, and projected settings target. Config may own these facts only when that is its declared jurisdiction; otherwise it must consume the owning runtime-path or projection authority.
- Consumer contract: workflow, GUI, CLI, tests, and docs may consume validated config snapshots or owner identifiers only. They must not duplicate defaults, infer missing required values, repair config, reinterpret key meaning, or own config-driven business rules.
- GUI/CLI live-sync contract: GUI controls and CLI flags submit intent or presentation input only. They must call the same `ConfigManager` loader, validator, or runtime option resolver, and the same owning request-plan builder when request planning is a separate authority. Live GUI enable/disable state must be derived from one owner-backed snapshot, view model, or adapter, and UI-thread mechanics remain governed by `docs/agents/60-gui-threading/gui-threading.md`. Disabled controls must not silently mutate persisted settings, clear dependent values, skip selected workflow work, or convert invalid selected work into success. If a UI change persists user preferences, the write must go through the `ConfigManager` and return a revalidated snapshot or explicit failure.
- External reload contract: if config JSON can be edited outside the app while the app is open, reload must be explicit or signature/version based, must run through the config owner, and must fail visibly on invalid, stale, unknown, or partially written JSON before updating controls or runtime plans.
- Observability and witnesses: redacted logs/reports for config mutation or failure, key/path/reason outcome records, and deterministic checks for default application, required-without-default failure, invalid/corrupt JSON, unknown/deprecated keys, grouped-section validation, activation validation, disabled-group non-execution, re-enable validation, GUI/CLI same-snapshot parity, save/reload failure visibility, idempotent no-rewrite behavior, and runtime path/name derivation.

Repo-owned shared platform settings route to `docs/agents/settings/00-settings-standards/settings-standards.md`; user-local secrets and machine-local overrides remain outside repo-owned config packages unless a future owner explicitly adopts a non-secret projection.

### Enum-like config values
- Allowed values and defaults live in one lightweight owner.
- Config validation and runtime logic must import from that owner; no duplicated lists.

### Validation + defaults
- Invalid config values are handled by the config SSOT (reject or coerce).
- Defaults are allowed only when declared by the config SSOT and applied before runtime path selection; missing or invalid required values must fail or be skipped explicitly with key + reason recorded.
- Config drift detection: when config values can become stale relative to runtime conditions (e.g., thresholds, timeouts, external API parameters), the config owner should expose a staleness witness (last-updated timestamp or validation check) so drift is surfaced explicitly rather than causing silent misbehavior.

### JSON config create/normalize/repair
- Only the config owner/loader may create, normalize, or repair owned non-secret config JSON.
- If an owner declares an app-local runtime JSON file, the loader may create the missing file at the owner-declared location, commonly the executable folder for packaged apps and a declared project/main root for development runs. This path rule must be declared once by the owner and reused by GUI, CLI, tests, and packaging.
- Repair runs before runtime workflow/path selection and the repaired config must be revalidated before use.
- Each config key must be classified by the config SSOT as defaultable or required-without-default.
- Defaultable missing/invalid keys may be filled only with declared defaults or declared migrations.
- Required-without-default values, especially machine-specific file/folder paths, must never be invented. They may be represented by an owner-declared blank/unconfigured marker in starter JSON only if that marker is invalid for runtime use, produces `FAILED_VALIDATION` or `SKIPPED + key + reason`, and is paired with GUI/CLI hints from the config owner's metadata.
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
