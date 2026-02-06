---
doc_type: playbook
ssot_owner: AGENTS.md
update_trigger: governance learning capture procedure or output expectations change
---

# Playbook - Governance Learnings (Session -> Governance Deltas)

Use when:
- You want an AI assistant (Claude/Codex/Copilot/etc.) to review a work session and extract learnings that should be codified into this governance pack.
- You want the assistant to propose or (when explicitly authorized) apply governance updates while avoiding duplicates.

Definition:
- Learning: a repeatable pitfall, missing invariant, missing witness/check, missing SSOT owner, missing template, or missing injection profile that would prevent future errors if codified.

Hard gates:
- Read and follow `AGENTS.md` (SSOT). If you cannot access it, request it before doing any work.
- Follow `AGENTS.md` "Context Injection Procedure (Hard Gate)" (consult `agents-manifest.yaml`, load injected docs/playbooks).
- Auto-edit is allowed only when this playbook is explicitly invoked (see `AGENTS.md` "Governance Auto-Edit + Council Review").
- Before any edit: run the Council Review step and apply the confirmation gate from `AGENTS.md`.
- Follow `docs/agents/25-docs-ssot-policy.md` (docs cannot become a second SSOT).

Language discipline:
- Use `MUST` / `Hard Gate` only when quoting requirements explicitly hard-gated in `AGENTS.md`.
- Use `must` / `required` for playbook procedure steps.
- Use `should` / `recommended` for suggestions and preferences.

Procedure guardrails:
- Before claiming something is "missing", verify it does not already exist (search the repo with `rg`).
- If auto-edit is not authorized by the user/session policy, propose deltas only.

## Prompt skeleton (copy/paste into any chat)

```
Hard gates:
- Copy the "Hard gates" section from `docs/agents/playbooks/governance-learnings-template.md` verbatim and keep wording in sync.

Task type: governance_improvement

Goal:
- Scrutinize this session (and any referenced repo files) to extract governance learnings that should be codified, then propose or apply updates when authorized.

Field completion rule:
- Fill every required field. If information is missing, write `Unknown` or `N/A + reason` (do not omit fields).

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
   - For each candidate, search the repo for existing coverage (start with governance docs + referenced SSOT owners; expand only if needed).
   - Mark status as `ALREADY_COVERED`, `PARTIAL`, or `MISSING`.
3) Council review (required before edits):
   - Run the Subagent Council per `AGENTS.md` "Subagent Council (Hard Gate)" with minimum intention coverage (SSOT/duplication, silent-error/edge-case, resource/security/perf).
   - Merge findings; if conflicts or gaps remain, pause and ask before editing.
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
   - Confidence (`MUST`|`SHOULD`|`COULD` + `VERIFIED`|`UNVERIFIED`):
   - If a field is not applicable, write `N/A + reason`.
6) Final summary:
   - MUST-codify (max 7; MUST requires VERIFIED evidence + concrete verification command/manual check)
   - SHOULD/COULD
   - Already-covered (no action)
   - Manifest/injection improvements (if any)
   - Open questions/unknowns
   - UNVERIFIED items cannot be promoted as MUST.

Output format:
- Markdown
- Short bullets and small tables
- Section order: Decision-grade brief -> Output records -> Final summary
- Each learning must be actionable: where to change + what to add + how to verify
```
