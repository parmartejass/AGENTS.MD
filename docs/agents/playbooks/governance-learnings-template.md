---
doc_type: playbook
ssot_owner: AGENTS.md
update_trigger: governance learning capture procedure or output expectations change
---

# Playbook - Governance Learnings (Session -> Governance Deltas)

Use when:
- You want an AI assistant (Claude/Codex/Copilot/etc.) to review a work session and extract new learnings that should be codified into this governance pack.
- You want the assistant to propose exact governance updates (where to put them + draft snippets) while avoiding duplicates.

Definition:
- Learning: a repeatable pitfall, missing invariant, missing witness/check, missing SSOT owner, missing template, or missing injection profile that would prevent future errors if codified.

Hard gates:
- Read and follow `AGENTS.md` (SSOT). If you cannot access it, request it before doing any work.
- Follow `AGENTS.md` "Context Injection Procedure (Hard Gate)" (consult `agents-manifest.yaml`, load injected docs/playbooks).
- Before claiming something is "missing", verify it does not already exist (search the repo with `rg`).
- Do not edit files unless explicitly asked; propose deltas only.
- Follow `docs/agents/25-docs-ssot-policy.md` (docs cannot become a second SSOT).

## Prompt skeleton (copy/paste into any chat)

```
Hard gates:
- Read and follow `AGENTS.md` (SSOT). If you cannot access it, ask me to paste it before doing any work.
- Follow `AGENTS.md` "Context Injection Procedure (Hard Gate)".
- Before asserting a learning is "missing", search the repo to verify it is not already covered (use `rg`).
- Do not edit files unless explicitly asked; propose deltas only.

Task type: governance_improvement

Goal:
- Scrutinize this session (and any referenced repo files) to extract new governance learnings that should be codified, and propose exactly where/how to codify them.

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
     - `docs/project/learning.md` for repo-specific operational pitfalls
     - `agents-manifest.yaml` for detect/inject gaps (missing profile or missing signals)
     - `scripts/*` for deterministic enforcement checks
     - `docs/agents/index.md` or README if a new doc/playbook is proposed (avoid orphan docs)
3) Produce governance delta proposals (do not edit unless explicitly asked):
   - For each missing learning, output:
     - ID: `LEARN-###` + short title
     - Evidence (session) + why it matters
     - Authority-first prevention point (earliest contract/authority that should prevent it)
     - Target file + exact section to update (or create)
     - Draft text snippet (minimal; reference SSOT owners by identifier; do not re-encode constants/rules)
     - Witness/verification (how to prove/enforce deterministically)
     - Risk if not addressed
     - Priority: MUST | SHOULD | COULD
4) Final summary:
   - MUST-codify (max 7)
   - SHOULD/COULD
   - Already-covered (no action)
   - Manifest/injection improvements (if any)
   - Open questions/unknowns

Output format:
- Markdown
- Short bullets and small tables
- Each learning must be actionable: "where to change + what to add + how to verify"
```
