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
B) A CLI dispatcher (`main.py` / `cli.py`) listing workflows.
C) A docs index page listing workflows and entrypoints.

## Requirements
- Each workflow has a stable ID/name.
- Each workflow specifies: inputs, outputs/artifacts, and config keys used.
- No workflow is “hidden” without an index entry.

