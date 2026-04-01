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

## Governance Pack Layout (When Vendored)

When this pack is installed as a submodule under `.governance/` in a target repo:
- `.governance/AGENTS.md` is authoritative; root `AGENTS.md`, `CLAUDE.md`, `.cursorrules`, and `.github/copilot-instructions.md` are project-owned overlays that must direct readers to the governance root.
- The context injection manifest lives at `.governance/agents-manifest.yaml`.
- Governance docs and scripts live under `.governance/docs/agents/` and `.governance/scripts/`.
- Project-specific docs remain at `docs/project/` in the target repo.

## Path Resolution (SSOT)

All paths in this governance pack are written relative to a root. Resolve paths as follows:
- Governance root: the directory containing this `AGENTS.md` and `agents-manifest.yaml`. Unless explicitly marked as project-root, all governance paths (e.g., `docs/agents/...`, `docs/agents/playbooks/...`, `scripts/...`, `./README.md`) are resolved relative to this root.
- Project root: the target repo root into which the pack is vendored (parent of `.governance/` when used as a submodule). Paths under `docs/project/...` and `README.md` (project README) are resolved relative to the project root.
- When vendored as `.governance/`, governance-root paths resolve under `.governance/` without rewriting the path strings in docs or manifests.

## Submodule Workflow Rules (Hard Gate)

The governance pack source repo is: `https://github.com/parmartejass/AGENTS.MD.git`

When editing files inside `.governance/`:
1. **NEVER** commit `.governance/` changes from the parent repo directory.
2. **ALWAYS** go INTO the submodule first: `cd .governance`
3. **ALWAYS** checkout and pull main before making changes: run `git checkout main`, then `git pull origin main`
4. Create a branch, commit, and push to the **submodule repo** (parmartejass/AGENTS.MD).
5. Create PR in the submodule repo, merge to main.
6. Return to parent repo and update the pointer: `git submodule update --remote .governance`

The parent repo only stores a pointer (SHA) to a commit in the submodule—it cannot store file changes.

See `./README.md` section "Editing governance (from inside a project)" for exact commands.

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
  - Bugfix/regression: follow "Bias-Resistant Debugging" (no extra exceptions) and run applicable tests, including deterministic MRE witness, regression test, at least one disconfirming edge/adversarial test, and at least one failure-path check; when artifact-based verification is enabled, store evidence in `docs/project/change-records/*.json` using `docs/agents/schemas/change-record.schema.json`.
    Artifact-based verification is enabled when `docs/project/change-records/.required` exists or `scripts/check_change_records.ps1` is run with `-RequireRecords`.
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

1) **Restate goal + acceptance criteria** (1-5 bullets).
2) **Discover** relevant files and existing SSOT owners (constants/config/rules/workflows/etc).
   - **MUST** consult `agents-manifest.yaml` and execute the Context Injection Procedure (see below).
   - Use `docs/agents/10-repo-discovery/repo-discovery.md` for discovery search terms and SSOT adoption rules.
   - MUST ensure project docs exist and are read (start with `README.md` and `docs/project/index.md`; create missing docs per "Documentation SSOT Policy").
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
- business rules / conditions / validation logic
- workflow orchestration steps
- skills, scripts, and tools for the same domain
- Excel lifecycle management (open/close/quit/verify/kill)
- GUI queue/drain + cancellation pattern

**File/folder structure IS SSOT enforcement.** Related artifacts sharing the same authority boundary MUST live under the same parent folder. Broader domains may contain multiple artifact-class roots only when a governance authority decision explicitly records one canonical owner plus any allowed non-owner workspace paths. When adding new files, find the existing SSOT parent first. When discovering scattered files that belong to the same authority boundary, refactor them into their SSOT parent before proceeding with other work.

Hard rules:
- If an SSOT already exists in the repo for a responsibility, **extend it** — do not create a parallel file/folder.
- If related files are scattered across multiple locations, **consolidate them under one parent** as part of the current change.
- Do not create parallel utilities/modules/docs/skills for the same ownership.
- A non-owner workspace path is allowed only when a governance authority decision records the canonical owner, the allowed non-owner path, and the forbidden duplicates. This is hierarchical authority, not parallel authority.
- Every new file must answer: "Which existing SSOT parent does this belong under?" If none exists, create one and move any related scattered files into it.

