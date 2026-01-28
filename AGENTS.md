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
3. **ALWAYS** checkout and pull main before making changes: `git checkout main && git pull origin main`
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
- **Root-cause uplift** (authority-first): for any defect or error, trace from symptom to the earliest authority/contract/boundary that should have prevented it; prefer fixing there by adding or strengthening invariants/validation so the class of errors becomes structurally impossible; one authority fix prevents N errors. If a symptom-level patch is unavoidable, record why upstream prevention is infeasible.
- **Proof obligations**: preconditions/postconditions + failure modes to cover.
- **Verification**: exact commands or deterministic manual checks (include at least one failure-path check when feasible).
- **Resource bounds**: timeouts, cancellation, and guaranteed cleanup in `finally` for external resources.
- **Performance constraints**: expected data sizes and speed targets; choose algorithm/I/O strategy accordingly, without weakening correctness or safety.

Supporting references:
- First principles patterns: `docs/agents/00-principles.md`
- Concept -> owner map: `docs/agents/20-sources-of-truth-map.md`

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
- Record the authority graph in `docs/project/architecture.md` or the workflow registry; no orphan docs.
- All reads/writes must go through the authority; no shadow logic or one-off duplication.

### Workflow State Machine + Two-Phase Commit (When writes occur)
- Required phases: INIT, VALIDATED, COMMIT_READY, COMMITTING, CLEANING, DONE.
- Failure phases: FAILED_VALIDATION, FAILED_COMMIT, FAILED_CLEANUP.
- Validation must be side-effect free; no writes before VALIDATED.
- If any failure after writes begin: record FAILED_COMMIT, log what was written, attempt bounded cleanup in `finally`.

### Bias-Resistant Debugging (Hard Gate)
Biases to guard against:
- premature closure, confirmation bias, anchoring, novelty/recency bias

Mandatory anti-bias artifacts for every fix:
- minimal reproducible example (MRE)
- regression fixture stored in repo
- disconfirming tests (edge/adversarial cases)
- invariant witness that fails pre-fix and passes post-fix
- root-cause uplift record: symptom location, upstream authority fix point, prevention change made, class of errors prevented, or explicit justification if patching locally
- SSOT consolidation evidence when divergence was a root cause

Confidence rule:
- confidence is evidence-weighted; "it worked once" is not evidence

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
   - Use `docs/agents/10-repo-discovery.md` for discovery search terms and SSOT adoption rules.
   - MUST ensure project docs exist and are read (start with `README.md` and `docs/project/index.md`; create missing docs per "Documentation SSOT Policy").
3) **Decompose** into atomic, independently verifiable subtasks.
4) **Ambiguity gate**: if multiple interpretations would change code materially, STOP and ask 1-3 clarifying questions.
5) **Implement minimally**: smallest diff that satisfies acceptance criteria; no bundled refactors.
6) **Verify** with deterministic tools (tests/lint/run) or provide deterministic manual checks
   when tools are unavailable.
7) **Report**: what changed, where SSOT lives, and evidence of verification.

## Context Injection Procedure (Hard Gate)

Before reasoning or implementing, agents MUST:

1) Read `agents-manifest.yaml`.
2) Determine matching profiles by evaluating each profile's `detect` signals against the task:
   - `detect.keywords`: case-insensitive substring match on the user prompt and any referenced file contents.
   - `detect.code_patterns`: regex/substrings matched against code in scope.
   - `detect.file_globs`: match against files referenced and/or being edited.
   - `detect.signals`: explicit signals provided by the harness/user.
   - If semantic search is available and a profile matches, start with `agents-manifest.yaml:semantic_queries.<profile>` when present (see `docs/agents/05-context-retrieval.md`).
3) READ all files from `default_inject`.
4) If one or more profiles match, READ the union of all matching profiles' `inject` lists (unless `agents-manifest.yaml:injection_mode` specifies otherwise). If no profiles match, READ `fallback_inject` (if defined).
5) Follow context retrieval best practices in `docs/agents/05-context-retrieval.md`.

If any referenced file is not accessible, STOP and ask the user to paste it.

## Non-Negotiables (Hard Gates)

### 1) Single Source of Truth (SSOT)
For every concept, there must be exactly one authoritative definition:
- constants (sheet names, headers, statuses, folder names, prefixes/patterns)
- config keys + defaults + schema
- business rules / conditions / validation logic
- workflow orchestration steps
- Excel lifecycle management (open/close/quit/verify/kill)
- GUI queue/drain + cancellation pattern

If an SSOT already exists in the repo for a responsibility, **extend it**.
Do not create parallel utilities/modules/docs for the same ownership.

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
- Follow: `docs/agents/15-stuck-in-loop-generate-fresh-restart-prompt.md`

### 10) Performance & Speed (When Relevant)
- If speed/performance is an acceptance criterion or implied by scale, state a performance model and pick low-risk optimizations first (algorithmic wins, reduce I/O, avoid repeated scans).
- Never trade away correctness, determinism, data integrity, edge-case safety, logging, or guaranteed cleanup for speed; keep concurrency bounded and cancellation-aware.
- Verify claimed speedups with deterministic evidence (benchmark/timing) or complexity reasoning; avoid premature micro-optimizations.

## Governance Templates (Required)

### Change Contract (Required for any change record)
Use in PR description or commit message.

