---
doc_type: playbook
ssot_owner: AGENTS.md
update_trigger: governance learning capture procedure or output expectations change
---

# Playbook - Governance Learnings (Session -> Governance Deltas)

Use when:
- You want an AI assistant (Claude/Codex/Copilot/etc.) to review a work session and extract new learnings that should be codified into this governance pack.
- You want the assistant to propose or (when explicitly authorized) apply governance updates while avoiding duplicates.

Definition:
- Learning: a repeatable pitfall, missing invariant, missing witness/check, missing SSOT owner, missing template, or missing injection profile that would prevent future errors if codified.

Hard gates:
- Read and follow `AGENTS.md` (SSOT). If you cannot access it, request it before doing any work.
- Follow `AGENTS.md` "Context Injection Procedure (Hard Gate)" (consult `agents-manifest.yaml`, load injected docs/playbooks).
- Before claiming something is "missing", verify it does not already exist (search the repo with `rg`).
- Auto-edit is allowed only when this playbook is explicitly invoked and edit permission is granted for governance docs/playbooks and `agents-manifest.yaml`; otherwise propose deltas only (see `AGENTS.md` "Governance Auto-Edit + Council Review").
- Before any edit: run the Council Review step and apply the confirmation gate from `AGENTS.md`.
- Follow `docs/agents/25-docs-ssot-policy.md` (docs cannot become a second SSOT).

## Prompt skeleton (copy/paste into any chat)

```
Hard gates:
- Read and follow `AGENTS.md` (SSOT). If you cannot access it, ask me to paste it before doing any work.
- Follow `AGENTS.md` "Context Injection Procedure (Hard Gate)".
- Before asserting a learning is "missing", search the repo to verify it is not already covered (use `rg`).
- Auto-edit is allowed only when this playbook is explicitly invoked and edit permission is granted for governance docs/playbooks and `agents-manifest.yaml`; otherwise propose deltas only (see `AGENTS.md` "Governance Auto-Edit + Council Review").
- Before any edit: run the Council Review step and apply the confirmation gate from `AGENTS.md`.

Task type: governance_improvement

Goal:
- Scrutinize this session (and any referenced repo files) to extract new governance learnings that should be codified, and propose or apply updates when authorized.

Evidence inputs (provide if available):
- Session transcript or recap
- Files changed and diffs
- Commands run + outputs
- Error messages/logs
- Decisions that caused rework

If you cannot see the full session history:
Ask me for a "Session Recap" using this schema, then proceed:
- Work performed:
- Failures/friction encountered (exact messages if any):
- Workarounds used:
- Decisions made:
- Repeated confusion points:
- What I wish had existed in governance beforehand:

Required repo context (read at minimum):
- `AGENTS.md`
- `agents-manifest.yaml`
- `docs/agents/index.md`
- `docs/agents/20-sources-of-truth-map.md`
- `docs/agents/25-docs-ssot-policy.md`
- `docs/project/learning.md`
- Plus any injected docs/playbooks per the manifest (or `fallback_inject` if no profiles match).

Decision-grade brief (required before learnings):
- Model summary (inputs/outputs/side effects/boundaries); reference `docs/agents/00-principles.md` and `AGENTS.md` "First-Principles Protocol" (do not duplicate).
- SSOT map for this session (constants/config/rules/workflows/lifecycle utilities); reference `docs/agents/20-sources-of-truth-map.md`.
- Proof obligations (preconditions/postconditions/failure modes) + verification commands you will use.
- Confidence gate: label each claim as VERIFIED or UNVERIFIED (no MUST proposals without VERIFIED evidence).
- Change Contract alignment (required before any edit; reference the `AGENTS.md` template).

Steps:
1) Extract candidate learnings (5-15):
   - Each must include:
     - Evidence from this session (tag as R or D; quote/paraphrase)
     - Failure mode prevented (what would break next time)
     - Proposed invariant (S; one sentence, testable) + category (data, ordering, atomicity, idempotency, lifecycle, observability, other)
     - Proposed witness (what is measured, where recorded, pass criteria)
   - If evidence is weak, mark as UNVERIFIED and ask for more context.
2) De-duplicate and place (verify):
   - For each candidate, search the repo for existing coverage.
   - If covered: mark ALREADY COVERED and cite where (file + section).
   - If partially covered: mark PARTIAL and cite the gap.
   - If missing: decide correct codification target:
     - `AGENTS.md` for hard gates / cross-cutting invariants / "must always"
     - `docs/agents/*.md` for supporting policy/runbook (non-authoritative; intent/runbook only)
     - `docs/agents/playbooks/*.md` for copy/paste templates
     - `docs/agents/skills/*.md` for skill standards and platform adapters (no policy duplication)
     - `docs/project/learning.md` for repo-specific operational pitfalls
     - `agents-manifest.yaml` for detect/inject gaps (missing profile or missing signals)
     - `scripts/*` for deterministic enforcement checks
     - `docs/agents/index.md` or README if a new doc/playbook is proposed (avoid orphan docs)
3) Council review (required before edits):
   - Run the Subagent Council per `AGENTS.md` "Subagent Council (Hard Gate)" and ensure minimum intention coverage (SSOT/duplication, silent-error/edge-case, resource/security/perf).
   - Merge findings; if conflicts or gaps remain, pause and ask before editing.
4) Produce governance deltas (proposals or auto-edits, depending on authorization):
   - If auto-edit is authorized: apply minimal edits after the confirmation gate, and summarize changes using the fields below.
   - If auto-edit is not authorized: propose deltas only.
   - For each missing learning, output:
     - ID: `LEARN-###` + short title
     - Evidence (session) + why it matters
     - Authority-first prevention point (earliest contract/authority that should prevent it) + why there instead of the symptom location
     - Target file + exact section to update (or create)
     - Draft text snippet (minimal; reference SSOT owners by identifier; do not re-encode constants/rules)
     - Change Contract alignment: reference `AGENTS.md` (map to the relevant sections; do not duplicate the full contract)
     - Witness/verification (how to prove/enforce deterministically)
     - Risk if not addressed
     - Confidence: MUST | SHOULD | COULD + VERIFIED | UNVERIFIED (MUST requires a concrete witness + verification command)
5) Final summary:
   - MUST-codify (max 7)
   - SHOULD/COULD
   - Already-covered (no action)
   - Manifest/injection improvements (if any)
   - Open questions/unknowns

Output format:
- Markdown
- Short bullets and small tables
- Start with a "Decision-grade brief" section before listing learnings.
- Each learning must be actionable: "where to change + what to add + how to verify"
```
