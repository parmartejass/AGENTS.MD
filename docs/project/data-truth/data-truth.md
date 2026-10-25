---
doc_type: reference
ssot_owner: docs/project/data-truth/data-truth.md
update_trigger: data-truth ownership, provenance, validation, or routing changes
---

# Data Truth

## Purpose
- Record declared project data-truth owners and route consumers to them.
- Docs or doc-owned artifacts own facts only when explicitly declared here or in the referenced owner.

## Boundary
- This branch owns project-local data-truth routing and provenance notes when a project doc is the declared owner.
- It does not own reusable governance policy or code/config constants that already have declared owners.

## Current Summary
- No project-owned data-truth cluster is currently declared in this governance-pack repo.
- Code, config, schemas, and source assets remain owners of their own facts unless a project-doc owner is explicitly routed here.
- Material observations and data assertions follow `AGENTS.md` Instruction Derivation Gate and `docs/agents/governance/documentation/documentation.md`.

## Change Rule
- Add a branch-local owner subdoc only when a concrete project data/config/constant/default/source-artifact truth must affect future behavior and no more specific owner holds it.
- A qualifying assertion MUST record declared owner and fact identifier, redacted provenance, verification status and evidence, validation expectation, and supersession trigger.
- An unverified assertion stays labeled unverified until its declared witness passes.
- A checker is never a reason to add policy records here.
- This branch MUST stay free of fixed truth-kind taxonomies.

## Verification
- `docs/project/data-truth/data-truth_index.md` routes this branch.
- Run the project-doc and docs-router checks listed in `README.md` Checks.
