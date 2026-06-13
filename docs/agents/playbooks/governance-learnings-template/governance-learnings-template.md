---
doc_type: playbook
ssot_owner: AGENTS.md
update_trigger:
  - governance learning capture procedure change
  - output expectations change
---

# Playbook - Governance Learnings (Session -> Governance Deltas)

## Purpose
Use this playbook to have an AI assistant review a work session and extract repeatable governance learnings that should be codified into the governance pack, while avoiding duplication and staying aligned with SSOT boundaries.

## Use when
- You want an AI assistant to review a work session and extract learnings that should be codified into this governance pack.
- You want the assistant to propose or (when explicitly authorized) apply governance updates while avoiding duplicates.

## Don't use when
- You do not have (or cannot provide) session evidence (transcript/recap/diffs/logs).
- You want new governance policy invented from scratch without evidence.

## Definitions
- Learning: a repeatable pitfall, missing invariant, missing witness/check, missing SSOT owner, missing template, or missing injection profile that would prevent future errors if codified.
- Governance-level learning: a learning that changes reusable agent behavior across tasks/repos because it affects `AGENTS.md` hard gates, SSOT owners, invariants, witnesses, manifest routing, docs routing, safety, deterministic checks, or reusable governance playbooks.
- Evidence handoff: a bounded, redacted summary of session evidence. It can support promotion decisions, but it is not itself a governance delta.
- Noise: task-local, tool-budget, temporary execution preference, weak-evidence, or non-governance instruction that should not create a governance update.

## Quickstart checklist (recommended)
1. Confirm required context is accessible:
   - Read `AGENTS.md`.
   - Resolve the current task routing from `agents-manifest.yaml`.
   - Read the routed owner docs and record the manifest-resolution witness.
2. Confirm whether governance auto-edit is authorized for this session.
3. Collect evidence inputs; if none are available, request a Session Recap using the schema in this file.

## Authority References
- Global hard gates, council requirements, and governance auto-edit rules are owned by `AGENTS.md`.
- Context-routing facts are owned by `agents-manifest.yaml`; this playbook must not keep a local injected-doc list.
- Docs placement, router behavior, and non-owner-doc limits are owned by `docs/agents/25-docs-ssot-policy/docs-ssot-policy.md`.
- This playbook owns the promotion/noise gate, evidence record shape, and copy/paste prompt scaffold for governance-learning work.

## Language discipline
- Use `MUST` / `Hard Gate` only when quoting requirements explicitly hard-gated in `AGENTS.md`.
- Use `must` / `required` for playbook procedure steps.
- Use `should` / `recommended` for suggestions and preferences.
- Use `P1` / `P2` / `P3` for proposal priority labels (do not use `MUST` as a priority label).

## Procedure guardrails
- Before claiming something is "missing", verify it does not already exist (search the repo with `rg`).
- If auto-edit is not authorized by the user/session policy, propose deltas only.
- If any required file is inaccessible, stop and request it.
- If council output is `go_no_go = hold`, stop before editing.
- If council conflicts or evidence gaps remain unresolved, stop and ask before editing.
- If evidence is weak or missing for a candidate, mark it `UNVERIFIED` and request recap/context.
- Prefer user-provided recap or redacted evidence handoff over raw transcripts.
- Do not store raw session transcripts, raw local session logs, secrets, cookies, credentials, personal identifiers, or full user-home paths in repo artifacts.
- Redact sensitive evidence before output; use counts, timestamps, session IDs, hashes, relative paths, and short snippets only when needed.

## Promotion / Noise Gate

Run this gate before de-duplication and before drafting any governance delta.

Promote a candidate to de-duplication only when verified evidence shows a reusable governance gap affecting one or more of:

- `AGENTS.md` hard gates or execution loops
- SSOT ownership, authority boundaries, or duplicate-authority prevention
- invariants, witnesses, deterministic checks, or README Checks alignment
- manifest/context injection routing
- docs routing, playbook structure, or governance template behavior
- safety, resource cleanup, explicit failure, or no-silent-skip behavior
- repeatable cross-repo agent behavior that future agents must preserve

Repetition is useful evidence, but it is not sufficient by itself. A single verified critical governance failure may promote. Repeated task-local preferences must still be rejected.

Use these gate statuses:

- `PROMOTE_FOR_DEDUP`: verified governance-level candidate; continue to de-duplication and placement.
- `DEFER_EVIDENCE_GAP`: plausible governance concern, but evidence is incomplete or inaccessible.
- `REJECT_TASK_LOCAL`: applies only to one task, repo, file, or temporary user goal.
- `REJECT_TOOL_BUDGET`: concerns token/time/thread/tool budgeting rather than durable governance behavior.
- `REJECT_TEMPORARY_EXECUTION_PREFERENCE`: temporary instruction for the current run, not a reusable rule.
- `REJECT_WEAK_EVIDENCE`: assertion lacks enough verified evidence to affect governance.
- `REJECT_CONFLICTS_WITH_SSOT`: conflicts with current `AGENTS.md` or another authority unless the user explicitly requests an authority change and confirmation/council gates pass.
- `REJECT_NON_GOVERNANCE`: does not affect governance-level authority, invariants, witnesses, routing, safety, or checks.

Rejected candidates must include evidence, gate status, and rejection reason. They must not emit draft governance deltas, backlog proposals, or target locations beyond `N/A + rejected`.

For project-local bounded authority memory, place promoted records through `docs/agents/25-docs-ssot-policy/docs-ssot-policy.md` and scaffold any missing project-doc shape with `docs/agents/playbooks/project-docs-template/project-docs-template.md`. This playbook records only the selected owner path, promotion evidence, and reason; it does not maintain a local placement matrix.

Example rejection:

- Candidate: "do not let subagents spawn more subagents"
- Gate status: `REJECT_TEMPORARY_EXECUTION_PREFERENCE` or `REJECT_CONFLICTS_WITH_SSOT`
- Reason: task-local execution preference and/or conflict with `AGENTS.md` standing subagent authorization unless the user explicitly asks to revise that authority and required confirmation/council gates pass.

## Preflight checklist (required before Step 1)
- AGENTS access confirmed.
- Manifest routing resolved and injected files read.
- Auto-edit authorization status known.

## Severity rubric (for council findings)
- `HIGH`: blocker risk that can cause incorrect governance edits, policy drift, or unsafe execution sequence.
- `MEDIUM`: likely misuse or rework risk that is non-blocking with explicit controls.
- `LOW`: clarity/compliance improvement with low immediate execution risk.

## Procedure
1. Extract candidate learnings from session evidence or an evidence handoff.
2. Run the Promotion / Noise Gate; reject non-governance noise before de-duplication.
3. De-duplicate promoted candidates against governance docs and referenced SSOT owners before declaring `MISSING`.
4. Run Council review and reconcile findings before any edits.
5. Produce governance deltas (proposals or auto-edits, based on authorization).
6. Emit deterministic output records in required field order.
7. Publish final summary with P1/P2/P3 split, rejected noise counts, and explicit unknowns.

## Prompt pack (copy/paste into any chat)

```text
Hard gates (copy/paste scaffold sourced from AGENTS.md):
- Read and follow `AGENTS.md`; if it is inaccessible, request it before doing any work.
- Execute the `AGENTS.md` Context Injection Procedure using the current `agents-manifest.yaml`.
- Execute the docs-first authority gate before any non-trivial plan, review, council output, implementation, or repo mutation.
- For governance auto-edit, apply the `AGENTS.md` Governance Auto-Edit Gate and Subagent Council before editing.
- Derive task instructions from declared SSOT owners; if ownership is unknown or conflicting, stop and report the authority gap before acting.
- Use docs placement and router rules from `docs/agents/25-docs-ssot-policy/docs-ssot-policy.md`; do not restate them here.

Task type: governance_improvement

Goal:
- Scrutinize this session (and any referenced repo files) to extract governance learnings that should be codified, then propose or apply updates when authorized.

Field completion rule:
- Fill every required field. If information is missing, write `Unknown` or `N/A + reason` (do not omit fields).

Preflight checklist (required before Step 1):
- AGENTS access confirmed.
- Manifest routing resolved and injected files read.
- Auto-edit authorization status known.

Evidence inputs (provide if available; if none, write `None provided`):
- Session transcript or recap
- Session evidence handoff from the relevant evidence-collection playbook
- Files changed and diffs
- Commands run + outputs
- Error messages/logs
- Decisions that caused rework
- Sanitize secrets/PII in pasted evidence.

If you cannot see the full session history:
- Ask me for a "Session Recap" using this schema:
  - Work performed:
  - Failures/friction encountered (exact messages if any):
  - Workarounds used:
  - Decisions made:
  - Repeated confusion points:
  - What I wish had existed in governance beforehand:
- Wait for the recap before continuing.

Required repo context (read at minimum):
- `AGENTS.md`
- Current routing from `agents-manifest.yaml`.
- Files injected by the matched profile or fallback routing.
- Any owner docs referenced by candidate evidence.
- If a required file is inaccessible (permissions/tooling), stop and request it; do not infer missing contents.
- If a required file is truly missing and `AGENTS.md` requires creation, create it only in authorized proposal/auto-edit flow.

Decision-grade brief (required before learnings; use this exact label order):
- Model:
- SSOT map:
- Authority uplift summary:
  - Failure class 1 (VERIFIED|UNVERIFIED):
    - Earliest authority/contract boundary:
    - Authority-first prevention point:
    - Evidence/heuristic:
  - Failure class 2 (VERIFIED|UNVERIFIED):
    - Earliest authority/contract boundary:
    - Authority-first prevention point:
    - Evidence/heuristic:
  - Failure class 3 (VERIFIED|UNVERIFIED):
    - Earliest authority/contract boundary:
    - Authority-first prevention point:
    - Evidence/heuristic:
  - Deprioritized classes (if any):
  - Reconciliation note after Step 5:
- Proof obligations + verification plan:
- Blast radius summary (workflows/docs/tools/agents impacted):
- Verification SSOT alignment (commands from README.md "Checks"; note gaps requiring README updates or manual checks):
- Confidence gate summary (claim-level VERIFIED/UNVERIFIED status):
- Change Contract alignment (map to `AGENTS.md` template sections; do not duplicate full contract):

Council summary block (required before Step 4; follow `AGENTS.md` "Subagent Council (Hard Gate)"):
- council_run_id:
- phase (`pre_change` | `post_change`):
- intent_coverage (`ssot_duplication`, `silent_error`, `edge_case`, `resource_security_perf`):
- reviewers (id, role, scope):
- findings (severity, location, issue, evidence, recommendation):
- conflicts:
- reconciliation_decision:
- residual_risks:
- go_no_go (`go` | `hold`):
- verification_links:
- profile_doc_coverage (when `AGENTS.md` Profile-Aware Context Coverage applies):

Severity rubric (for findings):
- HIGH: blocker risk that can cause incorrect governance edits, policy drift, or unsafe execution sequence.
- MEDIUM: likely misuse or rework risk that is non-blocking with explicit controls.
- LOW: clarity/compliance improvement with low immediate execution risk.

Promotion / Noise Gate (required before de-duplication):
- Promote only verified governance-level candidates affecting `AGENTS.md` hard gates, SSOT owners, invariants, witnesses, manifest routing, docs routing, safety, deterministic checks, or reusable governance playbooks.
- Repetition is not sufficient by itself; a single verified critical governance failure may promote.
- Reject task-local, tool-budget, temporary execution preference, weak-evidence, conflicting-with-SSOT, and non-governance items.
- Use one of these gate statuses: `PROMOTE_FOR_DEDUP`, `DEFER_EVIDENCE_GAP`, `REJECT_TASK_LOCAL`, `REJECT_TOOL_BUDGET`, `REJECT_TEMPORARY_EXECUTION_PREFERENCE`, `REJECT_WEAK_EVIDENCE`, `REJECT_CONFLICTS_WITH_SSOT`, `REJECT_NON_GOVERNANCE`.
- Rejected candidates must include evidence and reason, use `Target location: N/A + rejected`, and must not emit draft governance deltas or backlog proposals.
- Example rejection: "do not let subagents spawn more subagents" is `REJECT_TEMPORARY_EXECUTION_PREFERENCE` or `REJECT_CONFLICTS_WITH_SSOT` unless the user explicitly requests an authority change and confirmation/council gates pass.

Steps:
1) Extract candidate learnings (0-15):
   - If fewer than 5 VERIFIED candidates exist, continue with available candidates and state shortfall + reason.
   - Each candidate must include:
     - Evidence from this session (tag as R or D; R = runtime truth, D = recorded truth)
     - Failure mode prevented
     - Proposed invariant (S; one sentence, testable) + category (data, ordering, atomicity, idempotency, lifecycle, observability, other)
     - Proposed witness (what is measured, where recorded, pass criteria)
   - If evidence is weak, mark as UNVERIFIED and request additional context.
2) Apply the Promotion / Noise Gate:
   - Assign exactly one gate status to each candidate.
   - Continue only `PROMOTE_FOR_DEDUP` candidates to Step 3.
   - Keep `DEFER_EVIDENCE_GAP` and rejected candidates in output records without draft deltas.
3) De-duplicate and place (verify):
   - For each candidate, search in this order:
     1. governance/playbooks/docs area
     2. referenced SSOT owner docs/files
     3. broader repo
   - Use `rg` for verification and record search terms used when practical.
   - Mark status as `ALREADY_COVERED`, `PARTIAL`, or `MISSING`.
4) Council review (required before edits):
   - Run the Subagent Council per `AGENTS.md` "Subagent Council (Hard Gate)" with minimum intention coverage (SSOT/duplication, silent-error scan, edge-case scan, resource/security/perf).
   - Merge findings into one council summary block using the required fields above.
   - For each HIGH/MEDIUM finding, include at least one evidence item (R or D) and one action (apply/defer + rationale).
   - If `go_no_go` is `hold`, stop and ask before editing.
   - If conflicts or gaps remain, pause and ask before editing.
5) Produce governance deltas (proposals or auto-edits, depending on authorization):
   - If auto-edit is authorized: apply minimal edits after the confirmation gate and within the scope in `AGENTS.md` "Governance Auto-Edit Gate".
   - If auto-edit is not authorized: propose deltas only.
6) Output records (deterministic; one record per candidate, exact field order):
   - ID:
   - Gate status:
   - Status (`MISSING`|`PARTIAL`|`ALREADY_COVERED`|`DEFERRED`|`REJECTED`):
   - Evidence (R/D):
   - Failure mode prevented:
   - Authority-first prevention point:
   - Target location:
   - Draft delta (for `MISSING`/`PARTIAL`) or coverage citation (for `ALREADY_COVERED`):
   - Change Contract alignment:
   - Witness/verification:
   - Risk if not addressed:
   - Modularity/structure decision:
   - Priority + confidence (`P1`|`P2`|`P3` + `VERIFIED`|`UNVERIFIED`):
   - If a field is not applicable, write `N/A + reason`.
   - Rejected candidates must use `Target location: N/A + rejected` and `Draft delta: N/A + rejected`.
   - ID format rule: `GL-DDMMYYYY-###`
   - Increment rule: `###` starts at `001` within the session output and increments by 1 for each record.
