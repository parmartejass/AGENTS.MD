---
doc_type: runbook
ssot_owner: docs/project/learning/learning.md
update_trigger: new operational learnings/pitfalls discovered in real use
---

# Learning Notes

## Boundary
- This root doc owns durable operational learnings and recurring pitfalls observed in real use.
- It does not own change history, task status, reusable governance policy, project goals, architecture, or data-truth records.

## Common pitfalls
- 2026-10-03 user-reported: agents "fail to comply" with existing packaged-folder instructions; one incidence agent-verified (below); cause unverified. Validate through the consolidated contract, its structural witness, and independent review.
- 2026-10-03 agent-verified: a migration that lands a structural rule must also satisfy it; the governance-core migration moved a 146-line CLI module verbatim into the package entry while the checker verified only entry presence, so the check stayed green. Lesson: verify every changed artifact against the full rule, with a manual witness wherever the checker does not enforce it, before closure. Fixed with AST interface witnesses in CH-20261004-001.
- 2026-09-27 user-reported: prompt-originated information and decisions were omitted from project docs and lost; incidence and cause unverified. Validate through prompt-to-owner intake evidence and independent review.
- 2026-10-05 agent-verified: fixture setups re-ran full public validation of the unchanged live repository 152 times (64 of 70 suite seconds). Lesson: validate an unchanged live owner once per process and reuse the result only while every file it returns keeps its validated file state.
- 2026-09-08 agent-verified: on Windows, directory-entry metadata omitted the hardlink count while direct path metadata reported it (MRE in `scripts/check_governance_core/test_docs_policy.py`); file-family safety resolves through the inventory owner.
- Python may not be runnable on some machines (Windows Store app aliases); ensure `python` resolves to Python 3.11+ for README-listed checks.
- For generated artifacts (`__pycache__/`, `*.pyc`, local outputs), apply the tracking rule in `docs/project/rules/rules.md` and `.gitignore`.
- Broad vocabulary scanning cannot prove semantic fallback intent, blocks legitimate docs, tests, and history, and misses renamed substitute paths; it was rejected as the no-fallback witness (2026-05-24).
- Required-doc discovery from broad `AGENTS.md` path examples creates shadow authority; the docs-policy explicit branch declaration is the intended source (2026-09-08).
- Cross-doc route and applies lines in owner docs were the residual drift source after consolidation; relations live only in `docs/agents/governance/ssot/ssot.md` (2026-09-20).

## User decision style
- The user decides at jurisdiction level (SSOT, SRP, stable interface, no hardcoding), not at code level, and answers open technical questions only through those fundamentals.
- Success is measured by subtraction, config over code, and one near-instant call per intent.
- Replies must be few words per line; verification must be demonstrable to an operator, not read as a review narrative.

## Verification tips
- When a repo adopts this pack, run the README Checks target-repo project-docs command early to confirm docs and README linkage.
- Keep external-service connection procedures in the owning skill or integration folder rather than `docs/project/`.
