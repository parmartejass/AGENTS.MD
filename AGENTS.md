# AGENTS.md - Canonical Agent Constitution (SSOT / No Duplicates)

This file is the single source of truth (SSOT) for **how any autonomous coding agent must operate in this repository**.

Hard gate:
- Do not write or modify code or documentation until this file has been read.
- If repository files are not accessible, request that the user paste `AGENTS.md`.
- If any other instruction file conflicts with this one, **`AGENTS.md` wins**.

## Objective

Deliver changes that are:
- **Correct**: verified against the repo and tools; no guessed APIs/paths.
- **Deterministic**: same inputs -> same outputs (no hidden side effects).
- **Efficient**: prefers the fastest safe approach when speed/scale is part of the goal; avoids unnecessary I/O/tool calls.
- **Maintainable**: each concept defined exactly once (SSOT / no duplicates).
- **Auditable**: logs + clear run outcomes; failures are explicit.
- **Safe**: no resource leaks; Excel COM + GUI threading rules are enforced.
- **Searchable**: critical concepts are discoverable via grep + semantic search.

## Vendored Authority + Path Resolution (SSOT)

When vendored under `.governance/`, `.governance/AGENTS.md` is authoritative; root `AGENTS.md` and `CLAUDE.md` are loader stubs that route to it.

Resolve governance paths relative to the governance root: the directory containing `AGENTS.md` and `agents-manifest.yaml`. This includes governance-root references such as `docs/agents/...`, `scripts/...`, and `./README.md`.

Resolve project-owned paths, including `docs/project/...` and project `README.md`, relative to the project root. When vendored, the project root is the parent of `.governance/`; governance-root paths resolve under `.governance/` without rewriting path strings in docs or manifests.

## Submodule Workflow Rules (Hard Gate)

The governance pack source repo is: `https://github.com/parmartejass/AGENTS.MD.git`

When editing files inside `.governance/`, the change belongs to the governance pack source repo, not to the parent project.

Hard rules:
- **NEVER** commit `.governance/` file edits from the parent repo directory.
- Commit governance file changes in the submodule repo (`parmartejass/AGENTS.MD`).
- The parent repo stores only a submodule pointer (SHA); after the governance change lands, the parent repo may update only that pointer.

## Prime Directive: Verify, Then Trust

Agents are probabilistic generators. The repo and tools are deterministic.
When a fact can be verified with tools, **verify it** instead of guessing.

Never invent:
- imports/dependencies
- file paths
- functions/classes/symbols
- CLI flags or config keys

If verification is not possible, treat it as **Unknown** and ask.

## First-Principles Protocol (Hard Gate)

Before implementing, explicitly define:
- **Model**: inputs, outputs, side effects, and system boundaries.
- **SSOT map**: which owner(s) hold constants, config, rules, workflows, and any lifecycle utilities.
- **Root-cause uplift** (authority-first): for any defect or error, trace from symptom to the earliest authority/contract/boundary that should have prevented it; prefer fixing there by adding or strengthening invariants/validation so the class of errors becomes structurally impossible; one authority fix prevents N errors. If a symptom-level patch is unavoidable, record why upstream prevention is infeasible and what error class remains unprevented.
- **Structural consolidation** (authority-first): when multiple findings map to the same invariant/authority, treat them as one defect; default to a single upstream fix in the authority owner.
- **Derived task authority** (authority-first): for any non-trivial output, first identify or create the minimum task-specific control artifact required to make the output trustworthy (for example an authority map, source map, extraction ledger, validation matrix, patch plan, or test fixture). The final output must be generated from and verified against that control artifact; do not treat the final output itself as the authority.
- **Patch, do not fork authority**: when improving governance, docs structure, frameworks, prompts, or reusable procedures, update the current highest owning authority through an explicit patch/supersession path. Do not create disconnected framework versions, parallel docs, or replacement structures unless the user explicitly authorizes a new authority and the old authority is deprecated or superseded.
- **Proof obligations**: preconditions/postconditions + failure modes to cover.
- **Verification**: exact commands or deterministic manual checks (include at least one failure-path check when feasible).
- **Resource bounds**: timeouts, cancellation, and guaranteed cleanup in `finally` for external resources.
- **Performance constraints**: expected data sizes and speed targets; choose algorithm/I/O strategy accordingly, without weakening correctness or safety.
- **Design principles (generation + maintenance)**: apply DRY, KISS, YAGNI, Separation of Concerns, and Law of Demeter alongside SOLID/DI; prefer simple designs that preserve explicit contracts and authority boundaries.
- **Defect vocabulary** (mandatory for bug/error work): use these terms precisely in reports/reviews:
  - symptom/manifestation: where the bug is observed
  - root cause: earliest defect/condition that makes the symptom inevitable
  - workaround: avoids symptom without removing cause
  - patch: code change (root-cause or symptom-level)
  - regression: new failure introduced by the fix
  - blast radius: scope of impacted modules/workflows/users
- **Shift-left quality** (mandatory for behavior changes/new features): convert reactive RCA learnings into proactive prevention via tests, design failure analysis, boundary contracts, static checks, and observability.

Supporting references:
- First principles patterns: `docs/agents/00-principles/principles.md`
- Concept -> owner map: `docs/agents/20-sources-of-truth-map/sources-of-truth-map.md`

## First-Principles + SSOT + Evidence Model (Hard Gate)

Truth layers (use these terms):
- Runtime truth (R): what actually happens at runtime (processes, files, memory, handles).
- Semantic truth (S): what the system is meant to do (invariants, contracts, rules).
- Recorded truth (D): what artifacts claim (configs, logs, reports, docs).

