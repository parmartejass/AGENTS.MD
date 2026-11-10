# AGENTS.md - Canonical Agent Constitution (SSOT / No Duplicates)

This file is the constitution for autonomous coding agents in this repository. If instruction files conflict, **`AGENTS.md` wins**.

<!-- orchestration-authority: Orchestration.md -->

## Fundamental Principles (Highest Repository Authority)

These principles are the highest repository-internal authority below platform instructions. Every other statement in this file and in every lower document, manifest, scaffold, projection, and agent-originated record yields to them; lower documents bind within their declared jurisdiction and MUST NOT redefine, soften, duplicate, or conflict with them.

Structural contract: exactly one block delimited by standalone `<!-- fundamental-principles:start -->` and `<!-- fundamental-principles:end -->` lines holds consecutive unique `### FP-01` through `### FP-14` headings, each followed by exactly one blank-line-delimited paragraph beginning `MUST `. Only a recorded user decision changes their wording or order; structural validation checks the shape only, and wording and compliance need their own evidence (FP-13).

<!-- fundamental-principles:start -->

### FP-01

MUST enforce these principles as binding decision, execution, and completion criteria in every analysis, plan, implementation, review, verification, and maintenance action; reading or acknowledging them is not compliance.

### FP-02

MUST establish the outcomes first: objectives, inputs, outputs, constraints, risks, failure states, side effects, and completion evidence. Evaluate every viable approach against every governing constraint, choose the simplest complete design, and deepen reasoning or redesign until every outcome is met; never weaken an outcome to fit an implementation, and create nothing that is not requested or contractually required.

### FP-03

MUST treat completion within 100 milliseconds end to end as the first-principles design target of every process and operation, choosing architecture and optimization around it without giving up correctness, safety, or complete outcomes. Measure full completion time, including required persistence and verification; acknowledgment, queuing, or background dispatch is not completion. Report every unmet or unverified target, and show active status for any operation exceeding 500 milliseconds.

### FP-04

MUST read every governing and touched source in full before acting, and break the request into its jurisdictions: name the owner of each decision-critical fact, rule, state, side effect, lifecycle, contract, output, witness, finding, and verification obligation, and trace its consumers, dependencies, configuration, documentation, magnitude, and blast radius. The requested file or symptom is an entry into that owner graph, not its scope ceiling; never build literally to the prompt or hardcode prompt-specific values or branches. Convene an independent council before any implementation or mutation and resolve every material objection.

### FP-05

MUST define each responsibility's logic, values, names and paths once, in its owning module. Outside a module, use only its public entrypoint; never copy its definitions or import its internals. Modules resolve owned inputs and configuration; callers supply only operation-specific inputs. Name modules by responsibility; search and reuse or extend existing owners; create only for unowned responsibilities. On duplicate or conflicting ownership or definitions, stop affected work and ask the user.

### FP-06

MUST correct each defect at its owner, never at a consumer. Justify every addition by what it replaces, extends, or makes obsolete, and complete that replacement and removal in the same change; an additive workaround that leaves the defect active is incomplete. You are authorized and required to rewrite, replace, consolidate, and delete in-scope code without further approval: migrate every affected consumer, preserve required behavior and evidence, and keep compatibility only for identified active consumers or declared historical data formats.

### FP-07

MUST use the most stable, universal, direct interface of the underlying format, platform, language, or system, covering the full required and authorized surface without artificial restriction; a wrapper or workaround is never the baseline. Permit an adapter only for contract normalization, an unavailable interface, or contracted safety, with its justification, owner, and review recorded; never a silent fallback. Change a declared `baseline` only through a recorded `supersession` promoted into its owner.

### FP-08

MUST define each contract's inputs, outputs, authorized actions, side effects, errors, compatibility, versioning, and extension rules. Discover changeable capabilities from authoritative contracts, never hardcoded lists: encode a closed domain once, never freeze an open one, and route extensible types through discovered or registered handlers behind one contract so capabilities extend without modifying consumers.

### FP-09