7) Final summary:
   - P1 codify now (max 7; requires VERIFIED evidence + concrete verification command/manual check)
   - P2/P3 backlog
   - Already-covered (no action)
   - Rejected noise by gate status
   - Manifest/injection improvements (if any)
   - Open questions/unknowns
   - UNVERIFIED items cannot be promoted as P1.

Output format:
- Markdown
- Short bullets and small tables
- Section order: Decision-grade brief -> Output records -> Final summary
- Each learning must be actionable: where to change + what to add + how to verify
```

## Suggested de-dup search approach (recommended)
When you reach Step 2, use this sequence:
1. Search governance/playbooks/docs area first.
2. Search referenced SSOT owner docs/files next.
3. Broaden to the whole repo only if needed.

Record the exact `rg` search terms used in candidate evidence notes when practical.

## Session Recap schema (for users)
- Work performed:
- Failures/friction encountered (exact messages if any):
- Workarounds used:
- Decisions made:
- Repeated confusion points:
- What I wish had existed in governance beforehand:

## Output record example (filled; illustrative/non-authoritative)
- ID: GL-10022026-001
- Status (`MISSING`|`PARTIAL`|`ALREADY_COVERED`): PARTIAL
- Evidence (R/D): D - Session transcript showed repeated omission of hard gates when users copied an incomplete prompt skeleton.
- Failure mode prevented: Governance updates run without required hard-gate constraints due to non-self-contained prompt reuse.
- Authority-first prevention point: `docs/agents/playbooks/governance-learnings-template/governance-learnings-template.md` prompt pack owner.
- Target location: `docs/agents/playbooks/governance-learnings-template/governance-learnings-template.md`
- Draft delta (for `MISSING`/`PARTIAL`) or coverage citation (for `ALREADY_COVERED`): Replace prompt skeleton with a self-contained prompt pack that uses a minimal AGENTS-sourced scaffold and playbook-owned preflight fields.
- Change Contract alignment: `AGENTS.md` template sections B (invariants), C (witnesses), D (authority impact), H (verification checklist).
- Witness/verification: `python3 scripts/check_governance_core/check_governance_core_main.py` passes; manual witness confirms prompt pack keeps only the minimal AGENTS-sourced scaffold needed for copy/paste execution.
- Risk if not addressed: Repeated governance drift and skipped council/confirmation gate steps.
- Modularity/structure decision: Keep playbook as single authority document; avoid creating parallel prompt docs.
- Priority + confidence (`P1`|`P2`|`P3` + `VERIFIED`|`UNVERIFIED`): P1 + VERIFIED

## Non-goals
- This playbook is not a replacement for `AGENTS.md`.
- This playbook does not define new SSOT owners.
- This playbook does not authorize governance auto-edits outside existing `AGENTS.md` gates.
