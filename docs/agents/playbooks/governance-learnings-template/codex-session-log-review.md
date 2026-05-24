---
doc_type: playbook
ssot_owner: docs/agents/playbooks/governance-learnings-template/codex-session-log-review.md
update_trigger: Codex session evidence handoff method or output contract changes
---

# Codex Session Log Review Evidence Handoff

## Purpose

Use this playbook to collect bounded, deterministic evidence from local Codex session logs for a requested timeframe and concept, then hand the evidence to `governance-learnings-template.md`.

This file owns evidence acquisition only. It does not decide whether evidence becomes a governance update.

## Authority Boundary

- Evidence collection owner: this file.
- Governance promotion/rejection owner: `governance-learnings-template.md` Promotion / Noise Gate.
- Context routing owner: `agents-manifest.yaml`.
- Privacy/redaction baseline: `docs/agents/30-logging-errors/logging-errors.md`.

Do not encode concept-specific search terms in this playbook. The run supplies the concept query.

## Required Inputs

- review goal:
- absolute timeframe start:
- absolute timeframe end:
- timezone:
- inclusivity rule: start inclusive, end exclusive unless the user requests otherwise
- authorized log root(s):
- authorized evidence source(s), when using non-log sources:
- concept query:
  - include terms:
  - aliases:
  - exclude terms:
  - case sensitivity:
  - regex allowed: yes/no
  - semantic inference allowed: yes/no
- project/repo filter, if any:
- output evidence limit:
- scan budget:
  - max files:
  - max bytes per file:
  - max total bytes:
  - max runtime seconds:
- redaction requirements:

If the user gives a relative timeframe, normalize it to absolute timestamps before scanning. If the timeframe remains ambiguous, stop with `AMBIGUOUS_TIMEFRAME`.

## Repeatable Workflow Packaging Evidence Mode

Use this mode when the review goal is to find repeated manual workflows that may deserve packaging as a skill, existing-asset extension, automation, subagent, skip, or defer decision.

This mode is still evidence acquisition only. It may recommend a candidate form and handoff owner, but it must not create, extend, install, schedule, or mutate any asset. Promotion, rejection, backlog, and edits remain owned by `governance-learnings-template.md` and the relevant asset authority.

### Timeframe Rule

- Normalize "last 30 days" to absolute start and end timestamps in the requested timezone before scanning.
- Treat the end timestamp as exclusive unless the user requests otherwise.
- "All available history if shorter" means the full inventory inside authorized roots or authorized source systems only. It must not expand root scope, scan `{HOME}` broadly, or read unapproved sources.
- If the relative timeframe cannot be normalized deterministically, stop with `AMBIGUOUS_TIMEFRAME`.

### Evidence Source Order

Use available evidence in this order, without silently omitting unavailable sources:

1. Recent Codex sessions and task summaries from authorized log roots.
2. Codex Memories and rollout summaries, only when the runtime exposes them and the user authorizes access.
3. Chronicle, only when enabled and authorized; use it for discovery only.
4. Existing skills, reusable assets, custom agents, automations, and projections, only through their current source owners.

For each source, record one status:

- `available_authorized`: source is available, authorized, and searched within budget.
- `unavailable`: source does not exist or is not exposed by the runtime.
- `skipped_unauthorized`: source exists or may exist, but approval was not given.
- `partial`: source was authorized but scan limits, parse failures, or timeouts prevented a complete search.

Authorized sources that are not fully searched must contribute to `PARTIAL_SEARCH` or an explicit `unknowns` entry. Chronicle-only candidates cannot be high confidence until confirmed in the relevant source system.

### Candidate Criteria

Include a workflow candidate only when evidence shows it is repeated, costly, error-prone, context-heavy, or benefits from a consistent process.

Rank higher when:

- it occurred at least twice with dated evidence
- it is clearly likely to recur and has concrete cost or risk evidence
- inputs are stable, the procedure is repeatable, and the output or stopping condition is clear
- packaging would materially improve speed, quality, consistency, or reliability
- existing assets do not already cover it adequately

Downgrade or defer when:

- evidence is single-source, indirect, unconfirmed, or Chronicle-only
- the workflow is one-off, ambiguous, sensitive, or poorly bounded
- the candidate overlaps an existing skill or asset that should be extended instead
- the recommended form lacks a current owner or deterministic verification path

### Recommended Form Routing

- `extend_existing`: use when an existing skill, playbook, setting, MCP asset, or automation already covers most of the workflow.
- `skill`: route to `docs/agents/skills/00-skill-standards/skill-standards.md`; this playbook must not define creation steps.
- `automation`: recommend only when an active project-local automation owner exists; otherwise use `defer` or `skip`.
- `subagent`: recommend only when an active project-local subagent owner exists; repo-owned subagent source docs and role adapters are not canonical in this governance pack.
- `skip`: use for one-off, sensitive, weakly evidenced, already-covered, or unsupported candidates.
- `defer`: use when the workflow may be useful but needs more evidence, owner confirmation, or source-system verification.

