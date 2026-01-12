---
doc_type: runbook
ssot_owner: AGENTS.md
update_trigger: context retrieval expectations or available tools change
---

# 05 — Context Retrieval Best Practices (Hard Gate)

Goal: retrieve complete, relevant context before reasoning or implementing, and avoid incomplete/incorrect conclusions caused by partial reads.

## Principle: Fetch Enough, Then Narrow

When uncertain, retrieve more surrounding context (imports, call sites, config owners, tests), then narrow to only what matters for the change.

## Grep (Ripgrep) Practices

### Use multiple passes
- Pass 1: exact symbol/function name
- Pass 2: related terms (caller, callee, config key, error message)
- Pass 3: file globs to catch configs/docs

### Include context lines
```sh
rg -n -C 5 "pattern"
rg -n -B 10 "pattern"
rg -n -A 20 "pattern"
```

### Find call sites and references
```sh
rg -n "function_name\\("
rg -n "def function_name"
rg -n "function_name"
```

### Filter by file type / glob
```sh
rg -n --type py "pattern"
rg -n --type md "pattern"
rg -n -g "*.yaml" "pattern"
```

## Semantic Search Practices (If Available)

- Ask complete questions (not single keywords).
- Keep one concept per query; split combined questions into multiple queries.
- When a profile matches in `agents-manifest.yaml`, prefer starting with `semantic_queries.<profile>`.
- Narrow scope first (directory/module), then broaden if results are thin.

## File Reading Practices

### Read full files when small
If a file is small enough to read quickly, read it fully. Top-of-file imports and bottom-of-file exports/entrypoints often matter.

### For large files, read in overlapping chunks
- Read start-of-file (imports, constants, class definitions).
- Jump to the target symbol (use grep for line numbers first).
- Read surrounding call sites and the file tail (entrypoints/exports).

### Always read related files together
When you touch a module, also check:
- its tests (if present)
- its config/constants owners (if referenced)
- its package/entrypoints (`__init__.py`, `__main__.py`, CLI/GUI dispatchers)

### Read before editing (hard gate)
Never edit a file you haven't read.

## Anti-Patterns (Reject)

- Grepping for one symbol and assuming you found all usages
- Reading only a function body without imports/class context
- Assuming file paths/symbols without verifying with `rg`/`ls`
- Making edits based only on error messages without reading the source

## Checklist Before Implementing

- [ ] Consulted `agents-manifest.yaml` and injected applicable docs/playbooks
- [ ] Grepped for primary symbol and related terms
- [ ] Read the full file (or overlapping chunks for large files)
- [ ] Read tests/config owners when relevant
- [ ] Identified the SSOT owner(s) to extend (no parallel ownership)
