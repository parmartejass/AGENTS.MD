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
### CH-20260806-001 - Retire runtime projections, wrappers, and reference app template
- Change ID/date/status: CH-20260806-001 / 2026-08-06 / ready
- Closure statement: Retired governance-owned runtime installation/projection behavior, tracked root runtime copies, platform snapshot/status records, link/setup/sync helpers, PowerShell validator wrappers, the runnable dual-entry reference app template, projection/setup/linking/wrapper/exact-string-policy tests, the flat entrypoint registry path, and duplicate private validator fragments while preserving surviving source-asset owners and direct Python checks.
- Owner promotion references for durable facts or `N/A + reason`: `docs/project/goal/goal.md` owns the retirement as durable project intent; `docs/project/rules/rules.md` owns the no-reintroduction project rule; `docs/project/architecture/architecture.md` owns the surviving source-only architecture graph; `docs/project/data-truth/data-truth.md` owns source-asset data-truth routing; `AGENTS.md`, `docs/agents/20-sources-of-truth-map/sources-of-truth-map.md`, `docs/agents/22-ssot-authority-decisions/ssot-authority-decisions.md`, `docs/agents/25-docs-ssot-policy/docs-ssot-policy.md`, and `docs/agents/35-coding-principles/coding-principles.md` own reusable governance routing and checker contract updates.
- Changed surfaces grouped by owner: governance policy/routing in `AGENTS.md`, `agents-manifest.yaml`, `README.md`, and `docs/agents/`; project authority docs in `docs/project/`; direct Python validator owners under `scripts/`; non-owner X governance-research registration; tracked deletion of the retired runtime/template/wrapper/helper families.
- Verification command/manual witness and result: README-owned checks passed: docs router contract regression test ran 8 tests OK; docs SSOT checks passed with the existing defaults/default value note; project docs checks passed; folder architecture checks passed; folder architecture regression tests ran 12 tests OK; governance core checks passed; governance-core unit discovery ran 35 tests OK; strict safety mode reported `Summary: 0 error(s), 0 warning(s)` and passed; Python safety baseline reported `Summary: 0 error(s), 0 warning(s)`.
- Residual risks/follow-up: Downstream consumer repositories are not modified by this source checkout cleanup; any existing consumer-local runtime files remain outside this repo and must be managed by that consumer.
- Commit/PR reference or `N/A + reason`: N/A + reason: user explicitly requested no staging, commit, push, or publish.

### CH-20260622-001 - Harden structured JSON config authority package
- Change ID/date/status: CH-20260622-001 / 2026-06-22 / ready
- Closure statement: Added and hardened a structured owner contract for config-owned data, defaults, and settings authorities so the compact language-agnostic `ConfigManager` boundary, app-identity-derived JSON naming, owner-declared runtime path, customizable value routing, JSON config grouping, key/type vocabulary, examples/placeholders, defaults, schemas, activation validation, loader lifecycle, live GUI/CLI sync, consumers, outcomes, and witnesses are declared in the config owner instead of scattered across workflows, GUI/CLI, docs, or patches.
- Owner promotion references for durable facts or `N/A + reason`: `docs/agents/40-config-constants/config-constants.md` owns the durable config authority package; this changelog records closure only.
- Changed surfaces grouped by owner: config/constants policy in `docs/agents/40-config-constants/config-constants.md`; tracked closure record in `docs/project/changelog/changelog.md`.
- Verification command/manual witness and result: The README-owned verification commands current at that closure passed; those historical wrapper/template/projection commands were retired by the later source-only cleanup. Docs SSOT reported only the expected config-owner defaults wording warning and `git diff --check` reported only expected LF/CRLF warnings. Strict safety mode was run and failed only on ignored local scratch Python files outside the tracked commit scope; baseline Python safety passed with zero errors and zero warnings. Re-verification trigger: rerun the current README "Checks" when config authority package rules, README Checks, or release gates change.
- Residual risks/follow-up: Semantic enforcement remains review-driven; the checks prove structure and known governance invariants, not every future project-specific config package. Future patches must avoid adding concrete defaults/key tables, universal config paths, runtime JSON note-field patterns, or project-specific GUI behavior here unless this doc explicitly owns those values.
- Commit/PR reference or `N/A + reason`: N/A + reason: direct commit/push to `main` requested; this entry is recorded in the resulting commit.

### CH-20260621-004 - Clarify 400 LOC decomposition approach
- Change ID/date/status: CH-20260621-004 / 2026-06-21 / ready
- Closure statement: Clarified the 400 LOC coding hard gate as a trigger to apply the full coding-principles authority analysis, requiring a recorded decomposition decision and witness when a file exceeds the limit or the current change would make it exceed the limit.
- Owner promotion references for durable facts or `N/A + reason`: `docs/agents/35-coding-principles/coding-principles.md` owns the durable file-size decomposition mechanics; `scripts/check_folder_architecture/check_folder_architecture_main.py` remains the numeric Python LOC enforcement witness; this changelog records closure only.
- Changed surfaces grouped by owner: coding-principles mechanics in `docs/agents/35-coding-principles/coding-principles.md`; tracked closure record in `docs/project/changelog/changelog.md`.
- Verification command/manual witness and result: docs-SSOT, docs-router contract, agents-manifest, project-docs, folder-architecture, and governance-core checks passed; manual owner scan found the durable 400 LOC decomposition procedure only in `docs/agents/35-coding-principles/coding-principles.md` and numeric enforcement in `scripts/check_folder_architecture/check_folder_architecture_main.py`.
- Residual risks/follow-up: Semantic review remains required for future large refactors because checks can enforce file length and doc structure, but cannot prove a decomposition decision preserves authority boundaries by themselves.
- Commit/PR reference or `N/A + reason`: N/A + reason: direct commit/push to `main` requested; this entry is recorded in the resulting commit.

