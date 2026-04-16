---
doc_type: reference
ssot_owner: AGENTS.md
update_trigger: workflow indexing requirements change
---

# Workflow Registry / Index Standard

There must be a single predictable place to find:
- workflow entrypoints
- workflow IDs/names
- required inputs/outputs
- related config keys

## Allowed implementations (choose one)
A) A `WORKFLOWS` registry dictionary in a central module.
B) A parent folder entrypoint resolved from `scripts/entrypoint_contracts.json` (for example `billing_main.py` or `billing_index.ts`) listing workflows and composing child feature folders.
C) A docs index page listing workflows and entrypoints.

## Requirements
- Each workflow has a stable ID/name.
- Each workflow specifies: inputs, outputs/artifacts, config keys used, and failure mode (what happens on error and how the caller is notified).
- No workflow is “hidden” without an index entry.
