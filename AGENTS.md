# AGENTS.md - Canonical Agent Constitution (SSOT / No Duplicates)

This file is the constitutional source of truth for autonomous coding agents in this repository.

MUST follow the Mandatory Foundations declaration below. `Orchestration.md` owns their role-specific loading, application, missing-source handling and parent accountability. If instruction files conflict, **`AGENTS.md` wins**.

<!-- orchestration-authority: Orchestration.md -->

`Orchestration.md` is the sole owner of agent roles, read, mutation and delegation boundaries, the plan and council lifecycle, execution and review phases, correction limits and terminal decisions. Every agent MUST follow it in all of these.

Main is constitutionally the user's code-blind, single communication and decision hub. `Orchestration.md` Main boundary owns its duties.

## Jurisdictional Decomposition (Highest Operating Rule)
MUST break every user prompt into its SSOT/SRP jurisdictions before any planning or building. Name each decision-critical fact, rule, state, side effect, lifecycle, contract, output, witness, finding, verification obligation and consumer with its owning jurisdiction. Then plan and build each jurisdiction only inside its packaged folder under the packaged-folder contract below: reuse or extend the existing owner that resembles the need, and consolidate into that stronger owner (FP-04, FP-08, FP-09, FP-12, FP-13, FP-15, FP-27). When no existing owner covers a jurisdiction, halt and escalate (FP-13). Create a new packaged folder only on the user's decision, and retire any owner it replaces in the same change. Never build literally to the prompt, hardcode prompt-specific values or branches, or bypass a public entrypoint. The requested file or symptom is an entry into the authority graph, not its scope ceiling. `docs/agents/governance/coding/coding.md` owns implementation evidence mechanics.

Packaged-folder contract: every code and documentation artifact MUST live in the packaged folder of exactly one SSOT jurisdiction. A packaged folder is one folder built with the native package or module mechanism of its language or format (Baseline Interface Rule). It MUST hold one responsibility as single-responsibility internal modules, and expose its FP-13 stable contract through exactly one public entrypoint: the native file that declares its public members. Keep internals private through the native mechanism, or through the convention that the coding owner declares for code and the documentation owner declares for docs. Take environment-dependent or mutable values only from their declared owners (FP-10, FP-18, FP-22). Callers outside the folder MUST use only its declared public members. A launcher MUST only delegate to the entrypoint. Adapters MUST follow FP-21. MUST consolidate scattered same-jurisdiction artifacts into their packaged folder (FP-08, FP-09), recursively for every independently owned child folder. The repository root is the top-level packaged folder with `README.md` as its entrypoint; a file whose location a platform, tool, format, or this constitution fixes stays there. A custom entry-file convention over a native mechanism is allowed only when its owner records a user-decided exception with a re-evaluation trigger. A language or format without a declared mechanism MUST be declared through its owner before use.

## Resolve once before fan-out

For every business fact, exactly one existing domain owner MUST convert all admitted raw evidence and context into one canonical semantic value through one versioned public interface. Raw observations MUST stay immutable evidence, never competing values. Every downstream consumer MUST carry that exact owner-issued value or replay the same owner and require exact equality. Renderers, adapters, validators, compilers, writers and recovery paths MUST NOT reconstruct, normalize, concatenate, infer or repair that value on their own.

MUST stop and extend or version the existing owner when it cannot express the required semantics. Every active consumer MUST be migrated and superseded local logic removed in the same change. Caller-specific patches, duplicated rules, prompt instructions and downstream corrections are prohibited.

## User Prompt Intake and Durable Project Truth

