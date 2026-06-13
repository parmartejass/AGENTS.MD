---
doc_type: reference
ssot_owner: docs/project/data-truth/data-truth.md
update_trigger: data-truth ownership, provenance, validation, or routing changes
---

# Data Truth

## Purpose
- Record declared project data-truth owners and route consumers to them.
- Allow docs or doc-owned artifacts to own facts only when explicitly declared here or in the referenced owner.
- Prevent duplicate/non-owner copies of values, mappings, defaults, headers, thresholds, paths, or business/source data.

## Boundary
- This branch owns project-local data-truth routing and provenance notes when a project doc is the declared owner.
- This branch does not own reusable governance policy, runtime projection mappings, or code/config constants that already have declared owners.

## Current Summary
- No project-owned data-truth cluster is currently declared in this governance-pack repo.
- Existing code, config, schemas, runtime projection manifests, and templates remain the owners for their own concrete facts unless a future project-doc owner is explicitly routed here.

## When to create a branch-local owner subdoc
- Create a data-truth subdoc when a stable project data/config/constant/default/source-artifact cluster needs its own intent, boundary, invariant, change rule, verification, and references.
- Do not create fixed truth-kind taxonomies or duplicate code/config/schema/source-owned values here.

## Change Rule
- Add or update a branch-local owner subdoc only when a concrete project data/config/constant/default/source-artifact truth must affect future behavior and no more specific owner already holds it.
- Do not add policy records here to satisfy a checker.

## Branch-local owner subdocs
- None currently declared.

## Verification
- `docs/project/data-truth/data-truth_index.md` routes this branch.
- README "Checks" owns the deterministic project-doc and docs-router verification commands.