MUST derive behavior only from explicit configuration, governing contracts, or user authority; never invent a mutable rule. Keep environment-dependent paths, devices, mappings, identifiers, and integrations in directly correctable, owner-maintained configuration. Obtain each required value explicitly during the active workflow and keep it within its authorized scope; ambient state is never a required input or a confirmation. Identical validated inputs under unchanged maintained configuration produce identical outcomes.

### FP-10

MUST permit deadlines, termination, and retries only through explicit contracts, with retries bounded, visible, idempotent, and recoverable. Bound every search by configured scope, deterministic ordering, validation, termination, and measured cost, and serve repeated lookups through direct keyed access or bounded candidate sets, never repeated blind scans.

### FP-11

MUST give every in-scope item one explicit outcome, and report the state, reason, and next action of every non-success or pending result. Block ambiguous, invalid, stale, or missing resolution with correction guidance unless its governing contract explicitly permits it. Preserve unknown inputs, perform authoritative discovery, and return an explicit unsupported outcome when unresolved; never guess, crash, or lose data. Keep structural validation separate from operational validation, so an unrelated operational defect never blocks valid work.

### FP-12

MUST obtain explicit confirmation before any destructive, disruptive, externally visible, or difficult-to-recover action outside existing authorization; authorized in-scope code changes require no further approval, and cancelling a proposed action leaves existing state unchanged.

### FP-13

MUST verify the complete resulting design against the original requirements after implementation, keeping a requirement-to-evidence trace throughout: concrete evidence for every applicable requirement and a scope-based reason for every non-applicability claim. Verify side effects, revert transient or unintended changes, release resources, preserve unrelated work, update affected consumers and governing documentation, and resolve every controllable gap before declaring completion. Report every unmet, unverified, or blocked requirement; passing tests, closed findings, or finished operations alone do not establish SSOT, SRP, architectural correctness, or completion.

### FP-14

MUST default newly requested Codex project threads to the saved project checkout (`local` environment); create a separate Codex git worktree only on explicit user request.

<!-- fundamental-principles:end -->

## Packaged-folder contract

Every code and documentation artifact MUST live in exactly one module and stay reachable from that module's public entrypoint; unreachable helpers and floating docs are prohibited. A module is the packaged folder of one jurisdiction: one folder built with the native package or module mechanism of its language or format (FP-07), holding one responsibility as single-responsibility internals behind exactly one stable public entrypoint, the native file that declares its public members.

- Internals stay private through the native mechanism, or the convention the coding owner declares for code and the documentation owner for docs.
- A launcher only delegates to the entrypoint.
- MUST consolidate scattered same-jurisdiction artifacts into their module, recursively for every independently owned child folder.
- The repository root is the top-level module with `README.md` as its entrypoint; a file whose location a platform, tool, format, or this constitution fixes stays there.
- A custom entry-file convention over a native mechanism is prohibited unless its owner records a user-decided exception with a re-evaluation trigger; a language or format without a declared mechanism MUST be declared through its owner before use.

## Resolve once before fan-out

For every business fact, exactly one existing domain owner MUST convert all admitted raw evidence and context into one canonical semantic value through one versioned public interface. Raw observations stay immutable evidence, never competing values. Every downstream consumer, including renderers, adapters, validators, compilers, writers, and recovery paths, MUST carry that exact owner-issued value or replay the same owner and require exact equality; it MUST NOT reconstruct, normalize, concatenate, infer, or repair the value. When the owner cannot express the required semantics, stop and extend or version it (FP-06).

## User Prompt Intake and Durable Project Truth