### CH-20260621-003 - Add scannable output shape hard gate
- Change ID/date/status: CH-20260621-003 / 2026-06-21 / ready
- Closure statement: Added a reusable `AGENTS.md` hard gate requiring non-trivial plans, reviews, implementation records, prompt scaffolds, council summaries, and final reports to expose decision-critical facts in scannable structured fields, compact tables, or short labeled lists.
- Owner promotion references for durable facts or `N/A + reason`: `AGENTS.md` owns the durable scannable output-shape obligation; `docs/project/changelog/changelog.md` records closure only and does not own the reusable rule.
- Changed surfaces grouped by owner: governance policy in `AGENTS.md`; tracked closure record in `docs/project/changelog/changelog.md`.
- Verification command/manual witness and result: docs-SSOT, docs-router contract, agents-manifest, project-docs, and governance-core checks passed; manual duplicate-rule scan found the full scannable-output rule only in `AGENTS.md` and closure references in this changelog.
- Residual risks/follow-up: Supporting prompt scaffolds remain non-owner examples; future changes may add route-only references to `AGENTS.md` if a scaffold appears narrower than the hard gate.
- Commit/PR reference or `N/A + reason`: N/A + reason: direct commit/push to `main` requested; this entry is recorded in the resulting commit.

### CH-20260621-002 - Consolidate SSOT jurisdiction and duplication pruning rule
- Change ID/date/status: CH-20260621-002 / 2026-06-21 / ready
- Closure statement: Consolidated the repeated one-source, reuse, no-duplicate, and no-drift governance concept into a single explicit SSOT jurisdiction and duplication pruning statement in `AGENTS.md`, with supporting docs routing to that jurisdiction instead of restating the mechanism.
- Owner promotion references for durable facts or `N/A + reason`: `AGENTS.md` owns the durable SSOT jurisdiction and duplication pruning rule; `docs/agents/10-repo-discovery/repo-discovery.md` routes discovery adoption to that jurisdiction; `docs/agents/20-sources-of-truth-map/sources-of-truth-map.md` routes concept jurisdiction ownership to that owner; `docs/agents/35-coding-principles/coding-principles.md` applies the rule to implementation-code mechanics.
- Changed surfaces grouped by owner: governance policy in `AGENTS.md`; supporting principles in `docs/agents/00-principles/principles.md`; discovery routing in `docs/agents/10-repo-discovery/repo-discovery.md`; concept-jurisdiction routing in `docs/agents/20-sources-of-truth-map/sources-of-truth-map.md`; implementation-code mechanics in `docs/agents/35-coding-principles/coding-principles.md`; prompt/log-schema/governance-learning scaffolds in `docs/agents/playbooks/`; tracked closure record in `docs/project/changelog/changelog.md`.
- Verification command/manual witness and result: docs-SSOT, docs-router, agents-manifest, project-docs, folder-architecture, governance-core, governance-core unit tests, `git diff --check`, stale-terminology scan, and council review passed; manual review confirmed the council SSOT reviewer now uses SSOT jurisdiction and duplication pruning while preserving the stable `ssot_duplication` schema token.
- Residual risks/follow-up: No known blocker after verification; manual review remains required because structural checks cannot prove every semantic duplication boundary.
- Commit/PR reference or `N/A + reason`: N/A + reason: direct commit/push to `main` requested; this entry is recorded in the resulting commit.

### CH-20260621-001 - Restore tracked Changelog closure-record owner
- Change ID/date/status: CH-20260621-001 / 2026-06-21 / ready
- Closure statement: Restored a required tracked project `Changelog` owner for closure records while preserving owner-doc truth for durable facts.
- Owner promotion references for durable facts or `N/A + reason`: `AGENTS.md`; `docs/agents/22-ssot-authority-decisions/ssot-authority-decisions.md` `SSOT-DEC-004`; `docs/agents/25-docs-ssot-policy/docs-ssot-policy.md`; `docs/agents/20-sources-of-truth-map/sources-of-truth-map.md`; `docs/agents/90-release-checklist/release-checklist.md`; `docs/agents/playbooks/project-docs-template/project-docs-template.md`; `docs/project/goal/goal.md`; `docs/project/architecture/architecture.md`; `docs/project/learning/learning.md`.
- Changed surfaces grouped by owner: governance policy and routing in `AGENTS.md`, `agents-manifest.yaml`, `README.md`, and `docs/agents/`; project-doc closure owner in `docs/project/changelog/`; project-doc validation in `scripts/check_governance_core/`; retired template scaffold.
- Verification command/manual witness and result: project-doc, docs-SSOT, manifest, docs-router, governance-core, folder-architecture, repo-hygiene, python-safety, targeted project-authority unit tests, full governance-core unit tests, template logging-contract tests, stale-surface scans, post-change council re-review, and `git diff --check` passed.
- Residual risks/follow-up: No known blocker; semantic jurisdiction remains intentionally enforced by owner docs plus council/manual review, while scripts enforce the structural project-doc route.
- Commit/PR reference or `N/A + reason`: N/A + reason: direct commit/push to `main` requested; this entry is recorded in the resulting commit.