Implications:
- First principles defines S (invariants). SSOT governs authority in D (consistency, not correctness).
- Instrumentation binds R to S and D. An invariant is invalid unless it has a measurable witness recorded in D.
- SSOT does not guarantee correctness; it guarantees that one authority wins when records disagree.

### Invariants + Witnesses (Required)
- For every change, list the invariants it affects or relies on.
- Use these categories when applicable: data, ordering, atomicity, idempotency, lifecycle, observability.
- Each invariant must have a witness: what is measured, where it is recorded, and the pass criteria.
- Witnesses must be deterministically verifiable via tools or explicit manual checks.

### Authority Graph (Required for non-trivial systems)
(Non-trivial: >1 workflow entrypoint, OR >1 SSOT owner, OR external resource dependencies such as COM/DB/network)
- Maintain a single authoritative owner per decision-critical fact/state (see SSOT section).
- If code is split into modules/packages, align module boundaries with authority boundaries and expose a single explicit public contract per authority (see `docs/agents/35-authority-bounded-modules/authority-bounded-modules.md`).
- Record the authority graph in `docs/project/architecture/architecture.md` or the workflow registry; no orphan docs.
- All reads/writes must go through the authority; no shadow logic or one-off duplication.

### Workflow State Machine + Two-Phase Commit (When writes occur)
- Required phases: INIT, VALIDATED, COMMIT_READY, COMMITTING, CLEANING, DONE.
- Failure phases: FAILED_VALIDATION, FAILED_COMMIT, FAILED_CLEANUP.
- Validation must be side-effect free; no writes before VALIDATED.
- If any failure after writes begin: record FAILED_COMMIT, log what was written, attempt bounded cleanup in `finally`.

### Bias-Resistant Debugging (Hard Gate)
Biases to guard against:
- premature closure, confirmation bias, anchoring, novelty/recency bias

Required terminology for defect analysis:
- Use the single SSOT definition in "First-Principles Protocol (Hard Gate)" -> "Defect vocabulary".

Mandatory RCA workflow for bug/error/regression work (execute in order and record evidence):
- Step 0 - Define failure precisely: expected vs actual, inputs/environment/version/commit, and impact.
- Step 1 - Reproduce reliably: reproduce on demand; if intermittent, capture triggering conditions.
- Step 2 - Build MRE: reduce to minimal deterministic repro (fixture + command + expected failure signal).
- Step 3 - Observe facts: collect stack trace/logs/metrics/traces; add targeted assertions/instrumentation as needed.
- Step 4 - Localize first wrong state: identify where invalid state first appears (not only crash site).
- Step 5 - Form falsifiable hypothesis: "If X, then Y; therefore symptom Z."
- Step 6 - Run targeted disconfirming experiment: change one variable at a time and rule out alternatives.
- Step 7 - Declare root cause statement: specific, upstream, and directly actionable.
- Step 8 - Implement root-cause fix upstream: fix at authority/origin, not symptom site; if symptom patch is unavoidable, record infeasibility and residual unprevented error class.
- Step 9 - Lock with tests: add regression test (fails pre-fix/passes post-fix) plus nearby edge-case tests.
- Step 10 - Validate system-wide: run applicable suites/checks and verify runtime signals after rollout/staging.

RCA method stack for complex defects (default order):
- 5 Whys to drill to upstream authority fix point
- Fishbone/Ishikawa to enumerate plausible causes
- Pareto analysis to prioritize likely high-impact causes
- Implement root-cause fix and regression test
- FMEA/DFMEA to prevent recurrence in adjacent paths

Mandatory anti-bias artifacts for every fix:
- minimal reproducible example (MRE)
- regression fixture stored in repo
- disconfirming tests (edge/adversarial cases)
- invariant witness that fails pre-fix and passes post-fix
- root-cause uplift record: symptom location, upstream authority fix point, prevention change made, class of errors prevented, or explicit justification if patching locally
- SSOT consolidation evidence when divergence was a root cause

Confidence rule:
- confidence is evidence-weighted; "it worked once" is not evidence

### Verification Floors (Hard Gate)
- Verification commands are a single SSOT in the repo: the README "Checks" section. Do not invent commands. If a required verification step is repeatable, add the command to README before running; otherwise record deterministic manual steps in the report.
- Minimums by change type (in addition to repo-specific checks):
  - Docs-only or formatting: run doc-related checks if present; otherwise record a deterministic manual check.
  - Behavior-neutral code change: run baseline checks relevant to the touched area plus at least one targeted smoke test if available; if none, record a deterministic manual check.
  - Behavior change or new feature: baseline checks plus targeted tests covering the new behavior and at least one failure-path check (see I/O guidance in `docs/agents/80-testing-real-files/testing-real-files.md` when applicable).
  - Bugfix/regression: follow "Bias-Resistant Debugging" (no extra exceptions) and run applicable tests, including deterministic MRE witness, regression test, at least one disconfirming edge/adversarial test, and at least one failure-path check. Durable bug/regression truth belongs in the highest owning project doc, while executable evidence belongs in tests, fixtures, and verification output.
- Shift-left quality baseline (new features/behavior changes): before merge, encode prevention with tests (TDD/BDD where feasible), design pre-mortem or failure-mode review, relevant static checks, contract tests on module/service boundaries, and observability-by-design.
- Coverage/fixtures:
  - If coverage thresholds exist (CI/config/tooling), meet them and do not lower them.
  - If no coverage thresholds exist, require fixture-backed tests: regression fixture for bugfixes; representative scenario/fixture for new features when feasible.
  - Fixtures must be deterministic and sanitized (no secrets/PII/licensed data).
