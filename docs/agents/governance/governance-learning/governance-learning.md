---
doc_type: playbook
ssot_owner: docs/agents/governance/governance-learning/governance-learning.md
update_trigger: promotion gate, evidence output shape, or acquisition contract changes
---

# Governance Learning

Jurisdiction: session-evidenced governance-learning candidates, their promotion gate, evidence output, and bounded session-log evidence acquisition.

## Applicability and proposal language

- Use only when explicitly invoked for a session-evidenced reusable governance gap.
- A missing required observation MUST return `UNVERIFIED` plus the named missing source.
- Missing evidence MUST NOT justify inventing a policy.
- Candidate wording MUST separate existing obligation, proposal, and illustrative text.
- A draft using MUST remains proposed text until adopted through its owner.
- Priority labels rank proposals; they MUST NOT imply authority.
- Prohibited: policy from popularity, replacing the lifecycle, self-authorizing edits.
- Raw transcripts MUST NOT enter repository artifacts.

## Candidate definitions

- Learning: evidenced recurring pitfall, missing invariant/witness, missing owner, or routing or template defect with a concrete prevention point.
- Governance-level learning: a learning that changes reusable governance behavior across tasks or repositories.
- Evidence handoff: summarized observations supporting classification; no governance or execution authority.
- Noise: task-local or temporary preference, weak evidence, or unrelated material.

## Promotion / Noise gate

- Apply this gate before de-duplication or delta drafting.
- Promotion Required evidence: reusable gap in constitution/lifecycle, SSOT ownership, invariants/witnesses, deterministic checks, authority/docs routing, reusable scaffolds, safety, or explicit outcomes.
- Repetition alone is insufficient; one verified critical governance failure qualifies when it shows that gap.
- Each candidate receives exactly one status.

| Gate status | Evidence disposition |
|---|---|
| `PROMOTE_FOR_DEDUP` | Verified governance-level gap; resolve existing coverage and owning location. |
| `DEFER_EVIDENCE_GAP` | Plausible concern with a named missing or inaccessible source. |
| `REJECT_TASK_LOCAL` | Applies to one task, repository, file, or temporary goal. |
| `REJECT_TOOL_BUDGET` | Temporary token/time/thread/tool budget without a durable gap. |
| `REJECT_TEMPORARY_EXECUTION_PREFERENCE` | Run-local execution preference. |
| `REJECT_WEAK_EVIDENCE` | Unsupported assertion. |
| `REJECT_CONFLICTS_WITH_SSOT` | Conflicting owner semantics without an authorized owner update. |
| `REJECT_NON_GOVERNANCE` | No governance-level implication. |

- Rejected candidates Record evidence and reason with target and draft delta `N/A + rejected`; no backlog proposal.
- Deferred candidates Record the missing evidence and next action without a draft delta.

## Coverage and placement evidence

- Resolve the highest owning jurisdiction before drafting any delta.
- Search the supplied bounded scope and Record terms, ordering, files/bytes, elapsed cost, termination, and coverage; expanded scope MUST have an explicit contract.
- Record `ALREADY_COVERED`, `PARTIAL`, or `MISSING` with owner citation, exact gap, and the matching duplicate removal.

## Evidence output

- Output MUST be a decision brief, candidate records with `GL-DDMMYYYY-###` identifiers, and a summary, in that order.
- Unknown and inapplicable fields retain `Unknown` or `N/A + reason`.
- Candidate count follows the supplied output limit; no minimum forces evidence creation.
- Priority ranks proposals, not obligation strength.
- `P1` MUST have verified evidence plus a concrete command or deterministic manual witness.

## Session-log evidence acquisition

- Purpose: collect bounded deterministic evidence from authorized session logs for a timeframe and concept.
- Boundary: evidence acquisition only; promotion, rejection, backlog, and edits stay outside it.
- Prohibited: concept-specific search terms stored here; the run supplies the concept query.

### Timeframe rule

- Relative timeframes MUST normalize to absolute timestamps in the requested timezone before scanning.
- The end timestamp is exclusive unless the user requests otherwise.
- All-available-history means the inventory inside authorized roots only; broad `{HOME}` or unapproved sources are Prohibited.
- Non-deterministic normalization MUST stop with `AMBIGUOUS_TIMEFRAME`.

### Source status

- Record one status per source: `available_authorized`, `unavailable`, `skipped_unauthorized`, or `partial`.
- Authorized sources not fully searched MUST feed `PARTIAL_SEARCH` or an explicit `unknowns` entry.
- Discovery-only evidence MUST NOT reach high confidence before source-system confirmation.

### Packaging form

- `skill`: a repeated, well-bounded workflow warranting a new bundle.
- `extend_existing`: an existing asset already covers most of it.
- `hook`: the obligation needs deterministic enforcement.
- `subagent`: an active project-local subagent owner exists.
- `skip`: one-off, sensitive, weakly evidenced, already-covered, or unsupported candidate.
- `defer`: needs more evidence, owner confirmation, or source-system verification.

### Root authorization

- Use only user-provided or user-approved log roots; resolve each to an absolute path before scanning.
- Reject traversal outside selected roots.
- Authorized roots need no duplicate approval.
- Persisting raw logs or full transcripts into the repo is Prohibited.

### Acquisition result states

- Return exactly one in `terminal_state`.
- `FOUND`: complete search found relevant evidence.
- `NOT_FOUND_AFTER_COMPLETE_SEARCH`: complete search found no relevant evidence.
- `PARTIAL_SEARCH`: limits, inaccessible roots, parse failures, or timeouts prevented completion.
- `INACCESSIBLE`: selected roots or required files cannot be read.
- `UNPARSEABLE`: session files exist but cannot be parsed reliably.
- `AMBIGUOUS_TIMEFRAME`: timeframe could not be normalized.

### Privacy rules

- Apply redaction to every snippet, path, and handoff value.
- Quote only short snippets that prove the finding; emitting full transcripts is Prohibited.
- Repo-tracked evidence files MUST have an explicit user request and redacted content.
- Storing raw memories, rollout summaries, discovery-only records, personal administration details, or broad path inventories is Prohibited.

### Handoff rule

- Acquisition ends at handoff; the receiving review MUST run the promotion gate before de-duplication, backlog, or edits.