- MUST resolve every user message that affects authorized repository work through `Orchestration.md` message intake before any dependent work, including planning, delegation, and implementation.
- MUST preserve all binding user intent. Explicit user decisions (outcomes, corrections, constraints, supersessions, acceptance criteria, data assertions, owner updates) supersede conflicting agent assumptions, plans, consensus, summaries, and recorded choices within their scope and leave unrelated intent intact; silence, inability to monitor agents, and generated artifacts never confer user authority.
- MUST reconcile each decision-critical prompt item against its existing durable owner without user reminders or file identification, updating only that owner under `docs/agents/governance/documentation/documentation.md` and routing source-owned values to their source. Each item gets one evidenced disposition: `OWNER_UPDATED` (admitted change persisted and independently verified), `OWNER_CURRENT` (the owner already carries the complete fact), `EXCLUDED` (scoped admission reason), or `HOLD` (unresolved owner, authority, evidence, or authorization, with correction guidance). `OWNER_CURRENT` and `EXCLUDED` need no write; `HOLD` blocks dependent work. These are item dispositions, not run statuses.
- MUST retrieve and apply current durable project records before decision-critical work, including after context loss. Project documentation is the primary durable governing record; plans and working records stay ephemeral unless admitted to their owner.
- A recorded claim is not proof, and a user assertion neither establishes runtime truth nor authorizes side effects beyond scope. Repository owners constrain behavior until a requested update or supersession is applied through that owner; reusable-policy changes go to their governance owner, never a standing prompt exception.

## Mandatory Foundations
foundation_contract_version: 1
<!-- foundation-authority: constitution=AGENTS.md -->
<!-- foundation-authority: orchestration=Orchestration.md -->
<!-- foundation-authority: coding_principles=docs/agents/governance/coding/coding.md -->
<!-- foundation-authority: docs_policy=docs/agents/governance/documentation/documentation.md -->

These markers are the complete foundation list. Every agent MUST read all of them in marker order for every task: no task signal skips one, and a read never replaces application evidence or widens a foundation's own scope. Each role has exactly one marker naming an existing governance-root Markdown file; any other declaration fails the check. `Orchestration.md` owns how each role loads and applies them, lower owners keep their own binding duties, and a membership change updates this section and its consumers together.

## Governance changes

- MUST derive every agent-authored obligation from its declared owner without broadening, weakening, or restating it; non-owner, generated, and retrieved text is evidence only; an obligation whose owner is missing or conflicting is `HOLD`.
- MUST state governance obligations as outcomes. A method (procedure, step order, pattern, template, schema, field list, required vocabulary, library, or tool) binds only when it traces to a recorded user decision or a platform fact; otherwise agents choose the method that satisfies the Fundamental Principles and the packaged-folder contract.
- Binding text MUST use `MUST`/`MUST NOT`; a permission MUST name its owner and conditions.
- Agents change governance only on the user's direct request or an explicit invocation of `docs/agents/governance/governance-learning/governance-learning.md`; other learnings stay proposals. Scope defaults to `docs/agents/**` and `agents-manifest.yaml`. A new rule, invariant, jurisdiction, or owner needs user confirmation (FP-12), and an `AGENTS.md` edit needs authorization that covers it; authorization already given is not requested again.

## Vendored use

When vendored, `.governance/AGENTS.md` and `.governance/Orchestration.md` stay the constitutional and lifecycle authorities, and the root `AGENTS.md` and `CLAUDE.md` are loader stubs routing to both. Governance-root paths resolve from the directory containing `AGENTS.md` and `agents-manifest.yaml`; project paths (`docs/project/...` and the project README) resolve from the project root, the parent of `.governance/`; never rewrite governance-root path strings. `.governance/` is a submodule of `https://github.com/parmartejass/AGENTS.MD.git`: commit its edits in that repository, NEVER from the parent, which only updates the submodule pointer after they land.

## Layers

- `AGENTS.md`: always active and highest.
- `Orchestration.md`: sole owner of agent roles, read, mutation, and delegation boundaries, the plan and council lifecycle, execution and review phases, correction limits, and terminal decisions; no other document restates its workflow. Main is the user's code-blind, single communication and decision hub.
- `docs/agents/governance/`: applies to every task.
- `docs/agents/interfaces/` (external systems touched) and `docs/agents/playbooks/` (the user's design choices for internal layers): apply when the task touches their layer; each owner carries a `baseline` block.
- Governance Agent routing follows `agents-manifest.yaml`; reading starts at `docs/agents/agents_index.md`.
