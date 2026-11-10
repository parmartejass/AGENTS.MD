---
doc_type: reference
ssot_owner: docs/project/data-truth/data-truth.md
update_trigger: data-truth ownership, provenance, validation, or routing changes
---

# Data Truth

## Boundary
- This branch owns project-local data-truth routing and provenance notes when a project doc is the declared owner.
- It does not own reusable governance policy or code/config constants that already have declared owners.

## Current Summary
- No project-owned data-truth cluster is currently declared in this governance-pack repo.
- Code, config, schemas, source assets, and external systems remain owners of their own facts unless a project-doc owner is explicitly routed here.

## Change Rule
- Add a branch-local owner subdoc only when a concrete project data/config/constant/default/source-artifact truth must affect future behavior and no more specific owner holds it.
- Adding policy records or fixed truth-kind taxonomies here is Prohibited.

## Verification
- `docs/project/data-truth/data-truth_index.md` routes this branch; run root `README.md` Checks.
