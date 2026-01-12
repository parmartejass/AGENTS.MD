# AGENTS.md — Canonical Agent Constitution (SSOT / No Duplicates)

This file is the single source of truth (SSOT) for **how any autonomous coding agent must operate in this repository**.

Hard gate:
- Do not write or modify code or documentation until this file has been read.
- If repository files are not accessible, request that the user paste `AGENTS.md`.
- If any other instruction file conflicts with this one, **`AGENTS.md` wins**.

## Objective

Deliver changes that are:
- **Correct**: verified against the repo and tools; no guessed APIs/paths.
- **Deterministic**: same inputs → same outputs (no hidden side effects).
- **Maintainable**: each concept defined exactly once (SSOT / no duplicates).
- **Auditable**: logs + clear run outcomes; failures are explicit.
- **Safe**: no resource leaks; Excel COM + GUI threading rules are enforced.
- **Searchable**: critical concepts are discoverable via grep + semantic search.

## Prime Directive: Verify, Then Trust

Agents are probabilistic generators. The repo and tools are deterministic.
When a fact can be verified with tools, **verify it** instead of guessing.

Never invent:
- imports/dependencies
- file paths
- functions/classes/symbols
- CLI flags or config keys

If verification is not possible, treat it as **Unknown** and ask.

## Mandatory Execution Loop (Follow For Every Task)

1) **Restate goal + acceptance criteria** (1-5 bullets).
2) **Discover** relevant files and existing SSOT owners (constants/config/rules/workflows/etc).
   - **MUST** consult `agents-manifest.yaml` and execute the Context Injection Procedure (see below).
   - Use `docs/agents/10-repo-discovery.md` for discovery search terms and SSOT adoption rules.
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
3) READ all files from `default_inject`.
4) If one or more profiles match, READ the union of all matching profiles' `inject` lists (unless `injection_mode` specifies otherwise). If no profiles match, READ `fallback_inject` (if defined).
5) Follow context retrieval best practices in `docs/agents/05-context-retrieval.md`.

If any referenced file is not accessible, STOP and ask the user to paste it.

## Non‑Negotiables (Hard Gates)

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

Unreferenced helpers and “floating docs” are prohibited.

### 4) Logging + Explicit Failure
- No `print()`.
- Use module-level logging (`logger = logging.getLogger(__name__)`) where applicable.
- Catch specific exceptions; log context; raise meaningful domain errors.
- Never “silently skip”: if something is skipped, record **SKIPPED + reason** (log and/or run report).

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

### Project-specific docs (recommended in downstream repos)
When this governance pack is copied into a project repo, it is encouraged to add a **minimal** project docs set that becomes the project's SSOT for intent/runbooks (not for code facts):
- `docs/index.md` (entrypoint; linked from README)
- `docs/goal.md` (objective + acceptance criteria)
- `docs/rules.md` (project do/don't rules)
- `docs/architecture.md` (SSOT pointers: entrypoints/modules/workflows)
- `docs/learning.md` (optional; operational learnings and pitfalls)

All such docs must follow the required doc header and must reference SSOT owners by identifier (code/config), rather than duplicating literals/rules.

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

Comments drift quickly; keep them “why-only”:
- explain invariants, rationale, and safety constraints
- do not restate logic or duplicate constants/defaults
- reference SSOT symbols/modules when needed

## Supporting Docs

Start here: `docs/agents/index.md`