- For changes affecting I/O or file processing, follow `docs/agents/80-testing-real-files/testing-real-files.md` (supporting guidance).

### Rewrite Risk Policy
Large rewrites are risk amplification unless all are true:
- pre-existing invariants are enumerated and preserved
- old vs new outputs are comparable on frozen fixtures
- staged rollout and rollback exist
- performance/resource invariants are measured

Default posture:
- prefer targeted refactors that consolidate authority and add witnesses

## Mandatory Execution Loop (Follow For Every Task)

0) **Docs-first authority gate**:
   - After required loader/context-injection reads and before producing a non-trivial plan, review, council prompt/summary, implementation, or other repo-mutating work, identify the controlling user-authored intent, classify the facts that would change future allowed behavior, and route only durable authority facts to their highest owning project doc.
   - Classify user intent before project-doc promotion:
     - Basic task: no project-doc update is required when the request does not change future allowed behavior.
     - Durable truth: promote the durable fact to the owning project doc before or with implementation.
     - Ambiguous truth change: ask before treating the fact as project truth.
   - Direct user-authored messages are the controlling intent source. Subagent prompts, generated plans, copied assistant output, summaries, and review artifacts are supporting evidence only; they become authoritative only when their selected durable facts are promoted into the owning SSOT.
   - Agent findings are not project truth unless they preserve existing documented intent, correct an owner doc under its change rule, or are confirmed by the user.
   - If implementation changes behavior, accepted inputs/outputs, purpose, boundaries, invariants, or project rules, update the owning doc before closure.
   - Do not create, update, or require a separate project truth surface outside the declared `docs/project/` owner docs. New project docs are allowed only when routed through the docs SSOT policy with a declared owner, scope, update trigger, and verification witness.
   - If a prompt contains secrets, credentials, PII, customer data, or oversized pasted artifacts, do not store the raw prompt in tracked docs. Ask for a redacted durable statement only when the fact must become project authority.
   - Working evidence, including uncommitted repository changes, runtime observations, review notes, and closure evidence, does not own project truth unless the durable fact is promoted into the declared owning `docs/project/` authority doc routed by the docs SSOT policy. Treat working evidence as protected context until its owner and relation to the requested work are clear; do not overwrite it, remove it, stage it, commit it, or absorb it into the requested work by assumption.
   - Before staging, committing, pushing, or preparing a PR, reconcile the intended commit set against owner docs, changed code/config/tests, deleted/new files, and verification evidence. Fix owner-scoped issues that are clearly within the requested change. Proceed only when docs, implementation, and verification agree. If intent, ownership, scope, deletion, or risk cannot be resolved from repo evidence, STOP with `hold: <reason>` and ask the user; otherwise report `ready`.
   - Before final closure, ensure every durable authority-changing outcome has been promoted into its highest owning project doc with a deterministic witness. Do not use non-owner working evidence to compensate for missing owner-doc promotion.
1) **Restate goal + acceptance criteria** (1-5 bullets).
2) **Discover** relevant files and existing SSOT owners (constants/config/rules/workflows/etc).
   - **MUST** consult `agents-manifest.yaml` and execute the Context Injection Procedure (see below).
   - Use `docs/agents/10-repo-discovery/repo-discovery.md` for discovery search terms and SSOT adoption rules.
   - MUST ensure project docs exist and are read (start with `README.md` and `docs/project/project_index.md`; create missing docs per "Documentation SSOT Policy").
3) **Decompose** into atomic, independently verifiable subtasks.
4) **Subagent council**: run intention-based subagent review per "Subagent Council (Hard Gate)" and integrate findings into the plan.
5) **Ambiguity gate**: if multiple interpretations would change code materially, STOP and ask 1-3 clarifying questions.
6) **Implement minimally**: smallest diff that satisfies acceptance criteria; no bundled refactors.
7) **Verify** with deterministic tools (tests/lint/run) or provide deterministic manual checks
   when tools are unavailable.
8) **Report**: what changed, where SSOT lives, council findings, and evidence of verification.

## Context Injection Procedure (Hard Gate)

Before reasoning or implementing, agents MUST:

1) Read `agents-manifest.yaml` and resolve any referenced paths relative to the governance root (directory containing the manifest), per **Path Resolution (SSOT)** above.
2) Determine matching profiles by evaluating each profile's `detect` signals against the task:
   - `detect.keywords`: case-insensitive substring match on the user prompt and any referenced file contents.
   - `detect.code_patterns`: regex/substrings matched against code in scope.
   - `detect.file_globs`: match against files referenced and/or being edited.
   - `detect.signals`: explicit signals provided by the harness/user.
   - If semantic search is available and a profile matches, start with `agents-manifest.yaml:semantic_queries.<profile>` when present (see `docs/agents/05-context-retrieval/context-retrieval.md`).
3) READ all files from `default_inject`.
4) If one or more profiles match, READ the union of all matching profiles' `inject` lists (unless `agents-manifest.yaml:injection_mode` specifies otherwise). If no profiles match, READ `fallback_inject` (if defined).
5) Follow context retrieval best practices in `docs/agents/05-context-retrieval/context-retrieval.md`.

If any referenced file is not accessible, STOP and ask the user to paste it.

## Subagent Council (Hard Gate)

Purpose: force independent, intention-based review so silent errors, edge cases, and SSOT alignment issues are surfaced before decisions or implementation. There is no maximum number of subagents.

