---
doc_type: playbook
ssot_owner: AGENTS.md
update_trigger: governance-learning promotion gate, evidence fields, or prompt scaffold changes
---

# Playbook - Governance Learnings (Session -> Governance Deltas)

This playbook owns candidate promotion/noise classification, evidence records, and the prompt scaffold for explicitly invoked governance-learning work. `AGENTS.md` owns Fundamental Principles and the Governance Auto-Edit Gate. `Orchestration.md` owns agent roles, review, authorization, execution, and terminal decisions. This procedure supplies evidence to that lifecycle.

## Applicability and proposal language

Use this explicitly invoked playbook for a session-evidenced reusable governance gap. A missing required observation remains `UNVERIFIED` with a request for the named source or the Session recap schema; it does not justify inventing a policy. Supported candidates remain independently assessable under Inputs and authority.

Candidate wording MUST distinguish an existing binding obligation (owner citation), a proposed owner change (clearly labeled proposal), and illustrative text. `AGENTS.md` Instruction Derivation Gate owns obligation strength; a draft using MUST is still proposed text until adopted through that owner. Priority labels rank proposals and MUST NOT imply authority. This playbook does not create a policy from popularity, replace the lifecycle, or authorize edits.

## Inputs and authority

- Review goal and supplied session evidence or redacted evidence handoff.
- Candidate output limit and bounded search scope/budget supplied by the active workflow.
- Authorization witness determined under `AGENTS.md` and `Orchestration.md`.
- Governance authority routes resolved through `agents-manifest.yaml` by its declared role.
- Docs placement and promotion owner: `docs/agents/25-docs-ssot-policy/docs-ssot-policy.md`.
- Local session-log acquisition owner: `codex-session-log-review.md`.

If evidence needed for a candidate is missing, record `UNVERIFIED` and the exact missing source. A user recap can supply that source using the schema below. Missing irrelevant history does not block supported candidates. Raw transcripts, credentials, personal identifiers, and full user-home paths are not repository artifacts; evidence output uses the redaction owner `docs/agents/30-logging-errors/logging-errors.md`.

## Candidate definitions

- Learning: an evidenced recurring pitfall, missing invariant/witness, missing owner, or routing/template defect with a concrete prevention point.
- Governance-level learning: a learning that changes reusable governance behavior across tasks or repositories.
- Evidence handoff: summarized observations supporting classification; it has no governance or execution authority.
- Noise: task-local or temporary preference, weak evidence, or unrelated material that does not justify a governance owner update.

## Promotion / Noise Gate

Apply this gate before de-duplication or drafting deltas. Promotion requires verified evidence of a reusable gap in the constitution/lifecycle, SSOT ownership, invariants/witnesses, deterministic checks, authority/docs routing, reusable scaffolds, safety, or explicit outcomes. Repetition alone is insufficient; a single verified critical governance failure qualifies when it demonstrates that gap.

Each candidate receives exactly one status:

| Gate status | Evidence disposition |
|---|---|
| `PROMOTE_FOR_DEDUP` | Verified governance-level gap; resolve existing coverage and owning location. |
| `DEFER_EVIDENCE_GAP` | Plausible governance concern with a named missing/inaccessible source. |
| `REJECT_TASK_LOCAL` | Applies only to one task, repository, file, or temporary goal. |
| `REJECT_TOOL_BUDGET` | Temporary token/time/thread/tool budget without a durable governance gap. |
| `REJECT_TEMPORARY_EXECUTION_PREFERENCE` | Run-local execution preference. |
| `REJECT_WEAK_EVIDENCE` | Unsupported assertion. |
| `REJECT_CONFLICTS_WITH_SSOT` | Conflicting owner semantics without an authorized owner update under `AGENTS.md` and `Orchestration.md`. |
| `REJECT_NON_GOVERNANCE` | No governance-level implication. |

Rejected candidates retain evidence and reason, with target and draft delta `N/A + rejected`; they do not produce backlog proposals. Deferred candidates retain the missing evidence and next action without a draft delta.

## Coverage and placement evidence

For each promoted candidate:

