---
doc_type: reference
ssot_owner: AGENTS.md
update_trigger: workflow discovery or owning architecture routes change
---

# Workflow Registry / Index Reference

`AGENTS.md` FP-12 through FP-19 and No Orphan Code / No Orphan Docs govern ownership, contracts, extensibility, and discoverability. Runtime composition and public boundaries are owned by `docs/agents/35-coding-principles/coding-principles.md`; the project's architecture owner declares its concrete workflow registry. This reference supplies an indexing view, not implementation choices or another runtime policy.

## Owner-resolved index
The declared registry exposes identifiers and routes for:
- workflow IDs and public entrypoints;
- input/output contracts and artifact locations;
- rule, config, validation, lifecycle, and outcome owners;
- selected-stage entrypoints and config-selection contracts when applicable.

Coverage witness: reconcile the workflow and selectable-stage universe exposed by the declared composition/registry contract with indexed IDs, public entrypoints, and owner routes. Every declared workflow MUST be accounted for in that index; record missing, duplicate, stale, or unresolved routes as findings against that owner. Resolution and caller notification MUST use the declared composition and outcome contracts, including coding-principles Dependency Direction and logging-errors Silent failures; this reference supplies no private terminal rule.

Contract fields resolve through their FP-14 owners. Config-driven selection mechanics route to `docs/agents/40-config-constants/config-constants.md`; failure and reporting mechanics route to `docs/agents/30-logging-errors/logging-errors.md`. Registry entries reference these authorities without restating defaults, predicates, business rules, or control semantics.