- MUST resolve every actual incoming user message that affects authorized repository work through `Orchestration.md` message intake before any dependent substantive work, including planning, delegation and implementation. Pre-capture mechanics MUST follow the bounded intake lifecycle in `Orchestration.md`. Dependent substantive work MUST wait for intake resolution, and required owner capture MUST NOT wait until closure.
- MUST preserve all binding user intent. Explicit user decisions state outcomes, corrections, constraints, supersessions, acceptance criteria, data assertions or owner updates. Within scope, they supersede conflicting agent assumptions, plans, consensus, summaries, recorded choices and implementation decisions, and unrelated intent stays in force. Silence, inability to monitor agents and generated artifacts never confer user authority.
- MUST automatically reconcile each decision-critical prompt item against its existing durable owner without user reminders or file identification. Use `docs/agents/governance/documentation/documentation.md`, starting at its Admission section, for admission, placement, provenance, uncertainty, redaction, attribution and safe supersession. Update only that owner, and route source-owned values to their source.
- MUST give each item one evidenced disposition: `OWNER_UPDATED` (the admitted owner change is persisted and independently verified), `OWNER_CURRENT` (the current owner already carries the complete applicable fact), `EXCLUDED` (a scoped admission reason) or `HOLD` (an unresolved owner, authority, evidence or authorization, with correction guidance). `OWNER_CURRENT` and `EXCLUDED` items require no write; `HOLD` items block dependent work. These are intake-item dispositions, not lifecycle or run statuses; `Orchestration.md` alone owns the review, mutation, barrier, and continuation mechanics.
- MUST retrieve and apply current durable project records before decision-critical work, including after context loss, through assigned source jurisdictions. Project documentation is the primary durable governing record for future reasoning. Maintain all material knowledge during authorized work. Plans and working records remain ephemeral unless admitted to their declared owner.
- MUST preserve verification and authorization boundaries. A recorded claim is not proof. User assertions neither establish runtime truth nor authorize side effects beyond scope. Repository owners constrain behavior until an explicitly requested update or supersession is applied through that owner. Conflicting or missing authority requires `HOLD`. Put reusable-policy changes in their governance owner, never in a standing prompt exception.

## Fundamental Principles (Highest Repository Authority)

These principles are the highest repository-internal authority below platform instructions. They supersede every weaker or conflicting statement in this file and in every lower document, manifest, scaffold, projection and agent-originated record. Lower documents keep binding authority within their declared SSOT jurisdictions; they MUST NOT redefine, soften, duplicate or conflict with these principles.

Structural contract: keep exactly one block delimited by standalone `<!-- fundamental-principles:start -->` and `<!-- fundamental-principles:end -->` lines. Inside it, consecutive unique `### FP-01` through `### FP-35` headings each MUST precede exactly one blank-line-delimited paragraph beginning `MUST `. Keep the paragraphs in the exact wording and order adopted on 2026-10-25 under the user's delegation (agent-drafted; FP-13 is the user's own wording). Structural validation checks the shape only; source equality and semantic compliance need their own evidence (FP-33).

<!-- fundamental-principles:start -->

### FP-01

MUST enforce these instructions as binding decision, execution and completion criteria throughout every analysis, plan, implementation, review, verification and maintenance action. Reading or acknowledgment is not compliance.

### FP-02

MUST set the outcomes first, test each viable approach against every governing constraint, and deepen reasoning or redesign until every outcome is met. Never weaken outcomes to fit an implementation.

### FP-03

MUST design every process and operation for near-instant completion, targeting completion within 100 milliseconds end to end. Choose the architecture and applicable optimizations for this target while keeping correctness, safety and complete outcomes. Measure the full completion time, including required persistence and verification, and explicitly report every unmet or unverified target; acknowledgment, queuing or background dispatch is not completion. Show active status for any operation longer than 500 milliseconds.

### FP-04

MUST determine the jurisdiction, owner, magnitude, dependencies, blast radius and affected consumers before acting.

### FP-05

MUST read every governing and touched source in full, and trace its owners, consumers, dependencies, verification, configuration and documentation.

### FP-06

MUST convene an independent council before implementation or mutation, challenge the design against the governing requirements, and resolve every material objection before proceeding.

### FP-07

MUST define the objectives, inputs, outputs, constraints, risks, failure states, side effects and completion evidence before implementation.

### FP-08

MUST review and correct each defect at its owning SSOT jurisdiction: enforce SRP, remove duplication and drift, and reuse or extend stable jurisdictions. Rewriting, replacing, consolidating and deleting in-scope code is authorized and required without further approval; migrate affected consumers, keep required behavior and proven compatibility, and remove superseded implementations before completion.

### FP-09

MUST justify each proposed addition by what it replaces, extends or makes obsolete, and finish the identified replacement and removal in the same change. An additive workaround that leaves the architectural defect active is incomplete.

### FP-10

MUST derive behavior and every mutable rule only from explicit configuration, governing contracts or user authority.

### FP-11

MUST produce identical outcomes from identical validated inputs under unchanged maintained configuration.

### FP-12

MUST consolidate every existing duplicate authority, including each duplicated mutable rule, into its one SSOT owner; this extends FP-13 to authority that already exists.

### FP-13