```md
# Change Contract (Required)

## A) Problem Statement (Observed vs Expected)
- Observed:
- Expected:
- Scope: (rows/files/modules/users impacted)

## B) Invariants (Semantic Truth: S)
List invariants affected by this change. Use categories.

### Data invariants
- INV-D1:
- INV-D2:

### Ordering invariants
- INV-O1:

### Atomicity invariants (2PC / all-or-nothing)
- INV-A1:

### Idempotency invariants
- INV-I1:

### Lifecycle invariants (Excel/COM/resources)
- INV-L1:

### Observability invariants (outcome/log completeness)
- INV-OBS1:

## C) Witnesses (Runtime Evidence: R / Recorded Truth: D)
For each invariant above, define a measurable witness.

| Invariant ID | Witness signal (what is measured) | Where recorded (log field/report col) | Pass criteria |
|---|---|---|---|
| INV-L1 | Excel PID baseline before/after | log.excel_pid_before/after | after == before |
| INV-A1 | No writes before validation complete | log.phase sequence | no write events before VALIDATED |

## D) Authority Impact + Fix Placement (SSOT: D)
Identify which authorities are touched and confirm no new competing authority exists.

- Config authority impacted? (Y/N) If Y: where is canonical key defined?
- Parser authority impacted? (Y/N)
- Writer authority impacted? (Y/N)
- Excel lifecycle authority impacted? (Y/N)
- Logger/schema authority impacted? (Y/N)
- Report ledger authority impacted? (Y/N)

No-duplication proof (list any removed duplicated logic/files):
- Removed:
- Replaced by:

### Authority-first fix analysis (if debugging)
- Symptom location (where error manifested):
- Authority fix point (where fix was applied):
- Class of errors prevented by fixing at authority:
- If patching at symptom, justify:

## E) Minimal Repro + Regression Fixture
- Minimal repro description:
- Fixture location (path):
- Before fix (expected failure signal):
- After fix (expected pass signal):

## F) Disconfirming Tests (Anti-Premature-Closure)
List tests designed to break your hypothesis.

- Test 1 (edge/adversarial):
- Test 2 (randomized/property):
- Test 3 (real-file replay):

## G) Rollout and Safety
- Feature flag / mode switch? (Y/N) If Y: name:
- Rollback plan:
- Data safety: (atomic writes? backups? temp + rename?)

## H) Verification Checklist (Expected Outcomes)
- [ ] All invariants have witnesses
- [ ] 2PC enforced (no writes before VALIDATED)
- [ ] Every row/file ends with terminal outcome + reason
- [ ] Cleanup baseline restored (Excel/process/temp files)
- [ ] Fixture added + tests pass
```

### Standard Log Schema (Required when logs are emitted)
- Logging policy in "Logging + Explicit Failure" still applies (no print, module logger, explicit failures).
- The log schema is SSOT: define one owner and extend it; do not fork schemas.

Run-level record (run_start, run_end):
- ts (ISO8601)
- event (run_start | run_end)
- run_id
- app, version, mode
- inputs, outputs (objects)
- result (SUCCESS | PARTIAL_SUCCESS | FAILURE)
- summary (object): by_outcome {executed, skipped, failed}; failed_by_phase {validation, commit, cleanup}
- timings_ms (object)
- errors (array of {type, message, where, fatal})
- resources (optional, when applicable): pids_before/after, handles_closed, quit_called, kill_fallback_used

Phase transition record:
- ts, event (phase_transition), run_id, phase, phase_seq, notes (optional)

Item-level record (row_event or file_event) - emitted once per item at terminal state:
- ts, event, run_id, phase
- item_id (row id or file path)
- outcome (EXECUTED | SKIPPED | FAILED)
- final_phase (VALIDATED | COMMITTED | FAILED_VALIDATION | FAILED_COMMIT | FAILED_CLEANUP)
- reason_code, reason_detail
- evidence (object)
- write_effects (object)
- duration_ms

Reason codes:
- Maintain a single enum owner (module or config). Extend there only.
- Example codes: MISSING_REQUIRED_HEADER, DUPLICATE_HEADER, MISSING_INPUT_FILE, INVALID_IDENTIFIER_FORMAT,
  DUPLICATE_KEY_IN_INPUT, COM_WRITE_FAILED, SAVE_FAILED, EXCEL_QUIT_FAILED, PID_VALIDATION_FAILED.

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
- `docs/project/index.md` (entrypoint; linked from README)
- `docs/project/goal.md` (objective + acceptance criteria)
- `docs/project/rules.md` (project do/don't rules)
- `docs/project/architecture.md` (SSOT pointers: entrypoints/modules/workflows)
- `docs/project/learning.md` (operational learnings and pitfalls)

Structure SSOT: `docs/agents/playbooks/project-docs-template.md`

All project docs must:
- Follow the required doc header (except index pages).
- Reference SSOT owners by identifier (code/config/workflow entrypoints) rather than duplicating literals/rules.
- Stay minimal and precise (prefer short bullet lists; avoid long prose).
- Avoid duplicating governance rules: reference `AGENTS.md` instead of copying its requirements.

### Docs MAY contain
- intent (“why”), invariants, and safety constraints
- contracts/interfaces referencing SSOT symbols/modules/workflow entrypoints
- playbooks/checklists/runbooks referencing entrypoints and config keys by identifier
- decision records (ADR-style)

### Docs MUST NOT contain (unless clearly marked as example)
- duplicated tables of constants/defaults
- prose re-implementations of business rules without pointing to the named rule function
- manually-maintained code blocks that mirror production code

### Required doc header (for files under `docs/`)
Each doc (except indexes) must declare:
- `doc_type`
- `ssot_owner`
- `update_trigger`

See `docs/agents/25-docs-ssot-policy.md`.

## Code Comment Policy (Hard Gate)

Comments drift quickly; keep them "why-only":
- explain invariants, rationale, and safety constraints
- do not restate logic or duplicate constants/defaults
- reference SSOT symbols/modules when needed

## Supporting Docs

Start here: `docs/agents/index.md`
