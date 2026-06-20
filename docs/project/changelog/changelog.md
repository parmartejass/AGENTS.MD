---
doc_type: reference
ssot_owner: docs/project/changelog/changelog.md
update_trigger: non-trivial work closes OR closure-record field contract changes
---

# Changelog

## Boundary
- This branch owns tracked closure-record facts for completed non-trivial work.
- It does not own behavior, invariants, project goals, rules, data truth, architecture, implementation rationale, active work, raw prompts, transcripts, or unpromoted working evidence.

## Invariant
- Each closure record references the owning docs/code/config/data/workflow authority for durable facts, or records `N/A + reason`.
- A closure record must not substitute for owner-doc promotion.
- Raw secrets, credentials, PII, customer data, and oversized pasted artifacts must not be stored here.

## Field Contract
- Closure-record field template/order is owned by `docs/agents/90-release-checklist/release-checklist.md`.
- Entries must follow that owner instead of redefining the field template here.

## Entries
### CH-20260621-001 - Restore tracked Changelog closure-record owner
- Change ID/date/status: CH-20260621-001 / 2026-06-21 / ready
- Closure statement: Restored a required tracked project `Changelog` owner for closure records while preserving owner-doc truth for durable facts.
- Owner promotion references for durable facts or `N/A + reason`: `AGENTS.md`; `docs/agents/22-ssot-authority-decisions/ssot-authority-decisions.md` `SSOT-DEC-004`; `docs/agents/25-docs-ssot-policy/docs-ssot-policy.md`; `docs/agents/20-sources-of-truth-map/sources-of-truth-map.md`; `docs/agents/90-release-checklist/release-checklist.md`; `docs/agents/playbooks/project-docs-template/project-docs-template.md`; `docs/project/goal/goal.md`; `docs/project/architecture/architecture.md`; `docs/project/learning/learning.md`.
- Changed surfaces grouped by owner: governance policy and routing in `AGENTS.md`, `agents-manifest.yaml`, `README.md`, and `docs/agents/`; project-doc closure owner in `docs/project/changelog/`; project-doc validation in `scripts/check_governance_core/`; template scaffold in `templates/python-dual-entry/docs/project/`.
- Verification command/manual witness and result: project-doc, docs-SSOT, manifest, docs-router, governance-core, folder-architecture, repo-hygiene, python-safety, targeted project-authority unit tests, full governance-core unit tests, template logging-contract tests, stale-surface scans, post-change council re-review, and `git diff --check` passed.
- Residual risks/follow-up: No known blocker; semantic jurisdiction remains intentionally enforced by owner docs plus council/manual review, while scripts enforce the structural project-doc route.
- Commit/PR reference or `N/A + reason`: N/A + reason: direct commit/push to `main` requested; this entry is recorded in the resulting commit.