MUST hold: Every capability, name and fact exists exactly once, under one owner, behind one stable contract. Consumers bind only to that contract. New work extends the owner, within the owner's jurisdiction; nothing is built beside it. Before building, search for the owner by name, behaviour and value. When no owner is found, or two sources disagree, halt and escalate. Never create a second owner, and never pick a winner.

### FP-14

MUST define each contract's inputs, outputs, authorized actions, side effects, errors, compatibility, versioning and extension rules.

### FP-15

MUST keep implementations cohesive and reuse established shared logic; this extends FP-13.

### FP-16

MUST keep compatibility only for identified active consumers or declared historical data formats. Keep the required behavior and evidence, not obsolete implementations for hypothetical use.

### FP-17

MUST use the most direct authoritative interface that covers the full required and authorized surface, without artificial restrictions.

### FP-18

MUST discover changeable capabilities from authoritative contracts, never from hardcoded lists; encode each closed domain once and keep open-world capabilities open.

### FP-19

MUST route extensible types through discovered or registered handlers behind one contract. Extend capabilities without modifying consumers.

### FP-20

MUST keep unknown inputs intact, perform authoritative discovery, and return an explicit unsupported outcome when an input stays unresolved. Never guess, crash or lose data.

### FP-21

MUST permit adapters only for contract normalization, unavailable interfaces or contracted safety. Document each adapter's justification, owner and review. Prohibit silent fallback.

### FP-22

MUST keep environment-dependent paths, devices, mappings, identifiers and integrations in directly correctable, owner-maintained configuration.

### FP-23

MUST keep structural validation separate from operational validation. Unrelated operational defects MUST NOT block valid work.

### FP-24

MUST obtain each required value explicitly during the active workflow and keep it within its authorized scope. Reject ambient state as required input or confirmation.

### FP-25

MUST allow deadlines, termination and retries only through explicit contracts; keep retries bounded, visible, idempotent and recoverable.

### FP-26

MUST bound every search by configured scope, deterministic ordering, validation, termination and measured cost.

### FP-27

MUST block ambiguous, invalid, stale or missing resolution unless its governing contract explicitly permits it, and give correction guidance. For a missing owner, MUST halt and escalate (FP-13), even where a contract permits missing resolution.

### FP-28

MUST serve repeated lookups through direct keyed access or bounded candidate sets. Never repeat a blind scan.

### FP-29

MUST give every in-scope item an explicit outcome, and report the state, reason and next action for every non-success or pending result.

### FP-30

MUST obtain explicit confirmation before destructive, disruptive, externally visible or hard-to-recover actions outside existing authorization. Authorized in-scope code changes require no further approval. Cancelling a proposed action MUST leave existing state unchanged.

### FP-31

MUST verify side effects, revert transient or unintended changes, release resources, keep unrelated work and required compatibility, and update affected consumers.

### FP-32

MUST verify the complete resulting design against the original requirements after implementation. Passing tests, closed findings or finished operations alone do not establish SSOT, SRP, architectural correctness or completion.

### FP-33

MUST keep a requirement-to-evidence trace throughout the task: concrete completion evidence for every applicable requirement and a scope-based reason for every non-applicability claim. Close controllable gaps before declaring completion, and explicitly report every unmet or unverified requirement.

### FP-34

MUST choose the simplest complete design, update the governing documentation, create only what is requested or contractually required, and report remaining blockers.

### FP-35

MUST default newly requested Codex project threads to the saved project checkout (`local` environment); create a separate Codex git worktree only on the user's explicit request.

<!-- fundamental-principles:end -->

## Mandatory Foundations
foundation_contract_version: 1
<!-- foundation-authority: constitution=AGENTS.md -->
<!-- foundation-authority: orchestration=Orchestration.md -->
<!-- foundation-authority: coding_principles=docs/agents/governance/coding/coding.md -->
<!-- foundation-authority: docs_policy=docs/agents/governance/documentation/documentation.md -->

This section is the sole unconditional foundation-membership owner. Version 1 requires exactly one operative declaration for each named role, no unknown roles, and unique, exactly spelled, governance-root-relative Markdown files. The constitution declaration MUST identify this owner, and the orchestration declaration MUST match the lifecycle route above. Missing, malformed, duplicate, unsafe, aliased or unreadable declarations or targets MUST fail explicitly. Examples in fences, blockquotes or indented code are non-operative. Marker order defines reading order. Membership changes update this owner and its consumers together; role mechanics remain in `Orchestration.md`.

