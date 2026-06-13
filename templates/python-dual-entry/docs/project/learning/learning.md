---
doc_type: runbook
ssot_owner: AGENTS.md
update_trigger: new domain pitfalls or operator learnings discovered
---

# Learning Notes (Project-Specific)

Purpose: capture practical learnings that help future changes, without turning docs into a second SSOT.

## Boundary
- This root doc owns recurring template pitfalls and verification tips.
- It does not own change history, task status, reusable governance policy, template goals, architecture, or data-truth routing.

## When to create a branch-local owner subdoc
- Create a learning subdoc when a stable lesson cluster needs its own intent, boundary, invariant, change rule, and verification.
- Do not create learning subdocs as chronological history or work-status records.

## Current Summary
- No branch-local learning subdocs are declared.

## Branch-local owner subdocs
- None currently declared.

Keep this focused on:
- pitfalls and failure modes discovered in real runs
- operational gotchas (paths, permissions, environment differences)
- verification tips (how to reproduce/confirm outcomes)

Avoid:
- duplicating constants/defaults from a different owner (reference the SSOT owner instead)
- re-implementing business rules in prose (reference the named rule functions/workflows)
