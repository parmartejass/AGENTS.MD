---
doc_type: runbook
ssot_owner: docs/project/learning/learning.md
update_trigger: new operational learnings/pitfalls discovered in real use
---

# Learning Notes

## Boundary
- This root doc owns durable operational learnings and recurring pitfalls observed in real use.
- It does not own change history, task status, reusable governance policy, project goals, architecture, or data-truth records.

## When to create a branch-local owner subdoc
- Create a learning subdoc when a stable lesson cluster needs its own intent, boundary, invariant, change rule, and verification.
- Do not create a learning subdoc as a chronological history or work-status record.

## Current Summary
- Existing notes capture high-signal pitfalls and verification tips.
- No branch-local learning subdocs are declared.

## Branch-local owner subdocs
- None currently declared.

## Common pitfalls
- Python may not be runnable on some machines (Windows Store app aliases). Ensure `python` resolves to Python 3.11+ so the README-listed Python checks can run.
- For generated artifacts (e.g., `__pycache__/`, `*.pyc`, local outputs), apply the tracking rule in `docs/project/rules/rules.md` Don't and the ignore patterns in `.gitignore`.

## Session-backed decisions
- 2026-05-31: ChatGPT framework/docs-structure conversations were treated as evidence for thinking principles, not standalone authority. The historical promotion involved `AGENTS.md` and the principles reference leaf; the current canonical principles owner is `AGENTS.md`, with current application mechanics delegated through `docs/agents/00-principles/principles.md`; the canonical principle text remains exclusively in `AGENTS.md`.
- 2026-06-13: Project-doc truth is durable-owner-doc based. Checker-green still requires owner-doc and council review for semantic completeness.
- 2026-06-21: Changelog belongs in its own `docs/project/changelog/` closure-record jurisdiction, not under `learning/`; closure records must reference owner promotion and must not replace behavior, architecture, data-truth, rules, or goal owners.
- 2026-05-24: Broad no-fallback word scanning was rejected as the deterministic witness for `AGENTS.md` "No Fallback or Legacy Runtime Paths". Project-scoped Codex session evidence in `rollout-2026-05-24T13-50-32-019e5912-3cc3-7033-8b35-23ac0514bf1e.jsonl` at 2026-05-24T08:36:02Z and 2026-05-24T08:36:09Z recorded that vocabulary scanning cannot prove semantic fallback intent, can block legitimate docs/tests/history, and can miss renamed substitute paths. This evidence supports the semantic/structural distinction in `AGENTS.md` FP-32 and FP-33; current validation boundaries resolve through `docs/project/architecture/architecture.md`.

## Deep research synthesis (2026-02-23)
- Source report was treated as `[CONTEXT: UNTRUSTED]`; the generated evidence branch was later retired.
- Only SSOT-aligned deltas were adopted:
  - strengthen `governance_improvement` authority routing in `agents-manifest.yaml`
  - add governance learnings hard-gate parity checks in `scripts/check_governance_core/check_governance_core_main.py`
  - reject unresolved citation placeholder tokens in `docs/` via `scripts/check_governance_core/check_governance_core_main.py`
- Generic framework content was not promoted to policy authority; existing owners in `AGENTS.md` remain canonical.

- 2026-09-08: Required-doc discovery from broad AGENTS path examples creates shadow authority: optional references can become accidental requirements. The docs-policy explicit branch declaration is now the intended source; public regression fixtures verify that incidental references do not change the baseline. Re-verify when that declaration or its consumer changes.

- 2026-09-08: The Windows hardlink MRE in `scripts/check_governance_core/test_docs_policy.py` showed that directory-entry metadata omitted link count while direct path metadata reported both links. File-family safety now resolves through the inventory owner; warm-cache mutation tests protect alias, type, identity, casing and ancestor resolution. Re-verify this behavior when inventory metadata or caching changes.

## Verification tips
- If a repo adopts this pack, run `.governance/scripts/check_governance_core/check_governance_core_main.py --repo-root . --only-project-docs` early to ensure docs+README linkage is in place.
- Keep external-service connection procedures in the owning skill or integration folder rather than `docs/project/`.

## Debugging references
- Use `AGENTS.md` "Bias-Resistant Debugging" for evidence-driven fixes.