1. Resolve the highest owning jurisdiction using `AGENTS.md` FP-04, FP-08, FP-12, and FP-27.
2. Search the supplied bounded governance/owner scope under FP-26; record terms, ordering, files/bytes, elapsed cost, termination, and coverage. Expanded scope requires the active workflow's explicit contract.
3. Record `ALREADY_COVERED`, `PARTIAL`, or `MISSING` with the owner citation and exact gap. Repeated lookups use the keyed evidence record under FP-28.
4. Record the owner replacement/extension and corresponding duplicate removal under FP-09. Route project-local durable facts through the docs SSOT policy; do not keep a second placement matrix here.
5. Supply candidate evidence to the review/execution assignment determined by `Orchestration.md`. The authorization witness determines proposals versus authorized edits under the Governance Auto-Edit Gate.

## Evidence output contract

Use a decision brief, candidate records, then summary. Field order below is the output contract; unknown and inapplicable fields retain `Unknown` or `N/A + reason`. Candidate count follows the supplied output limit; no minimum pressures evidence creation. Any truncated candidate set is pending with reason and next action under FP-29.

### Decision brief

- Model and scope:
- SSOT map:
- Authority uplift summary: verified failure classes, earliest defective boundary, prevention point, and evidence:
- Proof obligations and verification plan:
- Blast radius:
- README Checks alignment:
- Claim-level verification status:
- Change Contract owner reference and applicable evidence:
- Authorization and lifecycle evidence reference:

### Candidate record

- ID: `GL-DDMMYYYY-###`; date from the explicit review context, sequence starts at `001` and increments in output order.
- Gate status:
- Status: `MISSING` | `PARTIAL` | `ALREADY_COVERED` | `DEFERRED` | `REJECTED`
- Evidence (R/D):
- Failure mode prevented:
- Authority-first prevention point:
- Target location:
- Draft delta or coverage citation:
- Change Contract alignment:
- Witness/verification:
- Risk if not addressed:
- Modularity/structure decision:
- Priority and confidence: `P1` | `P2` | `P3`, with `VERIFIED` | `UNVERIFIED`
- Remaining action:

Priority ranks proposals, not obligation strength. P1 requires verified evidence and a concrete verification command or deterministic manual witness. Drafts remain proposals until applied through their owning authority.

### Summary

- Verified proposals by priority and owner.
- Already-covered candidates and citations.
- Rejected/deferred counts by gate status.
- Routing changes and duplicate removals proposed or verified.
- Unknowns, incomplete evidence, and required actions.

## Prompt scaffold

```text
Apply `AGENTS.md` and `Orchestration.md` to this explicitly invoked governance-learning review. Use `docs/agents/playbooks/governance-learnings-template/governance-learnings-template.md` for the promotion gate and evidence output contract; it does not replace those owners.

Complete controlling request and earlier binding decisions:
<retain all binding intent>

Review goal:
<desired reusable improvement>

Evidence or handoff:
<redacted evidence with provenance; Unknown if missing>

Authorized source/search scope and budgets:
<explicit sources, bounds, ordering, and termination contract>

Candidate output limit:
<run-supplied limit>

Authorization witness:
<current scope and side effects determined through the owners>

Requested evidence output:
<decision brief, candidate records, summary under the playbook contract>

Apply the playbook Evidence output contract in its declared field order. Fill every field; preserve Unknown or N/A + reason. For each candidate connect the observed R/D evidence, proposed S invariant, prevention point, witness, target owner and exact replacement/extension. Apply Promotion / Noise Gate before Coverage and placement evidence; rejected/deferred candidates retain their reason and next action without a draft delta.

If a required source is inaccessible, name the missing source and use the Session recap schema for the affected candidate. Distinguish missing evidence from irrelevant history. Record the bounded search witness and exact owner coverage before calling anything MISSING. Supply proposed or authorized changes only within the recorded authorization and lifecycle evidence.
```

## Miniature application example (illustrative)

A redacted run report shows an owned output path was overwritten before validation; a failure fixture reproduces it. The candidate record identifies that observation as R/D, the existing I/O owner as the prevention point, and preservation of the original on failed validation as the proposed S witness. If bounded coverage finds that the owner already prohibits this, classify `ALREADY_COVERED` and cite it: the remaining action is implementation correction in that jurisdiction, not another governance rule. A popularity claim without the run evidence remains `UNVERIFIED`; it cannot substitute for this witness.

## Session recap schema

- Work performed:
- Failures/friction encountered, with exact redacted messages:
- Workarounds used and observed outcomes:
- Decisions made and their sources:
- Repeated confusion points:
- Missing governance support and supporting evidence:
