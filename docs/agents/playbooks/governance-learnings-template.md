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
- You want an AI assistant (Claude/Codex/Copilot/etc.) to review a work session and extract learnings that should be codified into this governance pack.
- You want the assistant to propose or (when explicitly authorized) apply governance updates while avoiding duplicates.

## Don't use when
- You do not have (or cannot provide) session evidence (transcript/recap/diffs/logs).
- You want new governance policy invented from scratch without evidence.

## Definitions
- Learning: a repeatable pitfall, missing invariant, missing witness/check, missing SSOT owner, missing template, or missing injection profile that would prevent future errors if codified.

## Quickstart checklist (recommended)
1. Confirm required context is accessible:
   - `AGENTS.md`
   - `agents-manifest.yaml`
   - `docs/agents/index.md`
   - `docs/agents/20-sources-of-truth-map.md`
   - `docs/agents/25-docs-ssot-policy.md`
   - `docs/project/learning.md`
   - plus injected docs/playbooks from the manifest (or `fallback_inject` if no profiles match)
2. Confirm whether governance auto-edit is authorized for this session.
3. Collect evidence inputs; if none are available, request a Session Recap using the schema in this file.

## Hard gates (canonical; keep wording in sync)
- Read and follow `AGENTS.md` (SSOT). If you cannot access it, request it before doing any work.
- Follow `AGENTS.md` "Context Injection Procedure (Hard Gate)" (consult `agents-manifest.yaml`, load injected docs/playbooks).
- Auto-edit is allowed only when this playbook is explicitly invoked (see `AGENTS.md` "Governance Auto-Edit + Council Review").
- Before any edit: run the Council Review step and apply the confirmation gate from `AGENTS.md`.
- Follow `docs/agents/25-docs-ssot-policy.md` (docs cannot become a second SSOT).

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

## Preflight checklist (required before Step 1)
- AGENTS access confirmed.
- Context injection executed per `AGENTS.md`.
- Auto-edit authorization status known.

## Severity rubric (for council findings)
- `HIGH`: blocker risk that can cause incorrect governance edits, policy drift, or unsafe execution sequence.
- `MEDIUM`: likely misuse or rework risk that is non-blocking with explicit controls.
- `LOW`: clarity/compliance improvement with low immediate execution risk.

## Procedure
1. Extract candidate learnings from session evidence.
2. De-duplicate against governance docs and referenced SSOT owners before declaring `MISSING`.
3. Run Council review and reconcile findings before any edits.
4. Produce governance deltas (proposals or auto-edits, based on authorization).
5. Emit deterministic output records in required field order.
6. Publish final summary with P1/P2/P3 split and explicit unknowns.

## Prompt pack (copy/paste into any chat)

