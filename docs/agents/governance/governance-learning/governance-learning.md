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
- Prohibited: inventing a policy to cover missing evidence.
- Candidate wording MUST separate existing obligation, proposal, and illustrative text.
- A draft using MUST remains proposed text until adopted through its owner.
- Priority labels MUST only rank proposals, never signal authority.
- Policy MUST come from evidence, not from popularity.
- This workflow MUST NOT replace the lifecycle or self-authorize edits.
- Raw transcripts MUST NOT enter repository artifacts.

## Candidate definitions

- The Lexicon (ssot) defines learning, governance-level learning, evidence handoff and noise.

## Promotion / Noise gate

- Apply this gate before de-duplication or delta drafting.
- Promotion Required evidence: reusable gap in constitution/lifecycle, SSOT ownership, invariants/witnesses, deterministic checks, authority/docs routing, reusable scaffolds, safety, or explicit outcomes.
- Repetition alone is insufficient.
- One verified critical governance failure qualifies when it shows that gap.
- Each candidate receives exactly one status.

| Gate status | Evidence disposition |
|---|---|
| `PROMOTE_FOR_DEDUP` | Verified governance-level gap. Resolve existing coverage and the owning location. |
| `DEFER_EVIDENCE_GAP` | Plausible concern with a named missing or inaccessible source. |
| `REJECT_TASK_LOCAL` | Applies to one task, repository, file, or temporary goal. |
| `REJECT_TOOL_BUDGET` | Temporary token/time/thread/tool budget without a durable gap. |
| `REJECT_TEMPORARY_EXECUTION_PREFERENCE` | Run-local execution preference. |
| `REJECT_WEAK_EVIDENCE` | Unsupported assertion. |
| `REJECT_CONFLICTS_WITH_SSOT` | Conflicting owner semantics without an authorized owner update. |
| `REJECT_NON_GOVERNANCE` | No governance-level implication. |

- Rejected candidates record evidence and reason, with target and draft delta `N/A + rejected`.
- Rejected candidates get no backlog proposal.
- Deferred candidates Record the missing evidence and next action without a draft delta.

## Coverage and placement evidence

- Resolve the highest owning jurisdiction before drafting any delta.
- Search the supplied bounded scope.
- Record terms, ordering, files/bytes, elapsed cost, termination and coverage.
- An expanded scope MUST have an explicit contract.
- Record `ALREADY_COVERED`, `PARTIAL`, or `MISSING` with owner citation, exact gap, and the matching duplicate removal.

## Evidence output

- Output MUST be a decision brief, candidate records with `GL-DDMMYYYY-###` identifiers, and a summary, in that order, with the fields below in that order.
- Unknown and inapplicable fields retain `Unknown` or `N/A + reason`.
- Candidate count follows the supplied output limit.
- No minimum count forces evidence creation.
- A truncated set is pending, with reason and next action.
- Priority ranks proposals, not obligation strength.
- `P1` MUST have verified evidence plus a concrete command or deterministic manual witness.

| Part | Fields |
|---|---|
| Decision brief | model and scope; SSOT map; authority uplift summary (verified failure classes, earliest defective boundary, prevention point, evidence); proof obligations and verification plan; blast radius; README Checks alignment; verification status per claim; Change Contract owner reference and applicable evidence; authorization and lifecycle evidence reference |
| Candidate record | ID (date from the review context, sequence from `001` in output order); gate status; coverage status `MISSING`, `PARTIAL`, `ALREADY_COVERED`, `DEFERRED`, or `REJECTED`; evidence (R/D); failure mode prevented; authority-first prevention point; target location; draft delta or coverage citation; Change Contract alignment; witness or verification; risk if not addressed; modularity or structure decision; priority `P1`-`P3` with `VERIFIED` or `UNVERIFIED`; remaining action |
| Summary | verified proposals by priority and owner; already-covered candidates and citations; rejected and deferred counts by gate status; routing changes and duplicate removals proposed or verified; unknowns, incomplete evidence, and required actions |
| Session recap (user-supplied source for an `UNVERIFIED` candidate) | work performed; failures and friction with exact redacted messages; workarounds and observed outcomes; decisions made and their sources; repeated confusion points; missing governance support and supporting evidence |

## Session-log evidence acquisition

- Purpose: collect bounded deterministic evidence from authorized session logs for a timeframe and concept.
- Boundary: evidence acquisition only. Promotion, rejection, backlog and edits stay outside it.
- Concept-specific search terms MUST come only from the run's concept query.

### Timeframe rule

- Relative timeframes MUST normalize to absolute timestamps in the requested timezone before scanning.
- The end timestamp is exclusive unless the user requests otherwise.
- For all-available history (Lexicon (ssot)), broad `{HOME}` or unapproved sources are Prohibited.
- Non-deterministic normalization MUST stop with `AMBIGUOUS_TIMEFRAME`.

### Source status

- Record one status per source: `available_authorized`, `unavailable`, `skipped_unauthorized`, or `partial`.
- Authorized sources not fully searched MUST feed `PARTIAL_SEARCH` or an explicit `unknowns` entry.
- Discovery-only evidence MUST stay below high confidence until the source system confirms it.

### Packaging form

- `skill`: a repeated, well-bounded workflow warranting a new bundle.
- `extend_existing`: an existing asset already covers most of it.
- `hook`: the obligation needs deterministic enforcement.
- `subagent`: an active project-local subagent owner exists.
- `skip`: one-off, sensitive, weakly evidenced, already-covered, or unsupported candidate.
- `defer`: needs more evidence, owner confirmation, or source-system verification.

### Root authorization

- Use only user-provided or user-approved log roots.
- Resolve each root to an absolute path before scanning.
- Reject traversal outside selected roots.
- Authorized roots need no duplicate approval (FP-30).
- Raw logs and full transcripts MUST stay out of the repo.

### Acquisition result states

- Return exactly one state in `terminal_state` (FP-29).
- `FOUND`: complete search found relevant evidence.
- `NOT_FOUND_AFTER_COMPLETE_SEARCH`: complete search found no relevant evidence.
- `PARTIAL_SEARCH`: limits, inaccessible roots, parse failures, or timeouts prevented completion.
- `INACCESSIBLE`: selected roots or required files cannot be read.
- `UNPARSEABLE`: session files exist but cannot be parsed reliably.
- `AMBIGUOUS_TIMEFRAME`: timeframe could not be normalized.

### Privacy rules

- Apply redaction to every snippet, path, and handoff value.
- Quote only short snippets that prove the finding, never a full transcript.
- Repo-tracked evidence files MUST have an explicit user request and redacted content.
- MUST store none of these: raw memories, rollout summaries, discovery-only records, personal administration details, broad path inventories.

### Handoff rule

- Acquisition ends at handoff.
- The receiving review MUST run the promotion gate before de-duplication, backlog or edits.
