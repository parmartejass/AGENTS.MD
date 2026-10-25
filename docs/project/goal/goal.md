---
doc_type: reference
ssot_owner: docs/project/goal/goal.md
update_trigger: project objective, accepted intent, or verification requirements change
---

# Goal

## Objective
- Maintain a reusable, repo-agnostic governance pack for autonomous coding agents.

## Acceptance criteria
- Every repository Markdown file meets the line limit with its meaning intact: `docs/agents/governance/documentation/documentation.md` Size and cohesion.
- The Fundamental Principles keep the wording, order and `MUST ` lead adopted on 2026-10-25 under the user's delegation (agent-drafted): `AGENTS.md` Fundamental Principles (Highest Repository Authority), Structural contract.
- Owner-local identifiers supply stable routes without a second principles document or policy registry.
- Every lower document MUST be fully audited for owner derivation, necessity, duplication, and weakened obligations.
- Each declared lower owner retains its jurisdiction-specific rules, contracts, safeguards, mechanics, examples, and verification requirements.
- Pruning removes only demonstrated duplication or conflict.
- Keyword replacement or acknowledgment is not acceptance.
- Constitutional application, binding user intent, user-decision precedence and durable-record maintenance hold without user reminders: `AGENTS.md` User Prompt Intake and Durable Project Truth.
- The agent lifecycle, including Main's user-representative role, source separation and independent review, has the one owner that `AGENTS.md` names: `Orchestration.md`.
- Foundation acceptance follows `AGENTS.md` Mandatory Foundations (membership) and `Orchestration.md` Foundation loading and application (source and application witnesses, source isolation).
- `agents-manifest.yaml` routes Governance Agent authorities as `Orchestration.md` Task agents and focused exploration defines.
- The governance research corpus has one source, recorded in `docs/project/architecture/architecture.md` Authority graph (owner -> dependents).
- Governance-core consumers keep one plain-data public API: `README.md` Governance-core programmatic API.
- Structural validation MUST NOT claim source equality, semantic compliance, live agent obedience, or uninstrumented timing evidence; this extends `AGENTS.md` FP-32.
- Project docs retain declared durable project facts and owner routes; reusable source assets stay under `docs/agents/`.