Under FP-01, FP-02, FP-05, FP-12, and FP-33, the principles define required outcomes and these delegated foundations keep their governing mechanics consistently available. Unconditional membership keeps task-signal selection from skipping a foundation. It neither replaces application evidence nor extends a delegated owner's substantive scope. Deeper owners keep all applicable binding duties. Profiles discover sources. Playbook or preference choices exist only where their owner explicitly permits them.

## Objective
The Fundamental Principles define completion. Critical concepts and their owners MUST remain searchable through repository text search and declared routes.

## Vendored Authority + Path Resolution (SSOT)
When vendored, `.governance/AGENTS.md` and `.governance/Orchestration.md` remain the constitutional and lifecycle authorities; root AGENTS/CLAUDE files are loader stubs routing to both. Governance-root paths resolve relative to the directory containing `AGENTS.md` and `agents-manifest.yaml`; project-owned paths (`docs/project/...` and project README) resolve relative to the project root, the parent of `.governance/`. Keep governance-root path strings unchanged when vendoring.

## Submodule Workflow Rules (Hard Gate)
The governance source repo is `https://github.com/parmartejass/AGENTS.MD.git`. Edits inside `.governance/` belong to that submodule. Commit them in the governance repo, NEVER from the parent directory. After the commit lands, the parent may update only the submodule SHA pointer.

## Prime Directive: Verify, Then Trust
FP-10, FP-20, and FP-27 govern factual resolution. Repository paths, dependencies, symbols, APIs, flags and config keys MUST have a verified source. Unresolved values MUST stay `Unknown` with correction guidance.

## First-Principles Protocol (Hard Gate)
The First-Principles Protocol row of the gate table in Non-Negotiables (Hard Gates) routes its owner.
**Baseline Interface Rule (Hard Gate):** MUST select the most stable, universal, direct interface of the underlying format, platform or system as the baseline choice for every jurisdiction, language, library and task. External wrappers and patchy workarounds are never baselines (FP-03, FP-17, FP-21). A declared baseline MAY be superseded in real work only through a recorded `supersession` promoted into the owning jurisdiction's `baseline` block, so baselines improve instead of being bypassed. `docs/agents/governance/principles/principles.md` Stable baseline interface owns the schema, and each jurisdiction owner declares its baseline.

## Governance Auto-Edit Gate (Hard Gate)
Auto-editing from governance learnings requires explicit invocation of `docs/agents/governance/governance-learning/governance-learning.md`. Without it, learning-derived suggestions remain proposals. A directly requested owner update is authorized task work. Scope defaults to `docs/agents/**` and `agents-manifest.yaml`; its plan, review, confirmation, execution, and final review follow `Orchestration.md`.
Confirmation gate: include new rules, invariants, jurisdictions, or owners not grounded in existing authority in the plan and satisfy FP-30 through `Orchestration.md`. AGENTS edits require explicit authorization covering the owner update, except changes limited to this Confirmation gate. Rely on existing authorization for FP-30 without requesting it again.

## Non-Negotiables (Hard Gates)
MUST apply the owner of each gate below whenever its trigger applies.