Prefer extending an existing asset over creating a new one. Every skipped or deferred candidate must include a reason.

### Packaging Shortlist Fields

When this mode is used, include a compact shortlist with one row per candidate:

- repeated_workflow:
- supporting_evidence_and_dates:
- occurrence_count:
- source_types:
- source_confirmation_status:
- frequency_confidence:
- existing_coverage_or_likely_duplicate:
- recommended_form (`skill` | `extend_existing` | `automation` | `subagent` | `skip` | `defer`):
- worth_packaging_reason:
- skip_or_defer_reason:
- next_owner_or_handoff_target:

## Root Authorization

Session logs are local runtime evidence, not governance-owned facts.

Rules:

- Use only user-provided or user-approved log roots.
- Resolve every selected root to an absolute path before scanning.
- Reject traversal outside selected roots.
- Do not scan broad home, drive, or repo roots implicitly.
- If candidate roots are discovered, report them and wait for approval before reading files.
- Do not persist raw logs or full transcripts into the repo.

## Deterministic Pipeline

Run these phases in order:

1. Scope
   - restate the timeframe, concept query, selected roots, filters, and output limit.
2. Authorize log roots
   - resolve selected roots and verify they exist.
3. Inventory files
   - list candidate session files under selected roots.
   - stable-sort by timestamp/path.
   - filter by timeframe using file metadata only when possible.
   - apply scan budgets before content reads.
4. Parse records
   - stream files line-by-line.
   - parse structured records when available.
   - record parse failures with file, line, and reason.
   - stop with `PARTIAL_SEARCH` if file, byte, or runtime budgets are reached before the search is complete.
5. Normalize timestamps
   - convert record timestamps to the requested timezone.
   - apply the inclusivity rule.
6. Filter source records
   - prefer user-authored message events.
   - exclude subagent dispatch prompts, tool payloads, and copied transcript noise unless the goal requires them.
7. Search concepts
   - treat concept terms as data.
   - use fixed-string matching by default.
   - use regex only when explicitly requested and bounded.
   - keep semantic inference separate from literal matches.
8. Rank evidence
   - rank by direct user instruction, repetition, proximity to the requested repo/project, and stated reason.
   - downgrade temporary tool-use preferences and task-local commands.
9. Emit handoff
   - report counts, selected snippets, statuses, unknowns, and rejected-noise candidates.
   - hand off only summarized, redacted evidence to `governance-learnings-template.md`.

## Terminal States

Use exactly one terminal state:

- `FOUND`: complete search found relevant evidence.
- `NOT_FOUND_AFTER_COMPLETE_SEARCH`: complete search found no relevant evidence.
- `PARTIAL_SEARCH`: limits, inaccessible roots, parse failures, or timeouts prevent complete search.
- `INACCESSIBLE`: selected roots or required files cannot be read.
- `UNPARSEABLE`: session files exist but cannot be parsed enough for reliable review.
- `AMBIGUOUS_TIMEFRAME`: timeframe could not be normalized.

## Required Handoff Fields

- terminal_state:
- candidate_roots:
- selected_roots:
- search_window:
- timezone:
- inclusivity_rule:
- query_terms:
- source_statuses:
- scan_budget:
- per_source_scan_budget:
- files_found:
- files_read:
- bytes_read:
- runtime_seconds:
- budget_limits_hit:
- files_skipped:
- parse_failures:
- records_read:
- user_message_records:
- excluded_records:
- relevant_candidates:
- rejected_noise_candidates:
- packaging_shortlist:
- skipped_or_deferred_packaging_candidates:
- evidence_summary:
- top_ranked_evidence:
- direct_snippets:
- source_confirmation_status:
- unknowns:
- privacy_redactions_applied:
- handoff_target: `docs/agents/playbooks/governance-learnings-template/governance-learnings-template.md`

## Evidence Ranking

Rank high:

- direct user instruction about durable governance behavior
- repeated instruction across sessions/projects
- stated reason tied to SSOT, deterministic behavior, explicit failure, safety, witnesses, or docs routing
- evidence that identifies an existing governance gap or contradiction

Rank low or reject:

- one-off tool usage preference
- temporary budget/thread/speed instruction
- task-local execution instruction
- user frustration without reusable governance implication
- copied agent/subagent output that is not a direct user instruction
- prompt text that conflicts with current `AGENTS.md` authority without explicit request to change that authority

## Privacy Rules

- Redact secrets, tokens, cookies, auth headers, emails, phone numbers, account IDs, and full user-home paths.
- Prefer `<governance-root>`, `<project-root>`, `{HOME}`, or relative paths in output.
- Quote only short snippets needed to prove the finding.
- Do not emit full transcripts.
- Do not create repo-tracked evidence files unless the user explicitly asks and the content is redacted.
- Do not store raw Memories, rollout summaries, Chronicle records, personal administration details, or broad local path inventories in repo artifacts.

## Handoff Rule

This playbook ends after evidence handoff. The receiving governance-learning review must run the Promotion / Noise Gate before any de-duplication, backlog proposal, or governance edit.
