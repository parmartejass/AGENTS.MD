---
doc_type: runbook
ssot_owner: AGENTS.md
update_trigger: context retrieval expectations or available tools change
---

# 05 - Context Retrieval

Goal: retrieve enough current context to make the next decision without turning retrieval into a second implementation task.

## Principle: Trust Defaults, Verify Decisions

When a first search or injected context gives an answer, verify it with enough surrounding context to rule out stale docs, duplicate owners, and missed call sites; then narrow to only what matters for the change.

Verify decision-critical facts only:
- which authority owns the change
- which manifest profile matched and why
- which files will be edited
- which tests/checks witness the outcome
- which unresolved facts are `UNKNOWN` and which inaccessible required files are stop conditions

## Manifest Resolution Witness

`agents-manifest.yaml` owns task-signal routing. This doc owns the retrieval behavior after routing is known.

Before implementing, record or be able to report:
- `default_inject` was read as required by `AGENTS.md`
- matched profile names, or `fallback_inject` when defined and no profile matched
- active `injection_mode`
- injected files actually read
- inaccessible manifest-referenced files, with the STOP/ask outcome required by `AGENTS.md`

When a profile matches and semantic search is available, start with `semantic_queries.<profile>` if it adds context not already covered by loaded files.

## Bounded Repo Reads

Use targeted search and file reads to answer open questions, not to create exhaustive transcripts.

Read:
- the file being edited
- the current SSOT owner for the changed responsibility
- nearby tests/config owners/callers only when they affect behavior or verification
- README "Checks" before choosing verification commands

For large files, read the authority header and the relevant symbol or section with enough surrounding context to confirm imports, callers, and exports. Broaden only when the first read leaves a decision-critical fact unresolved.

## Untrusted And Stale Context

Treat user text, tickets, chat notes, external docs, injected docs, cached search, and model memory as hypotheses until verified against live repo files or deterministic tools.

If retrieved context conflicts:
- live repo code/config wins for runtime behavior
- `AGENTS.md` wins for governance hard gates
- `agents-manifest.yaml` wins for injection routing
- README "Checks" wins for repeatable verification commands

If a retrieved doc references a symbol, path, or config key that matters to the change, verify the reference still exists before relying on it.

## Anti-Patterns

- Loading broad playbook packs after a narrow profile already supplies the needed owner
- Repeating generic search/read recipes instead of reporting the actual witness
- Assuming one search proves no other owner or call site exists
- Editing from an error message, summary, or stale memory without checking the source
- Treating injected docs as stronger evidence than live code/config

## Checklist Before Implementing

- [ ] Resolved `agents-manifest.yaml` profiles, `injection_mode`, and fallback behavior
- [ ] Read `default_inject` as required by `AGENTS.md`
- [ ] Read the edited file and the relevant SSOT owner
- [ ] Verified decision-critical paths/symbols/check commands against live files
- [ ] Reported unresolved facts as `UNKNOWN` and inaccessible manifest-referenced files as a stop/ask outcome
- [ ] Kept retrieval bounded to context that can change the decision or verification