### 2) No Duplicates (Operational Meaning)
Duplication includes:
- repeating the same literal (same meaning) across files/docs
- repeating the same conditional logic/rule across files
- multiple Excel quit/kill implementations
- multiple GUI queue/drain implementations
- copy/paste helpers with minor variations

### 3) No Orphan Code / No Orphan Docs
New code must be reachable from:
- a workflow entrypoint/dispatcher/registry, or
- a clearly documented entrypoint used by the repo

New docs must be reachable from:
- a docs index (e.g., `docs/agents/index.md`) or the repo `README.md`

Unreferenced helpers and "floating docs" are prohibited.

### 4) Logging + Explicit Failure
- No `print()`.
- Use module-level logging (`logger = logging.getLogger(__name__)`) where applicable.
- Catch specific exceptions; log context; raise meaningful domain errors.
- Never "silently skip": if something is skipped, record **SKIPPED + reason** (log and/or run report).

### 5) Resource Safety
- Prefer context managers.
- Always cleanup in `finally` when managing external resources.
- Time-bound waits (no infinite loops).

### 6) Excel COM Lifecycle Safety (If Applicable)
Excel automation must guarantee shutdown:
- attempt graceful quit
- track and validate Excel PID
- verify process exit
- kill fallback only with validated PID and bounded timeout
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
- Never trade away correctness, determinism, data integrity, edge-case safety, logging, or guaranteed cleanup for speed; keep concurrency bounded and cancellation-aware.
- Verify claimed speedups with deterministic evidence (benchmark/timing) or complexity reasoning; avoid premature micro-optimizations.

### 11) Module Architecture — Mandatory Rules
These rules are NON-NEGOTIABLE. Violating any rule is a failed task.

Scope:
- Apply this section to implementation code that owns runtime behavior, workflow logic, or reusable runtime contracts.
- PowerShell/shell launchers and Python runtime shims such as `__main__.py` may exist only as zero-logic delegates into the canonical folder contract.
- Config payloads, fixtures, schemas, and generated artifacts do not become feature folders unless they start owning runtime behavior.

Rule 1 - Every feature is a folder:
- Every distinct piece of runtime functionality gets its own folder.
- No "too small for a folder" exception exists once a unit owns behavior.
- A parent `main.py` or `index.ts` may exist only as an orchestrator that calls child folders; it must not accumulate child logic.

Rule 2 - Every folder has exactly one public entry point:
- Python folders MUST expose `main.py`.
- TypeScript folders MUST expose `index.ts`.
- If another implementation language is used, declare one equivalent folder contract file and record it in `docs/project/architecture/architecture.md`.
- No file other than the folder entrypoint is public to the outside world; all other files in the folder are private implementation details.

Rule 3 - The parent entrypoint is the only connector:
- Children MUST NOT import siblings.
- Children MUST NOT import the parent.
- Only the parent entrypoint may import child entrypoints and pass data between them.
- Data flow must be explicit in the parent entrypoint; no hidden cross-folder coupling, registries, or side-channel wiring.

Rule 4 - Public contracts take plain data in and return plain data out:
- Public functions in a folder entrypoint MUST accept plain data types only (`str`, `int`, `dict`, `list`, dataclass/TypedDict-equivalent shapes).
- Public contracts MUST return plain data types only.
- Public contracts MUST NOT accept or return live handles/resources such as file handles, DB connections, sockets, COM objects, framework singletons, or process-global mutable state.

Rule 5 - I/O stays at the boundary:
- File reads/writes, network calls, database access, COM automation, subprocess execution, and framework I/O stay at the boundary.
- Pure logic functions MUST NOT perform I/O.
- A folder entrypoint may wire boundary helpers to pure logic, but business rules and transformations stay separated from the I/O implementation.

Rule 6 - No file exceeds 400 LOC:
- A file approaching 400 LOC is doing too much and MUST be decomposed by responsibility.
- Default split target: add private files inside the same folder first.
- Create a new child folder only when the responsibility becomes independently owned behavior.

Rule 7 - `shared/` is a dictionary, not a connector:
- `shared/` is optional.
- `shared/` may contain only data shapes and pure/stateless utility functions.
- `shared/` MUST NOT contain business rules, workflow orchestration, I/O, stateful services, singletons, or decision-making logic.
- Do not create `shared/` preemptively. Extract to `shared/` only when the exact same pure shape/utility is duplicated across 3+ folders.

