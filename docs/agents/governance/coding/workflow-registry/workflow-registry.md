---
doc_type: reference
ssot_owner: docs/agents/governance/coding/workflow-registry/workflow-registry.md
update_trigger: workflow index fields or coverage-witness expectations change
---

# Workflow Registry

Jurisdiction: the indexing view over the declared workflow registry and its coverage witness.

## Owner-resolved index

The declared registry MUST expose:

- workflow IDs and public entrypoints.
- input and output contracts plus artifact locations.
- rule, config, validation, lifecycle, and outcome owners.
- selected-stage entrypoints and config-selection contracts when applicable.

## Coverage witness

- Reconcile the workflow and selectable-stage universe from the declared composition contract against indexed IDs, entrypoints, and owner routes.
- Every declared workflow MUST be accounted for in that index.
- Record missing, duplicate, stale, or unresolved routes as findings against that owner.
- This reference defines no private terminal rule.

## Contract-field routing

- Contract fields MUST resolve through their declared contract owners.
- Registry entries MUST NOT restate defaults, predicates, business rules, or control semantics.
- Registry entries MUST reference those authorities instead.