```text
Hard gates:
- Read and follow `AGENTS.md` (SSOT). If you cannot access it, request it before doing any work.
- Follow `AGENTS.md` "Context Injection Procedure (Hard Gate)" (consult `agents-manifest.yaml`, load injected docs/playbooks).
- Auto-edit is allowed only when this playbook is explicitly invoked (see `AGENTS.md` "Governance Auto-Edit + Council Review").
- Before any edit: run the Council Review step and apply the confirmation gate from `AGENTS.md`.
- Follow `docs/agents/25-docs-ssot-policy.md` (docs cannot become a second SSOT).

Task type: governance_improvement

Goal:
- Scrutinize this session (and any referenced repo files) to extract governance learnings that should be codified, then propose or apply updates when authorized.

Field completion rule:
- Fill every required field. If information is missing, write `Unknown` or `N/A + reason` (do not omit fields).

Preflight checklist (required before Step 1):
- AGENTS access confirmed.
- Context injection executed per `AGENTS.md`.
- Auto-edit authorization status known.

Evidence inputs (provide if available; if none, write `None provided`):
- Session transcript or recap
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
- `agents-manifest.yaml`
- `docs/agents/index.md`
- `docs/agents/20-sources-of-truth-map.md`
- `docs/agents/25-docs-ssot-policy.md`
- `docs/project/learning.md`
- Plus any injected docs/playbooks per the manifest (or `fallback_inject` if no profiles match).
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
- intent_coverage (`ssot_duplication`, `silent_error_edge_case`, `resource_security_perf`):
- reviewers (id, role, scope):
- findings (severity, location, issue, evidence, recommendation):
- conflicts:
- reconciliation_decision:
- residual_risks:
- go_no_go (`go` | `go_with_risks` | `hold`):
- verification_links:

Severity rubric (for findings):
- HIGH: blocker risk that can cause incorrect governance edits, policy drift, or unsafe execution sequence.
- MEDIUM: likely misuse or rework risk that is non-blocking with explicit controls.
- LOW: clarity/compliance improvement with low immediate execution risk.

Steps:
1) Extract candidate learnings (0-15):
   - If fewer than 5 VERIFIED candidates exist, continue with available candidates and state shortfall + reason.
   - Each candidate must include:
     - Evidence from this session (tag as R or D; R = runtime truth, D = recorded truth)
     - Failure mode prevented
     - Proposed invariant (S; one sentence, testable) + category (data, ordering, atomicity, idempotency, lifecycle, observability, other)
     - Proposed witness (what is measured, where recorded, pass criteria)
   - If evidence is weak, mark as UNVERIFIED and request additional context.
2) De-duplicate and place (verify):
   - For each candidate, search in this order:
     1. governance/playbooks/docs area
     2. referenced SSOT owner docs/files
     3. broader repo
   - Use `rg` for verification and record search terms used when practical.
   - Mark status as `ALREADY_COVERED`, `PARTIAL`, or `MISSING`.
3) Council review (required before edits):
   - Run the Subagent Council per `AGENTS.md` "Subagent Council (Hard Gate)" with minimum intention coverage (SSOT/duplication, silent-error/edge-case, resource/security/perf).
   - Merge findings into one council summary block using the required fields above.
   - For each HIGH/MEDIUM finding, include at least one evidence item (R or D) and one action (apply/defer + rationale).
   - If `go_no_go` is `hold`, stop and ask before editing.
   - If conflicts or gaps remain, pause and ask before editing.
4) Produce governance deltas (proposals or auto-edits, depending on authorization):
   - If auto-edit is authorized: apply minimal edits after the confirmation gate and within the scope in `AGENTS.md` "Governance Auto-Edit + Council Review".
   - If auto-edit is not authorized: propose deltas only.
5) Output records (deterministic; one record per candidate, exact field order):
   - ID:
   - Status (`MISSING`|`PARTIAL`|`ALREADY_COVERED`):
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
   - ID format rule: `GL-DDMMYYYY-###`
   - Increment rule: `###` starts at `001` within the session output and increments by 1 for each record.
6) Final summary:
   - P1 codify now (max 7; requires VERIFIED evidence + concrete verification command/manual check)
   - P2/P3 backlog
   - Already-covered (no action)
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
- Authority-first prevention point: `docs/agents/playbooks/governance-learnings-template.md` prompt pack owner.
- Target location: `docs/agents/playbooks/governance-learnings-template.md`
- Draft delta (for `MISSING`/`PARTIAL`) or coverage citation (for `ALREADY_COVERED`): Replace prompt skeleton with a self-contained prompt pack that inlines hard gates and preflight checks.
- Change Contract alignment: `AGENTS.md` template sections B (invariants), C (witnesses), D (authority impact), H (verification checklist).
- Witness/verification: `python3 scripts/check_governance_core.py` passes; manual witness confirms prompt pack contains hard gates inline and no external copy dependency.
- Risk if not addressed: Repeated governance drift and skipped council/confirmation gate steps.
- Modularity/structure decision: Keep playbook as single authority document; avoid creating parallel prompt docs.
- Priority + confidence (`P1`|`P2`|`P3` + `VERIFIED`|`UNVERIFIED`): P1 + VERIFIED

## Non-goals
- This playbook is not a replacement for `AGENTS.md`.
- This playbook does not define new SSOT owners.
- This playbook does not authorize governance auto-edits outside existing `AGENTS.md` gates.