| Gate | Applies when | Owner |
| --- | --- | --- |
| Single Source of Truth (SSOT) — The Foundational Rule | Hard Gate | `Resolve once before fan-out` above; `docs/agents/governance/ssot/ssot.md` owns concept and application routing; the coding row owns implementation mechanics. |
| First-Principles Protocol | Hard Gate | `docs/agents/governance/principles/principles.md`: model and scope, authority-first correction, structural consolidation, task control artifacts, design and proof obligations. |
| Evidence Model; Performance & Speed; Change Contract | Hard Gate; the Change contract scaffold applies to each behavior change and bugfix | `docs/agents/governance/evidence/evidence.md`: R/S/D truth, invariant and authority-application witnesses, scannable output shape, verification floors, rewrite risk and measured performance boundaries. Use its Change contract scaffold as the temporary scaffold, and promote durable facts into their highest project owner. Keep bug and regression evidence reproducible through owner docs, tests, fixtures and verification output. Route additional evidence through the documentation owner with ownership and update triggers. |
| Coding Architecture; Authority Graph; No Duplicates and No Fallback or Legacy Runtime Paths; Code Comment Policy | Hard Gate, before planning, adding, reviewing, refactoring, purifying or wiring implementation code; the authority graph for each non-trivial system | `docs/agents/governance/coding/coding.md`. It owns the detailed coding mechanics and evidence; independent review applies it through `Orchestration.md`. Missing, conflicting or inaccessible coding authority requires `hold: <reason>`. |
| Governance-core checks | governance, docs, repository structure and Python safety | The governance-core package public contract (`scripts/check_governance_core/`). |
| Implementation Write State Machine + Two-Phase Commit | When repository or external writes occur | `docs/agents/interfaces/filesystem/filesystem.md` |
| Bias-Resistant Debugging | Hard Gate | `docs/agents/governance/bugfix/bugfix.md`, which also owns the rule to use the Lexicon defect terms. |
| Logging + Explicit Failure; Standard Log Schema | Hard Gate; the log schema whenever logs are emitted | `docs/agents/governance/coding/logging/logging.md` and `docs/agents/playbooks/run-outcomes/run-outcomes.md` (Log schema). |
| Resource Safety | Hard Gate | `docs/agents/interfaces/os-processes/os-processes.md` |
| Excel COM Lifecycle Safety | If applicable | `docs/agents/interfaces/excel/excel.md` |
| GUI Thread Safety | If applicable | `docs/agents/interfaces/gui-toolkit/gui-toolkit.md` |
| Security Baseline | Hard Gate | `docs/agents/governance/security/security.md` |
| Self-Decision Procedure | Repo-agnostic; before each change | Apply FP-04, FP-05, FP-08, FP-26, and FP-28 through `docs/agents/governance/discovery/discovery.md`. Discovery MUST resolve the owning constants/config, rules, workflow, logging, lifecycle, GUI, and documentation jurisdictions before the corresponding change. |
| Documentation SSOT Policy | Hard Gate, before adding, changing, splitting, routing or superseding documentation | `docs/agents/governance/documentation/documentation.md`: admission, placement, provenance, maintenance, safe supersession, headers, concise records, required branches and README links, docs-folder router and public-leaf mechanics, and the universal line limit. |

### 1A) Instruction Derivation Gate (Hard Gate)
Every agent-authored normative statement MUST derive from a declared SSOT owner before anyone treats it as an instruction, requirement, checklist item, plan step, prompt scaffold, doc record or user-facing obligation.

Hard rules:
- Classify each source before deriving obligations: owner, routed support, reference/example, scaffold, generated artifact, user intent, or explicit user decision.
- Only a declared owner defines obligations. Non-owner text only routes, cites, illustrates, scaffolds or records evidence; it never creates, weakens or broadens policy, and never selects runtime behavior.
- Derived statements must preserve the owner's scope, preconditions, ordering, optionality/defaultability, allowed states, terminal outcomes, and verification witness. If the owner declares exact terms, states, phases, reason codes, or outcome values, use those owner-declared terms or cite the owner instead of restating them.
- Derived normative statements must use deterministic obligation language. Binding requirements MUST use explicit required or prohibited terms such as `must`, `must not`, `required`, `prohibited`, `fail` or `hold`. Permission terms such as `may` or `allowed` may define only a bounded permission with a declared owner, conditions, and witness. Advisory terms such as `should`, `prefer`, `can` or `likely` MUST NOT define requirements or gate behavior, or weaken an owner obligation. An optional statement MUST name the decision owner, the conditions for choosing it, and the witness that proves the choice stayed within owner scope.
- Generated plans, checklists, prompt packs, summaries, and examples are non-authoritative unless each normative item cites or routes to the owner that makes it binding.
- Treat a missing owner, conflicting owners, unknown optionality/defaultability, a missing witness or unclear precedence as an authority gap (FP-13, FP-27). Stop and report the gap before editing or executing. Never infer, duplicate, downgrade or continue through a substitute path.

### 3) No Orphan Code / No Orphan Docs
Code MUST be reachable from a workflow or a documented entrypoint. Docs MUST be reachable from a docs index or README. Unreferenced helpers and floating docs are prohibited. Apply the coding and documentation owners in the gate table above.

## Supporting Docs (Three Layers)
This constitution is always active and ranks highest. `docs/agents/governance/` applies to every task. `docs/agents/interfaces/` (external systems touched) and `docs/agents/playbooks/` (the user's design choices for internal layers) apply when the task touches their layer. Reading starts at `docs/agents/agents_index.md`. `Orchestration.md` Task agents and focused exploration owns how `agents-manifest.yaml` routes Governance Agent authorities.