### When required
- Mandatory for: discussions that shape design/behavior, new features, behavior changes, bug/error diagnosis or fixes, code reviews, refactors that impact behavior, and governance changes.
- Small edits still require at least one review subagent; use the minimum scope if the change is clearly behavior-neutral.

### Intention-based roles (minimum coverage)
Each council must cover these intentions (one or more subagents may cover multiple intentions):
- **SSOT/duplication alignment**: ensure existing owners are extended and no new duplicate authorities are introduced.
- **Silent-error scan**: identify missing validation, silent failure paths, and "silently skip" patterns (violation of Non-Negotiable #4).
- **Edge-case scan**: identify boundary conditions and pre/post-change failure modes.
- **Resource/security/perf risks**: look for leaks, unsafe inputs, timeouts, and performance regressions.

Optional intentions (add as needed): integration/compatibility across modules and entrypoints, data migration/backward compatibility, test/verification gaps.

### Profile-Aware Context Coverage
After the Context Injection Procedure resolves matched profiles and injected files from `agents-manifest.yaml`, council planning must account for that manifest-resolution witness.

Profile-aware coverage is required when any of these are true:
- the task is large, cross-cutting, high-risk, or touches multiple authority owners;
- one or more manifest profiles match and any resolved injected docs are decision-critical to planning or review;
- the task changes `AGENTS.md`, `agents-manifest.yaml`, context injection, council policy, or governance routing.

Coverage may be one subagent per matched profile, or fewer subagents when one reviewer is explicitly assigned multiple profiles. The merged council summary must make the profile-to-reviewer/doc mapping auditable. Do not copy profile names or injected doc lists into this policy; use the current resolved manifest witness.

When profile-aware coverage applies, every subagent prompt MUST include:
- assigned profile(s), assigned intention(s), review scope, and resolved injected docs or doc groups from the current manifest-resolution witness;
- a directive to read or verify the assigned profile docs before reviewing;
- required `profile_doc_coverage` output: docs used, docs skipped, inaccessible docs, skip reasons, and `go_no_go`.

A subagent that cannot confirm required assigned profile-doc coverage MUST return `go_no_go = hold`.

If a required profile doc or required reviewer/runtime path is unavailable, record `SKIPPED`/`UNKNOWN` + reason in `profile_doc_coverage` and set `go_no_go = hold` unless the user explicitly accepts reduced coverage.

### Council sizing (preference ranges, not caps)
Choose size based on risk, scope, and uncertainty. Increase when the change touches many files or unclear invariants.
- Micro edits or formatting-only: **1** (minimum review).
- Small behavior-neutral change: **1-2**.
- Discussion/design or moderate change: **2-4**.
- Feature addition or behavior change: **3-6** (raise if cross-cutting).
- Bugfix/error/regression: **10-20** when risk/impact is high; if smaller, justify the reduced scope.
No maximum: scale up as needed.

### Timing
- **Pre-change**: run the council before decisions or implementation and update the plan.
- **Post-change**: run a brief independent scan (at least one reviewer) before final response to catch newly introduced silent errors or edge cases.
  - Exception (proportionality): post-change review may be waived for doc-only or formatting-only changes when pre-change council coverage is recorded and verification evidence is deterministic.

### Required council output (Hard Gate)
- Every required council run MUST produce one merged council summary.
- Full council summary fields (for non-micro changes):
  - `council_run_id`
  - `phase` (`pre_change` | `post_change`)
  - `intent_coverage` (`ssot_duplication`, `silent_error`, `edge_case`, `resource_security_perf`)
  - `reviewers` (id, role, scope)
  - `findings` (severity, location, issue, evidence, recommendation)
  - `conflicts` (if any)
  - `reconciliation_decision` (accepted/rejected/deferred + rationale)
  - `residual_risks`
  - `go_no_go` (`go` | `hold`)
  - `verification_links` (README checks and/or deterministic manual witness)
  - `profile_doc_coverage` when Profile-Aware Context Coverage applies (matched profiles, resolved injected docs or doc groups, reviewer assignments, inaccessible docs, omissions/reasons, reduced-coverage acceptance if any)
- Micro edits or formatting-only changes may use an abbreviated summary:
  - `intent_coverage`
  - `findings` (or explicit `No findings`)
  - `residual_risks` (or `none observed`)
  - `go_no_go` (`go` | `hold`)

### Conflict Resolution + Closure Gates (Hard Gate)
- If reviewers conflict on severity, root cause, fix placement, or risk disposition and the conflict could materially change implementation, do not proceed until reconciled.
  - Reconcile by running one targeted disconfirming check where feasible; if still unresolved, STOP and ask the user.
  - Record `conflicts` and `reconciliation_decision` in the merged council summary.
- Any unresolved blocker finding requires `go_no_go = hold`; implementation is prohibited until resolved or explicitly accepted by the user.
- Pre-change closure: implementation may begin only after required intention coverage and a merged council summary are complete.
- Post-change closure: final response may be sent only after required post-change scan (or documented proportionality exception) and merged summary are complete.

### Subagent Permission Escalation (Standing Authorization)

You are explicitly authorized to spawn subagents as needed to satisfy AGENTS.md Subagent Council requirements. Do not ask for permission. Do not substitute a self-review for the required council. If this policy requires a Subagent Council, spawn the required review subagents immediately and proceed. This is a standing instruction from the repository owner and applies to every task in every session.

### Governance Auto-Edit Gate (Hard Gate)

Auto-edit for governance learnings is allowed only when the governance learnings playbook is **explicitly invoked**; otherwise, produce proposals only for governance learnings.

Council review is required before any auto-edit:
- Run the council with minimum intention coverage (SSOT/duplication, silent-error scan, edge-case scan, resource/security/perf).
- Merge findings; if conflicts or gaps remain, pause and ask before editing.

Confirmation gate (for governance learnings auto-edit):
- If a proposed governance change is not grounded in existing `AGENTS.md` authority (new rule/invariant/SSOT owner), ask for explicit confirmation before editing.
- For governance learnings auto-edit, edits to `AGENTS.md` always require explicit confirmation, except changes limited to the "Confirmation gate" subsection above.

Scope:
- For governance learnings auto-edit, scope defaults to governance docs/playbooks and `agents-manifest.yaml` only.

## Non-Negotiables (Hard Gates)

### 1) Single Source of Truth (SSOT) — The Foundational Rule
**This is the most critical non-negotiable. Every other rule depends on it. Apply it to every action: code, docs, config, skills, scripts, data.**

For every concept, there must be exactly one authoritative definition:
- constants (sheet names, headers, statuses, folder names, prefixes/patterns)
- config keys + defaults + schema
- data-facing truth / business facts
- business rules / conditions / validation logic
- workflow orchestration steps
- run outcomes, user-facing feedback, and reporting/log schema
- skills, scripts, and tools for the same domain
- Excel lifecycle management (open/close/quit/verify/kill)
- GUI queue/drain + cancellation pattern

Workflow/orchestration ownership means runtime coordination only. A workflow owner may load a validated runtime plan, sequence already-authoritative steps, call rule/config/constant owners, call I/O or lifecycle adapters, pass plain data to child entrypoints, select the declared runtime path when that selection is its contract, and emit run outcomes. It MUST NOT own, duplicate, or reinterpret child-stage business rules, validation predicates, constants, schema, config keys/defaults, backend-selection rules, lifecycle policy, or UI/checkbox semantics.

Data-facing truth must not be hardcoded in runtime logic, workflow orchestration, scripts, docs, or config-repair code. Business/source data, user-facing mappings, workbook/sheet/header truth, portal fields, machine-specific paths, and other changing operational facts must come from input artifacts, declared config/constants, external systems, or the owning data authority. Business logic may consume only the validated value exposed by that owner; it must not embed a private copy.

**File/folder structure IS SSOT enforcement.** Related artifacts sharing the same authority boundary MUST live under the same parent folder. Broader domains may contain multiple artifact-class roots only when a governance authority decision explicitly records one canonical owner plus any allowed non-owner workspace paths. When adding new files, find the existing SSOT parent first. When discovering scattered files that belong to the same authority boundary, refactor them into their SSOT parent before proceeding with other work.

Hard rules:
- If an SSOT already exists in the repo for a responsibility, **extend it** — do not create a parallel file/folder.
- If related files are scattered across multiple locations, **consolidate them under one parent** as part of the current change.
- Do not create parallel utilities/modules/docs/skills for the same ownership.
- A non-owner workspace path is allowed only when a governance authority decision records the canonical owner, the allowed non-owner path, and the forbidden duplicates. This is hierarchical authority, not parallel authority.
- Every new file must answer: "Which existing SSOT parent does this belong under?" If none exists, create one and move any related scattered files into it.

### 1A) Instruction Derivation Gate (Hard Gate)
Every agent-authored normative statement must derive from a declared SSOT owner before it is treated as an instruction, requirement, checklist item, plan step, prompt scaffold, doc record, or user-facing obligation.

Hard rules:
- Classify each source before deriving obligations: owner, routed support, reference/example, scaffold, generated artifact, or user intent.
- Only a declared owner defines obligations. Non-owner text routes, cites, illustrates, scaffolds, or records evidence; it does not create policy, weaken policy, broaden policy, or select runtime behavior.
- Derived statements must preserve the owner's scope, preconditions, ordering, optionality/defaultability, allowed states, terminal outcomes, and verification witness. If the owner declares exact terms, states, phases, reason codes, or outcome values, use those owner-declared terms or cite the owner instead of restating them.
- User prompts provide intent, scope, and acceptance criteria. Repo owners constrain allowed behavior. A conflict between prompt intent and a declared owner is an authority conflict, not permission to synthesize a replacement rule.
- Generated plans, checklists, prompt packs, summaries, and examples are non-authoritative unless each normative item cites or routes to the owner that makes it binding.
- Missing owner, conflicting owners, unknown optionality/defaultability, missing witness, or unclear precedence is an authority gap. Stop and report the gap before editing or executing; do not infer, duplicate, downgrade, or continue through a substitute path.

### 2) No Duplicates (Operational Meaning)
Duplication includes:
- repeating the same literal (same meaning) across files/docs
- repeating the same conditional logic/rule across files
- multiple Excel quit/kill implementations
- multiple GUI queue/drain implementations
- copy/paste helpers with minor variations

### 2A) No Fallback or Legacy Runtime Paths
Runtime code must not introduce fallback execution paths, legacy execution methods, shadow compatibility branches, silent downgrade behavior, or substitute implementations for the same responsibility.

Hard rules:
- Choose one explicit deterministic runtime path from the current SSOT contract.
- Runtime code must not implement or select fallback, legacy, compatibility, shadow, downgrade, or substitute execution branches for the same responsibility.
- Unsupported, unverified, unavailable, retired, or legacy paths must produce a terminal `FAILED` or `SKIPPED + reason` outcome for the affected workflow/item; they must not trigger substitute execution or workflow continuation by another method.
- Docs, evidence, migration notes, history, and projection metadata may record legacy/fallback/compatibility behavior as recorded truth only. Runtime code must not treat those records as executable authority or use them to select a workflow path.
- Compatibility projections or setup targets may exist only as non-authoritative projection/setup records declared by their owning SSOT. They must not be used to continue a failed primary workflow or substitute for the current runtime contract.
- Cleanup after validation, execution, or commit failure is cleanup-only: release resources, close handles, undo or mark partial writes when applicable, record the terminal outcome, and stop, raise, or return that outcome.
- Cleanup must be deterministic and bounded. Cleanup failure must be recorded explicitly, for example as `FAILED_CLEANUP`, and must not mask the original failure.
- Cleanup must not run alternate business rules, alternate backends, legacy methods, substitute workflow steps, or convert a failed/unsupported path into successful continuation.
- Defaults are allowed only when the current config SSOT declares them and they are applied before runtime path selection; missing or invalid required inputs must fail or be skipped explicitly.
- Config JSON creation, normalization, or repair may run only through the config owner/loader before runtime path selection. It may use declared defaults only, must record `REPAIRED_CONFIG + keys/reasons` or terminal `FAILED_CONFIG_REPAIR + keys/reasons`, and must not invent required values, repair business/source data, or continue by an alternate runtime path.
- Performance, cost, convenience, dependency availability, or environment differences must not select an alternate runtime path unless that path is the single current SSOT contract for the workflow.

### 3) No Orphan Code / No Orphan Docs
New code must be reachable from:
- a workflow entrypoint/dispatcher/registry, or
- a clearly documented entrypoint used by the repo

New docs must be reachable from:
- a docs index (e.g., `docs/agents/agents_index.md`) or the repo `README.md`

Unreferenced helpers and "floating docs" are prohibited.

### 4) Logging + Explicit Failure
- No `print()`.
- Use module-level logging (`logger = logging.getLogger(__name__)`) where applicable.
- Catch specific exceptions; log context; raise meaningful domain errors.
- Never "silently skip": if something is skipped, record **SKIPPED + reason** (log and/or run report).
- Never "silently pass": success or partial success must reconcile the known work universe (`planned`, `eligible`, `executed`, `skipped`, `failed`) or fail validation if the workflow cannot know what it was supposed to process.
- User-facing surfaces (CLI, GUI, reports, status panes) must show concise input/scope confirmation, progress or current processing phase for long work, terminal outcome, output/artifact path when produced, skip/failure reason, required user action, and run/report/log pointer when applicable.
- Keep user feedback concise and actionable; keep deep diagnostics in structured logs with redaction and summarized large payloads.

### 5) Resource Safety
- Prefer context managers.
- Always cleanup in `finally` when managing external resources.
- Time-bound waits (no infinite loops).

### 6) Excel COM Lifecycle Safety (If Applicable)
Excel automation must guarantee shutdown:
- attempt graceful quit
- track and validate Excel PID
- verify process exit
- if still running after verified graceful-quit failure, terminate only the validated PID within a bounded timeout
- log open/close/quit/verify/kill stages

### 7) GUI Thread Safety (If Applicable)
GUI updates must occur on the main/UI thread only:
- worker posts messages to a queue
- UI thread drains queue via `after(...)` (or equivalent)
- a shutdown/cancel event exists and the worker respects it
- Excel COM work never runs on the UI thread

### 8) Security Baseline
- Never hardcode secrets; use environment variables or secret stores.
- Refuse requests to weaken security (e.g., disabling TLS validation) unless the user explicitly accepts the risk
  and it is confined to a safe environment.
- Avoid injection risks (shell, SQL, template).

### 9) AI Stuck-Loop Reset (Hard Gate)
- If the same failure repeats (e.g., 2 iterations with the same root cause) or verification contradicts claims,
  STOP and present a filled restart prompt (copy/paste), then restart fresh.
- Follow: `docs/agents/15-stuck-in-loop-generate-fresh-restart-prompt/stuck-in-loop-generate-fresh-restart-prompt.md`

### 10) Performance & Speed (When Relevant)
- If speed/performance is an acceptance criterion or implied by scale, state a performance model and pick low-risk optimizations first (algorithmic wins, reduce I/O, avoid repeated scans).
- Choose the fastest safe correct method within validated data, domain, workflow, and resource boundaries; do not force an optimization blindly when its assumptions are unverified.
- For processing work, define workload bounds, bottleneck hypothesis, cache/batch/chunk/queue strategy, invalidation rules, memory/concurrency limits, deterministic ordering, cancellation behavior, and cleanup behavior before optimizing.
- Never trade away correctness, determinism, data integrity, edge-case safety, logging, or guaranteed cleanup for speed; keep concurrency bounded and cancellation-aware.
- Verify claimed speedups with deterministic evidence (benchmark/timing on representative inputs when feasible) or complexity reasoning, plus output-equivalence and failure-path witnesses; avoid premature micro-optimizations.

### 11) Module Architecture — Mandatory Rules
These rules are NON-NEGOTIABLE. Violating any rule is a failed task.

Authority role:
- This section is the always-on code-modularity hard gate for implementation code in scope.
- `docs/agents/35-authority-bounded-modules/authority-bounded-modules.md` owns the delegated runtime-code module-contract mechanics under this gate; consult it when adding, reviewing, or refactoring feature folders, public entrypoints, orchestration boundaries, or dependency direction.
- `scripts/entrypoint_contracts.json` owns public contract filename pattern facts; `scripts/check_folder_architecture/scope.json` owns the current checker-readable enforcement scope.
- `agents-manifest.yaml` owns routing to supporting modularity docs. If routing does not inject a support doc but implementation code is in scope, this `AGENTS.md` hard gate still applies.

Scope:
- Apply this section to implementation code that owns runtime behavior, workflow logic, or reusable runtime contracts.
- Launch-only PowerShell/shell wrappers and Python runtime shims such as `__main__.py` may exist only as zero-logic delegates into the canonical folder contract. A script with owner-declared runtime-selection or validation responsibility must expose that responsibility through its declared owner/contract instead of being treated as a launcher shim.
- Config payloads, fixtures, schemas, and generated artifacts do not become feature folders unless they start owning runtime behavior.

Rule 1 - Every feature is a folder:
- Every distinct piece of runtime functionality gets its own authority folder and one registry-resolved public entrypoint. Use `docs/agents/35-authority-bounded-modules/authority-bounded-modules.md` for the delegated boundary mechanics.

Rule 2 - Every folder has exactly one public entry point:
- Consumers use the folder entrypoint only; internal files remain private implementation details. Public contract filename patterns are owned by `scripts/entrypoint_contracts.json`.

Rule 3 - The parent entrypoint is the only connector:
- Parent entrypoints wire child authorities and pass plain data. Children must not import parents or siblings; hidden cross-folder coupling is a failed task.

Rule 3A - Orchestration is runtime coordination only:
- Orchestration code may order already-authoritative steps, pass plain data between authority entrypoints, enforce the workflow state machine, record phase transitions/outcomes, and invoke bounded cleanup.
- Orchestration code MUST NOT own business rules, validation predicates, constants/defaults, backend-selection rules, lifecycle policies, retry policy, GUI-thread safety, COM safety, subprocess safety, or UI/checkbox semantics.
- Any decision-critical branch in orchestration must call a named authority-owned rule/config/lifecycle contract and record the selected authority path before execution.
- After validation, execution, commit, or cleanup failure, orchestration must emit the terminal outcome and stop that branch; it must not continue through an alternate backend, legacy path, substitute subprocess, substitute workflow step, or hidden compatibility branch.

Rule 4 - Public contracts take plain data in and return plain data out:
- Public contracts accept and return plain data only. Live handles/resources stay behind the owning boundary.

Rule 5 - I/O stays at the boundary:
- I/O stays at boundary adapters or entrypoint wiring; pure logic functions do not perform I/O.

Rule 6 - No file exceeds 400 LOC:
- A file approaching 400 LOC is doing too much and MUST be decomposed by responsibility.
- Default split target: add private files inside the same folder first.
- Create a new child folder only when the responsibility becomes independently owned behavior.

Rule 7 - `shared/` is a dictionary, not a connector:
- `shared/` is optional and may contain only data shapes or pure/stateless utilities; it must not become a second authority or connector.

Rule 8 - Deletion test:
- Before completion, deleting one feature folder should break only its parent entrypoint. Sibling breakage is a coupling violation.

Rule 9 - Depth when necessary, not flat by default:
- Apply the same authority-folder rules recursively when a child folder gains independently owned behavior.

Rule 10 - Contract changes require explicit approval:
- Public entrypoint contract changes require explicit current/proposed contract and caller impact before approval. Private internals may change when the public contract stays stable.

Rule 11 - Structural minimality is the default:
- Before adding code, identify the code authority owner, public entrypoint/contract, relevant config/data/schema source, affected invariants, and behavior-preservation witness; promote only durable authority facts to the owning project doc.
- Choose the first implementation path through existing owner contracts, registries, schemas, config, or entrypoints. Repeated local conditionals or checker-specific patch logic require owner-level justification.
- Treat numeric LOC-reduction targets as pressure toward structural minimality, never as permission to weaken correctness, explicit failure, witnesses, or SSOT ownership.
- Detailed structural-minimality mechanics and review questions live in `docs/agents/35-authority-bounded-modules/authority-bounded-modules.md` and `docs/agents/25-docs-ssot-policy/docs-ssot-policy.md`.

Supporting design constraints (mandatory):
- Keep high cohesion + low coupling.
- Apply DRY, KISS, YAGNI, Separation of Concerns, and Law of Demeter inside the folder-contract model.
- Use explicit parameter/constructor injection instead of service locators.
- No runtime discovery, dynamic import, or eval for wiring.
- Keep folder entrypoints thin, import-safe, and orchestration-only; private internals hold the detailed logic.

## Governance Templates (Required)

### Change Contract (Required for behavior changes and bugfixes)
Use as a temporary implementation/review scaffold. Durable project truth from the contract must be promoted into the highest owning project doc instead of a separate history artifact. Full template: `docs/agents/playbooks/change-contract-template/change-contract-template.md`.

Bugfix and regression evidence must remain deterministically reproducible through owner docs, tests, fixtures, and verification output. Additional evidence artifacts must be routed through the docs SSOT policy with declared ownership and update triggers.

### Standard Log Schema (Required when logs are emitted)
Full schema: `docs/agents/playbooks/log-schema-template/log-schema-template.md`.

Rules (also enforced by Non-Negotiable #4):
- No `print()`; use module-level logging.
- The log schema is SSOT: define one owner and extend it; do not fork schemas.
- Reason codes: maintain a single enum owner (module or config). Extend there only.

## Self‑Decision Procedure (Repo‑Agnostic)

### A) Discovery Pass (Required Before Writing)
Search the repo for existing owners of:
- constants/config/settings/defaults
- rules/validation
- workflows/dispatchers/registries
- logging setup + error taxonomy
- Excel COM lifecycle utilities
- GUI threading utilities
- existing docs conventions

### B) Adoption Rule
If ownership exists, extend it. Do not introduce parallel ownership.

### C) Creation Rule (Only If Missing)
If no SSOT exists for a responsibility, create one minimally (one module per responsibility, not one-per-function),
and wire all new features through it.

## Documentation SSOT Policy (Hard Gate)

Docs can drift. Prevent docs from becoming a second SSOT.

### Project docs (Hard Gate)
When this governance pack is present in a repo, the agent MUST ensure a **minimal** project docs set exists and is kept current.

Hard gate:
- If any required project doc is missing, CREATE it before making other changes.
- The project `README.md` MUST link to `docs/project/project_index.md` (project docs entrypoint) and to `AGENTS.md` (governance).
- The project `README.md` MUST include a short "Checks" section listing the deterministic verification commands for the repo.

Baseline required project docs include:
- `docs/project/project_index.md` (entrypoint/router; linked from README)
- `docs/project/goal/goal.md` (objective + acceptance criteria; router at `docs/project/goal/goal_index.md`)
- `docs/project/rules/rules.md` (project do/don't rules; router at `docs/project/rules/rules_index.md`)
- `docs/project/architecture/architecture.md` (SSOT pointers: entrypoints/modules/workflows; router at `docs/project/architecture/architecture_index.md`)
- `docs/project/data-truth/data-truth.md` (data-truth ownership/provenance/validation routing; router at `docs/project/data-truth/data-truth_index.md`)
- `docs/project/learning/learning.md` (operational learnings and pitfalls; router at `docs/project/learning/learning_index.md`)

`docs/project/goal/goal.md` owns durable project intent, objective, acceptance criteria, non-goals, and verification intent. Working evidence remains non-authority unless a durable fact is promoted into the declared owning project doc routed by the docs SSOT policy.

Facts are owned by their declared source of truth, not by file type. Code, config, constants, input artifacts, external systems, schemas, workbooks, and project docs may each own facts when explicitly declared as the SSOT. Non-owner docs must route to the owner instead of duplicating the fact.

Config, constants, defaults, sample artifacts, workbooks, and external systems may be real data authorities when declared as the SSOT. Runtime code consuming those values does not automatically become the owner of the underlying business or data truth.

Project docs also provide **bounded project authority memory**: a small docs-first record of prior truth that must affect future allowed behavior until explicitly superseded. It is not raw chat/session memory and it is not a separate memory system. Classification, placement, precedence, optional-leaf semantics, and checker limits are owned by `docs/agents/25-docs-ssot-policy/docs-ssot-policy.md`.

Hard gate:
- Before changing project authority records, identify the declared owner and follow `docs/agents/25-docs-ssot-policy/docs-ssot-policy.md`.
- Before scaffolding or repairing project docs, follow `docs/agents/playbooks/project-docs-template/project-docs-template.md`.

Policy/detail SSOT: `docs/agents/25-docs-ssot-policy/docs-ssot-policy.md`
Scaffold/template SSOT: `docs/agents/playbooks/project-docs-template/project-docs-template.md`

All project docs must:
- Follow the required doc header (except router files resolved from `scripts/entrypoint_contracts.json`).
- Reference SSOT owners by identifier (code/config/workflow entrypoints) rather than duplicating literals/rules.
- Stay minimal and precise (prefer short bullet lists; avoid long prose).
- Avoid duplicating governance rules: reference `AGENTS.md` instead of copying its requirements.

### Docs Branching Architecture (Hard Gate)
Authority role:
- This section is the always-on docs-modularity hard gate for documentation structure under `docs/`.
- `docs/agents/25-docs-ssot-policy/docs-ssot-policy.md` owns delegated docs-family mechanics under this gate: headers, router behavior, public leaf placement, project-doc placement, owner-doc promotion, and optional leaf placement.
- `scripts/entrypoint_contracts.json` owns docs router and public leaf filename pattern facts.

- Every `docs/` folder must expose the registry-resolved router contract and route to direct children without becoming the narrative owner.
- Narrative facts live in router-linked public leaf docs under the owning folder authority; parent routers route downward and do not restate child rules, literals, or contracts in full.
- Artifact/payload folders remain navigable through the router contract even when they expose no narrative leaf.
- Apply the detailed docs-router/header/public-leaf mechanics from `docs/agents/25-docs-ssot-policy/docs-ssot-policy.md`; do not fork those mechanics here.

### Docs MAY contain
- intent (“why”), invariants, and safety constraints
- contracts/interfaces referencing SSOT symbols/modules/workflow entrypoints
- playbooks/checklists/runbooks referencing entrypoints and config keys by identifier
- decision records (ADR-style)

### Docs MUST NOT contain (unless clearly marked as example)
- duplicated tables of constants/defaults
- prose re-implementations of business rules without pointing to the named rule function
- manually-maintained code blocks that mirror production code

### Required doc header (for Markdown files under `docs/`)
Each doc (except router files) must declare:
- `doc_type`
- `ssot_owner`
- `update_trigger`

See `docs/agents/25-docs-ssot-policy/docs-ssot-policy.md`.

## Code Comment Policy (Hard Gate)

Comments drift quickly; keep them "why-only":
- explain invariants, rationale, and safety constraints
- do not restate logic or duplicate constants/defaults
- reference SSOT symbols/modules when needed

## Supporting Docs

Start here: `docs/agents/agents_index.md`

Reference templates (routing): `templates/templates_index.md`