## Durable intent
Each record below is an explicit user decision unless marked `agent`; it is requested intent, not an implementation or compliance claim; implementation status lives in `docs/project/changelog/changelog.md`; re-evaluate a record when the user revisits it or its named owner changes.
- 2026-10-25 (governing rule): adopt the governing rule ("Every capability, name and fact exists exactly once ...") as the replacement of the SRP Stable-Interface wording, now `AGENTS.md` FP-13; add no other rule ("Add no new rules except the governing rule above"); delegate the Phase-3 choices to Main ("Take all positive decisions and implement ..."). Landed: CH-20261025-001.
- 2026-10-25 (`agent`, Main under that delegation): GR-1 e and GR-2 b: FP-13 is "MUST hold: " plus the governing rule; FP-12 and FP-15 stay as extensions of FP-13.
- 2026-10-25 (`agent`): GR-3 a: Agent decision: Main reads 'never pick a winner' as banning a choice by judgment; applying a declared precedence rule is not picking a winner. It adds no obligation and does not soften FP-13.
- 2026-10-25 (`agent`): GR-4 a: a missing owner halts and escalates; the user decides any new owner (`AGENTS.md` FP-13, FP-27, Jurisdictional Decomposition).
- 2026-10-25 (`agent`): K4 a: a warning-only repeat report in the existing checker (`docs/agents/governance/documentation/documentation.md` Validation boundary).
- 2026-10-25 (`agent`): K5 b: FP-01 to FP-35 rewritten in plain words, adopted on 2026-10-25 under the user's delegation (agent-drafted); FP-13 is the user's own wording.
- 2026-10-25 (`agent`): K9 b: the changelog owns supersession history (`docs/project/changelog/changelog.md`).
- 2026-10-25 (`agent`): U1 b: one Lexicon in `docs/agents/governance/ssot/ssot.md`; terms defined in `AGENTS.md` or `Orchestration.md` stay there by declared precedence and the Lexicon links them, so each term has one definition.
- 2026-10-25 (`agent`): O1, O3 and O5 retired as superseded by FP-13; O4 and O6 retired under the user's delegation.
- 2026-10-25 (`agent`): T1 a: the full ledger goes in numbered PR comments.
- 2026-10-24 (root launcher declaration): a project may declare a repository-root launcher file in its own architecture record ("yes al;" to the proposal to change this pack so a project can declare a root launcher such as `main.py`); owner: `docs/agents/governance/coding/coding.md` Packaged-folder code mechanics. Landed: CH-20261024-001.
- 2026-10-05 (stability scope): stability work stays within the packaged-folder, SSOT, SRP, and no-hardcoding intent and its governance-core enforcement. Agent-found gaps in unrelated owners stay out of scope: they are implemented, decided, or raised only when the user asks ("This is overburden avoid"; "the intent is entirely drifted").
- 2026-10-04 (packaged-folder root source): the folder-architecture check reads the pack's Python roots from the pack's own record and a host's roots from the host's own record, with no hardcoded root list or limit ("As.governence so direct folder is know"; "Don't hardcode via limit"); owner: `docs/project/architecture/architecture.md` Governance source roots. Landed: CH-20261004-001.
- 2026-10-03 (follow-up scope): fix the agent-authored SRP/SSOT review findings M1-M4 and I1-I6 of the packaged-folder landing in a separate workflow ("Fix M1-M4 + I1-I6"). N-class notes are excluded. Landed: CH-20261004-001.
- 2026-10-03 (M5 scope): the packaged-folder check enforces at the project root from the checked project's own architecture root markers ("Enforce at project root"); owners: `docs/project/architecture/architecture.md` Governance source roots and `README.md` Checks. Landed: CH-20261004-001.
- 2026-10-03 (packaged-folder rule): one top-level `AGENTS.md` instruction for every code or doc artifact, with the native-language packaged folder as the fundamental rule; the `<feature>_main` convention is an old learning that "may not" be the best default; owner: `AGENTS.md` Jurisdictional Decomposition (Highest Operating Rule). Extends the 2026-09-20 records below. Landed: CH-20261003-001.
- 2026-10-03 (migration scope): a new `AGENTS.md` rule, the affected lower docs, and governance-core as a native Python package (`__init__.py` API, `__main__.py` launcher). `check_governance_core_main.py` is removed with no shim, and vendored repos update their check command. Landed: CH-20261003-001.
- 2026-10-03: keep the `<authority>_index.md` docs-router name as a custom exception to the packaged-folder rule; `SSOT-DEC-003` holds the exception and its re-evaluation trigger.
- 2026-10-03: defer packaging `X-Bookmarks Import/` (`SSOT-DEC-001` non-owner workspace) and record it as non-conformant. Re-evaluate on its next non-trivial code change, an `SSOT-DEC-001` change, or a user request.
- 2026-10-03: the owning task agent performs its own explorer passes when nested subagents are unavailable ("the owing subagents can handle it as it's responsible"); owner: `Orchestration.md` Task agents and focused exploration.
- 2026-09-27: one stable `AGENTS.md` block holds the prompt-to-project-doc instructions: `AGENTS.md` User Prompt Intake and Durable Project Truth.
- 2026-09-20: `AGENTS.md` top SSOT rule owns "Resolve once before fan-out"; the Bilty case is illustrative only.
- 2026-09-20: every downstream harness imports this repository as its governance baseline ("this project is the highest governing repo which i import in all").
- 2026-09-20: reply and question style; owner: `docs/agents/governance/prompt-authoring/prompt-authoring.md` Use rules.
- 2026-09-20: FP-03 speed and the Fundamental Principles are the main criterion for every baseline decision.
- 2026-09-20: the three-layer `docs/agents/` structure, with one packaged folder per jurisdiction and one `baseline` block per interfaces or playbooks owner; owners: `AGENTS.md` Supporting Docs (Three Layers), `docs/agents/governance/ssot/ssot.md` Relation routing rule, `docs/project/rules/rules.md`, and `docs/project/architecture/architecture.md` Current Summary and Reserved jurisdictions.
- 2026-09-20: `AGENTS.md` carries Jurisdictional Decomposition as the highest operating rule.
- 2026-09-19: the Baseline Interface Rule (Excel: OOXML first); owners: `AGENTS.md` First-Principles Protocol and `docs/agents/governance/principles/principles.md` Stable baseline interface.
- 2026-09-19: each governance instruction lives in one single-jurisdiction owner doc as terse per-line obligations. Foundations stay unchanged except for path migration and that rule.
- 2026-09-15: FP-03 is a universal end-to-end performance goal. `AGENTS.md` FP-03 owns the values; lower owners keep mechanics and measurements without narrowing it.
- 2026-09-13: foundations keep their locations and loading is mandatory, with the parent accountable; owners: `AGENTS.md` Mandatory Foundations (membership) and `Orchestration.md` Foundation loading and application (loading and evidence).
- 2026-09-08: concise maintained documentation as the primary durable governing record; owners: `AGENTS.md` User Prompt Intake and Durable Project Truth and `docs/agents/governance/documentation/documentation.md` Concise owner records.

## Boundary
- This file owns stable project purpose, accepted scope, non-goals, and verification intent; architecture, data truth, rules, closure records, and learnings keep their project owners; reusable policy stays outside this branch.

## Non-goals
- This repo does not define domain business logic or a second governance framework.
- Static validation is not a semantic or platform-performance guarantee.

## Verification
- Run root `README.md` Checks.
- For principle updates, compare canonical paragraphs with the authorized source after line-ending normalization only.
- Reconcile every scoped document's full-read outcome and review the resulting owner graph under `Orchestration.md`.