Rule 8 - Deletion test:
- Before marking the task complete, ask: "Can I delete any single feature folder and the only file that breaks is its parent entrypoint?"
- If deleting one folder causes errors in any sibling folder, there is a coupling violation that MUST be fixed before completion.

Rule 9 - Depth when necessary, not flat by default:
- If a child folder grows multiple sub-responsibilities, apply these same rules recursively inside that child.
- There is no depth limit, but every level MUST keep one folder entrypoint, private internals, parent-only wiring, and a passing deletion test.

Rule 10 - Contract changes require explicit approval:
- Before changing a folder entrypoint contract, state:
  - the current contract
  - the proposed new contract
  - every parent entrypoint that calls it
- Get explicit user approval before changing entrypoint parameters, return types, or names.
- Internal files that are not the folder entrypoint may change freely as long as the public contract remains stable.

Supporting design constraints (mandatory):
- Keep high cohesion + low coupling.
- Apply DRY, KISS, YAGNI, Separation of Concerns, and Law of Demeter inside the folder-contract model.
- Use explicit parameter/constructor injection instead of service locators.
- No runtime discovery, dynamic import, or eval for wiring.
- Shared leaf modules remain pure/stateless and authority-neutral.
- Keep folder entrypoints thin, import-safe, and orchestration-only; private internals hold the detailed logic.

## Governance Templates (Required)

### Change Contract (Required for any change record)
Use in PR description or commit message. Full template: `docs/agents/playbooks/change-contract-template/change-contract-template.md`.

When artifact-based verification is enabled for the repo, record the same evidence in `docs/project/change-records/*.json` and validate it against `docs/agents/schemas/change-record.schema.json`.

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
- The project `README.md` MUST link to `docs/project/index.md` (project docs entrypoint) and to `AGENTS.md` (governance).
- The project `README.md` MUST include a short "Checks" section listing the deterministic verification commands for the repo.

Project docs are the SSOT for intent/runbooks (not for code facts):
- `docs/project/index.md` (entrypoint/router; linked from README)
- `docs/project/goal/goal.md` (objective + acceptance criteria; router at `docs/project/goal/index.md`)
- `docs/project/rules/rules.md` (project do/don't rules; router at `docs/project/rules/index.md`)
- `docs/project/architecture/architecture.md` (SSOT pointers: entrypoints/modules/workflows; router at `docs/project/architecture/index.md`)
- `docs/project/learning/learning.md` (operational learnings and pitfalls; router at `docs/project/learning/index.md`)

Structure SSOT: `docs/agents/playbooks/project-docs-template/project-docs-template.md`

All project docs must:
- Follow the required doc header (except index pages).
- Reference SSOT owners by identifier (code/config/workflow entrypoints) rather than duplicating literals/rules.
- Stay minimal and precise (prefer short bullet lists; avoid long prose).
- Avoid duplicating governance rules: reference `AGENTS.md` instead of copying its requirements.

### Docs Branching Architecture (Hard Gate)
- Every directory under `docs/` MUST contain an `index.md`.
- `index.md` is the required public routing contract for a docs folder.
- `index.md` MUST be routing-only; it MUST NOT be the canonical narrative content doc for a migrated folder.
- Each docs-folder `index.md` MUST catalog its direct children only.
- Narrative leaf folders MUST contain exactly one canonical non-`index.md` markdown file.
- Each child entry in a folder index MUST include:
  - the child path/link
  - its role/purpose
  - a `Required when:` routing statement
- Direct references to actual narrative content MUST point to the canonical leaf doc, not to `index.md`.
- During staged migration, untouched legacy content-bearing `index.md` files may remain only in folders that have not yet been migrated to the router-plus-leaf pattern. Once a docs folder is touched for structure work, migrate it.
- Parent indexes route downward; they MUST NOT restate the child doc's rules, literals, or contracts in full.
- Flat markdown docs under `docs/` should be promoted into branch folders when they start accumulating multiple subtopics or repeated edits.
- Payload/artifact folders under `docs/` (schemas, generated docs, settings payloads, change records, runtime assets) still require an `index.md` so the tree stays navigable and auditable.

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
Each doc (except indexes) must declare:
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

Start here: `docs/agents/index.md`
