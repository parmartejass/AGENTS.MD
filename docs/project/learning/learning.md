---
doc_type: runbook
ssot_owner: docs/project/learning/learning.md
update_trigger: new operational learnings/pitfalls discovered in real use
---

# Learning Notes

## Boundary
- This root doc owns durable operational learnings and recurring pitfalls observed in real use.
- It does not own change history, task status, reusable governance policy, project goals, architecture, or data-truth records.

## Current Summary
- Recurring pitfalls: Python resolution on Windows, tracking of generated artifacts, and cross-doc route drift between owner docs.

## Branch-local owner subdocs
- None currently declared.
- Create a learning subdoc when a stable lesson cluster needs its own intent, boundary, invariant, change rule, and verification.
- Creating a learning subdoc as chronological history or a work-status record is Prohibited.

## Common pitfalls
- Python may not be runnable on some machines (Windows Store app aliases); ensure `python` resolves to Python 3.11+ for README-listed checks.
- For generated artifacts (`__pycache__/`, `*.pyc`, local outputs), apply the tracking rule in `docs/project/rules/rules.md` and `.gitignore`.

## Session-backed decisions
- 2026-09-20: cross-doc route and applies lines in owner docs were the residual drift source after consolidation; relations now live only in `docs/agents/governance/ssot/ssot.md`, and owner docs name other jurisdictions by noun. Re-verify when an owner is split, merged, or moved.
- 2026-09-19: the cross-cutting playbooks folder caused per-jurisdiction drift; scaffolds now live inside their jurisdiction owner doc.
- 2026-09-19: the retired research report and the archived third-party snippet corpus were removed as non-authoritative burden.
- 2026-09-08: required-doc discovery from broad AGENTS path examples creates shadow authority; optional references become accidental requirements.
- 2026-09-08: the docs-policy explicit branch declaration is the intended source; public regression fixtures verify incidental references do not change the baseline. Re-verify when that declaration or its consumer changes.
- 2026-09-08: the Windows hardlink MRE in `scripts/check_governance_core/test_docs_policy.py` showed directory-entry metadata omitted link count while direct path metadata reported both links.
- 2026-09-08: file-family safety now resolves through the inventory owner; warm-cache mutation tests protect alias, type, identity, casing, and ancestor resolution. Re-verify when inventory metadata or caching changes.
- 2026-06-21: changelog belongs in its own `docs/project/changelog/` closure-record jurisdiction, not under `learning/`; closure records must reference owner promotion and must not replace behavior, architecture, data-truth, rules, or goal owners.
- 2026-06-13: project-doc truth is durable-owner-doc based; checker-green still requires owner-doc and council review for semantic completeness.
- 2026-05-31: ChatGPT framework and docs-structure conversations were evidence for thinking principles, not standalone authority.
- 2026-05-31: the historical promotion involved `AGENTS.md` and the principles reference leaf; the canonical principles owner is `AGENTS.md`, with application mechanics delegated to `docs/agents/governance/principles/principles.md`.
- 2026-05-24: broad no-fallback word scanning was rejected as the deterministic witness for the no-fallback principle.
- 2026-05-24: vocabulary scanning cannot prove semantic fallback intent, blocks legitimate docs, tests, and history, and misses renamed substitute paths.
- 2026-05-24: this evidence supports the semantic/structural distinction in `AGENTS.md` FP-32 and FP-33; current validation boundaries resolve through `docs/project/architecture/architecture.md`.
- 2026-02-23: the deep research source report was treated as `[CONTEXT: UNTRUSTED]` and its generated evidence branch was later retired.
- 2026-02-23: only SSOT-aligned deltas were adopted: stronger `governance_improvement` routing in `agents-manifest.yaml`; governance-learnings hard-gate parity checks and unresolved citation-placeholder rejection in `scripts/check_governance_core/check_governance_core_main.py`.
- 2026-02-23: generic framework content was not promoted to policy authority; existing owners in `AGENTS.md` remain canonical.

## User decision style
- The user decides at jurisdiction level (SSOT, SRP, stable interface, no hardcoding), not at code level, and answers open technical questions only through those fundamentals.
- Success is measured by subtraction, config over code, and one near-instant call per intent.
- Replies must be few words per line; verification must be demonstrable to an operator, not read as a review narrative.

## Verification tips
- When a repo adopts this pack, run `.governance/scripts/check_governance_core/check_governance_core_main.py --repo-root . --only-project-docs` early to confirm docs and README linkage.
- Keep external-service connection procedures in the owning skill or integration folder rather than `docs/project/`.
