---
doc_type: reference
ssot_owner: docs/project/data-truth/data-truth.md
update_trigger: template input, output, scenario schema, config, or fixture authority changes
---

# Data Truth

## Intent
- Route consumers to the template artifacts that own scenario keys, scenario loading, fixtures, expected outputs, and event-log output behavior.

## Boundary
- Scenario key truth is owned by `templates/python-dual-entry/myapp/config_keys.py`.
- Scenario loading and scenario path resolution are owned by `templates/python-dual-entry/myapp/scenarios.py`.
- Scenario fixture, expected-output, and test-output workspace truth is owned by `templates/python-dual-entry/tests/`.
- Default event-log output behavior is owned by `templates/python-dual-entry/myapp/logging_config.py`.
- This doc routes those owners and does not duplicate file contents or schema values.

## When to create a branch-local owner subdoc
- Create a data-truth subdoc when a stable template data/source/config cluster needs its own intent, boundary, invariant, change rule, and verification.
- Do not create fixed truth-kind taxonomies or duplicate code/test-owned values here.

## Current Summary
- Scenario key truth is owned by `templates/python-dual-entry/myapp/config_keys.py`.
- Scenario loading and scenario path resolution are owned by `templates/python-dual-entry/myapp/scenarios.py`.
- Scenario fixture and expected-output truth is owned by `templates/python-dual-entry/tests/`.
- Default event-log output behavior is owned by `templates/python-dual-entry/myapp/logging_config.py`.

## Invariant
- Runtime and tests consume scenario keys from `templates/python-dual-entry/myapp/config_keys.py`.
- Runtime and tests load scenarios through `templates/python-dual-entry/myapp/scenarios.py`.
- Scenario fixtures and expected outputs stay under `templates/python-dual-entry/tests/` and are verified by the template test harness.
- Default event-log output behavior stays behind `templates/python-dual-entry/myapp/logging_config.py`.

## Change Rule
- Update the owning code or test artifacts first, then update this routing note only if ownership, provenance, consumers, or verification changes.

## Branch-local owner subdocs
- None currently declared.

## Verification
- `templates/python-dual-entry/README.md` section "Checks" owns the deterministic template verification commands.
