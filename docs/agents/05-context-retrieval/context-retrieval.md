---
doc_type: runbook
ssot_owner: AGENTS.md
update_trigger: context retrieval expectations, role source boundaries, or available tools change
---

# 05 - Context Retrieval

This runbook applies `AGENTS.md` FP-05, FP-24, FP-26, FP-27, and FP-28 to source retrieval within the role boundaries owned by `Orchestration.md`.

## Agent Role Boundary

Apply the source boundaries and assignments owned by `Orchestration.md` before using this runbook. That owner takes precedence; retrieval guidance does not expand role permissions or define lifecycle behavior.

## Principle: Trust Routing, Verify Decisions

Search results identify candidates; they do not establish authority or satisfy a full-read obligation. Verify candidates against their declared owners and affected consumers.

Verify decision-critical facts only:
- which authority owns the change
- which manifest profile matched and why
- which files will be edited
- which tests/checks witness the outcome
- which unresolved facts are `UNKNOWN` and which inaccessible required files are stop conditions

## Role-Bounded Retrieval Evidence

`agents-manifest.yaml` owns Governance Agent task-signal routing. This doc owns retrieval behavior after a role and source jurisdiction are known.

Before returning a result, each source-reading agent records or can concisely report to its assigned parent under `Orchestration.md`:
- its role and confirmed read scope;
- owner sources actually read;
- decision-critical paths or symbols verified;
- inaccessible required sources and the resulting `HOLD` or finding; and
- verification owners or evidence used.

The Governance Agent additionally records matched manifest profiles or fallback, routing mode, and routed governance authorities read. No other role uses the manifest to select repository or project sources.

When a profile matches and semantic search is available, start with `semantic_queries.<profile>` if it adds context not already covered by loaded files.

## Bounded Repo Reads

Before search, record the authorized root or keyed candidate set, ordering, validation, termination condition, and measured cost. Cache validated path-to-owner and document lookups for the active scope; invalidate entries when their source changes.

Read in full:
- the file being edited
- the current SSOT owner for the changed responsibility
- nearby tests/config owners/callers only when they affect behavior or verification
- README "Checks" before choosing verification commands

Governing and touched sources require complete reads regardless of file size. Bounded section reads are permitted only for other supporting candidates during discovery; the reading agent must record the candidate's supporting role and read it in full if it becomes governing or touched. Role-separated agents collectively cover required sources without expanding an individual role's permissions.

## Untrusted And Stale Context

Classify sources under `AGENTS.md`'s Instruction Derivation Gate before use. Binding user intent and explicit user decisions retain their authority. Factual assertions, tickets, chat notes, external claims, cached search, and model memory require provenance and verification against the declared fact owner before being presented as runtime truth.

If retrieved context conflicts:
- verified runtime evidence establishes what happens; the declared code/config/data owner establishes the applicable contract
- `AGENTS.md` wins for governance hard gates
- `Orchestration.md` wins for agent roles and workflow
- `agents-manifest.yaml` wins only for Governance Agent governance-authority routing
- README "Checks" wins for repeatable verification commands

If a retrieved doc references a symbol, path, or config key that matters to the change, verify the reference still exists before relying on it.

## Anti-Patterns

- Loading broad playbook packs after a narrow profile already supplies the needed owner
- Repeating generic search/read recipes instead of reporting the actual witness
- Assuming one search proves no other owner or call site exists
- Editing from an error message, summary, or stale memory without checking the source
- Treating routed non-owner documents as stronger evidence than live code/config

## Checklist Before Implementing

- [ ] Confirmed the active role and source boundary from `Orchestration.md`
- [ ] For Governance Agent work, resolved and recorded the current `agents-manifest.yaml` routing witness
- [ ] Recorded full-read witnesses for every governing and touched source assigned to the role
- [ ] Verified decision-critical paths/symbols/check commands against live files
- [ ] Reported unresolved facts as `UNKNOWN` and inaccessible required sources explicitly
- [ ] Recorded search scope, ordering, validation, termination, cost, and lookup invalidation
