# AGENTS.md - Canonical Agent Constitution (SSOT / No Duplicates)

This file is the constitutional source of truth for autonomous coding agents in this repository.

MUST follow the Mandatory Foundations declaration below; `Orchestration.md` owns role-specific loading, application, missing-source handling, and parent accountability. If instruction files conflict, **`AGENTS.md` wins**.

<!-- orchestration-authority: Orchestration.md -->

`Orchestration.md` is the sole owner of agent roles, read/mutation/delegation boundaries, the plan and council lifecycle, execution and review phases, correction limits, and terminal decisions. Supporting docs, manifests, prompts, and project docs must route to that owner without restating its workflow.

Main is constitutionally the user's code-blind, single communication and decision hub. It preserves complete controlling intent, challenges drift, tracks workflow state, and alone declares terminal outcomes; its detailed contract is owned by `Orchestration.md`.

## Fundamental Principles (Highest Repository Authority)

These principles are the highest repository-internal authority. They supersede every weaker or conflicting statement in this file and every lower document, manifest, scaffold, projection, and agent-originated record. Higher-priority platform instructions remain controlling. Each lower document MUST retain binding authority within its declared SSOT jurisdiction, including its necessary rules, contracts, mechanics, examples, and verification requirements. Lower documents MUST NOT redefine, soften, duplicate, or conflict with these Fundamental Principles; constitutional precedence resolves conflicts without removing delegated authority or its necessary domain-specific instructions.

This section owns the canonical structural contract: exactly one block delimited by standalone `<!-- fundamental-principles:start -->` and `<!-- fundamental-principles:end -->` lines; within it, consecutive unique `### FP-01` through `### FP-35` headings each precede exactly one blank-line-delimited paragraph beginning `MUST `. Identifiers provide stable owner-local references; the paragraphs retain their exact wording and order as authorized by the user. Structural validation checks this shape only; source equality and semantic compliance require their own evidence under FP-33.

<!-- fundamental-principles:start -->

### FP-01

MUST enforce these instructions as binding decision, execution, and completion criteria throughout every analysis, plan, implementation, review, verification, and maintenance action. Reading or acknowledgment is not compliance.

### FP-02

MUST establish outcomes first, evaluate viable approaches against every governing constraint, and deepen reasoning or redesign until every outcome is satisfied. Never weaken outcomes to fit an implementation.

### FP-03

MUST enforce performance requirements as first-principles design constraints before selecting an approach: complete controllable routing, configuration, validation, and interface decisions within 100 milliseconds; acknowledge actions within 100 milliseconds; show active status beyond 500 milliseconds. Meet these limits through reasoning and architecture, never haste, weakened validation, or shortcuts.

### FP-04

MUST determine jurisdiction, ownership, magnitude, dependencies, blast radius, and affected consumers before acting.

### FP-05

MUST read every governing and touched source in full; trace owners, consumers, dependencies, verification, configuration, and documentation.

### FP-06

MUST convene an independent council before implementation or mutation; challenge the design against governing requirements and resolve every material objection before proceeding.

### FP-07

MUST define objectives, inputs, outputs, constraints, risks, failure states, side effects, and completion evidence before implementation.

### FP-08

MUST review and correct defects at their owning SSOT jurisdiction; enforce SRP, eliminate duplication and drift, and reuse or extend stable jurisdictions. You are authorized and required to rewrite, replace, consolidate, and delete in-scope code without further approval; migrate affected consumers, preserve required behavior and proven compatibility, and remove superseded implementations before completion.

### FP-09

MUST justify each proposed addition by what it replaces, extends, or makes obsolete; complete identified replacement and removal in the same change. An additive workaround that leaves the architectural defect active is incomplete.

### FP-10

MUST derive behavior only from explicit configuration, governing contracts, or user authority; never invent mutable rules.

### FP-11

MUST produce identical outcomes from identical validated inputs under unchanged maintained configuration.

### FP-12

MUST assign every mutable rule exactly one SSOT owner and eliminate duplicate authority.

### FP-13

MUST give every package one responsibility and one owner; assign each shared capability one stable contract. Every module or package of any size must expose exactly one stable public interface/API; internals must be private, fully hidden behind that interface, freely restructurable, and any caller dependency on them is a defect.

### FP-14

MUST define each contract’s inputs, outputs, authorized actions, side effects, errors, compatibility, versioning, and extension rules.

### FP-15

MUST keep implementations cohesive; reuse established shared logic and place extensions within the owning jurisdiction; never create parallel authority.

### FP-16

MUST preserve compatibility only for identified active consumers or declared historical data formats; preserve required behavior and evidence, not obsolete implementations for hypothetical use.

### FP-17

MUST use the most direct authoritative interface covering the full required and authorized surface, without artificial restrictions.

### FP-18

MUST discover changeable capabilities from authoritative contracts, never hardcoded lists; encode closed domains once and never freeze open-world capabilities.

### FP-19

MUST route extensible types through discovered or registered handlers behind one contract; extend capabilities without modifying consumers.

### FP-20

MUST preserve unknown inputs, perform authoritative discovery, and return explicit unsupported outcomes when unresolved; never guess, crash, or lose data.

### FP-21

MUST permit adapters only for contract normalization, unavailable interfaces, or contracted safety; document justification, ownership, and review; prohibit silent fallback.

### FP-22

MUST keep environment-dependent paths, devices, mappings, identifiers, and integrations in directly correctable, owner-maintained configuration.

### FP-23

MUST separate structural validation from operational validation; unrelated operational defects must never block valid work.

### FP-24

MUST reject ambient state as required input or confirmation; obtain each required value explicitly during the active workflow and preserve its authorized scope.

### FP-25

MUST permit deadlines, termination, and retries only through explicit contracts; keep retries bounded, visible, idempotent, and recoverable.

### FP-26

MUST bound every search by configured scope, deterministic ordering, validation, termination, and measured cost.

### FP-27

MUST block ambiguous, invalid, stale, or missing resolution unless its governing contract explicitly permits it; provide correction guidance.

### FP-28

MUST serve repeated lookups through direct keyed access or bounded candidate sets; never repeat blind scans.

### FP-29

MUST assign every in-scope item an explicit outcome; report the state, reason, and next action for every non-success or pending result.

### FP-30

MUST obtain explicit confirmation before destructive, disruptive, externally visible, or difficult-to-recover actions outside existing authorization. Authorized in-scope code changes require no further approval. Cancelling a proposed action must leave existing state unchanged.

### FP-31

MUST verify side effects, revert transient or unintended changes, release resources, preserve unrelated work and required compatibility, and update affected consumers.

### FP-32

MUST verify the complete resulting design against the original requirements after implementation. Passing tests, closing findings, or completing operations alone does not establish SSOT, SRP, architectural correctness, or completion.

### FP-33

MUST maintain a requirement-to-evidence trace throughout the task; provide concrete completion evidence for every applicable requirement and a scope-based reason for every non-applicability claim. Resolve controllable gaps before declaring completion; explicitly report every unmet or unverified requirement.

### FP-34

MUST choose the simplest complete design, update governing documentation, create nothing unless requested or contractually required, and report remaining blockers.

### FP-35

MUST default newly requested Codex project threads to the saved project checkout (`local` environment); create a separate Codex git worktree only on explicit user request.

<!-- fundamental-principles:end -->

## Mandatory Foundations
foundation_contract_version: 1
<!-- foundation-authority: constitution=AGENTS.md -->
<!-- foundation-authority: orchestration=Orchestration.md -->
<!-- foundation-authority: coding_principles=docs/agents/35-coding-principles/coding-principles.md -->
<!-- foundation-authority: docs_policy=docs/agents/25-docs-ssot-policy/docs-ssot-policy.md -->

This section is the sole unconditional foundation-membership owner. Version 1 requires exactly one operative declaration for each named role, no unknown roles, and unique, exactly spelled, governance-root-relative Markdown files; constitution must identify this owner and orchestration must match the lifecycle route above. Missing, malformed, duplicate, unsafe, aliased, or unreadable declarations or targets fail explicitly; examples in fences, blockquotes, or indented code are non-operative. Marker order defines reading order. Membership changes update this owner and its consumers together; role mechanics remain in `Orchestration.md`.

Under FP-01, FP-02, FP-05, FP-12, and FP-33, the principles define required outcomes and these delegated foundations keep their governing mechanics consistently available. Unconditional membership prevents task-signal selection from skipping a foundation; it does not replace application evidence or extend a delegated owner's substantive scope. Deeper owners retain all applicable binding duties; profiles discover sources, and playbook or preference choices exist only where their owner explicitly permits them.

## Objective
The Fundamental Principles define completion. Critical concepts and their owners MUST remain searchable through repository text search and declared routes.

## Vendored Authority + Path Resolution (SSOT)
When vendored, `.governance/AGENTS.md` and `.governance/Orchestration.md` remain the constitutional and lifecycle authorities; root AGENTS/CLAUDE files are loader stubs routing to both. Governance-root paths resolve relative to the directory containing `AGENTS.md` and `agents-manifest.yaml`; project-owned paths (`docs/project/...` and project README) resolve relative to the project root, the parent of `.governance/`. Do not rewrite governance-root path strings when vendoring.

## Submodule Workflow Rules (Hard Gate)
The governance source repo is `https://github.com/parmartejass/AGENTS.MD.git`. Edits inside `.governance/` belong to that submodule: NEVER commit them from the parent directory. Commit in the governance repo; after landing, the parent may update only the submodule SHA pointer.

## Prime Directive: Verify, Then Trust
FP-10, FP-20, and FP-27 govern factual resolution. Repository paths, dependencies, symbols, APIs, flags, and config keys MUST have a verified source; unresolved values remain `Unknown` with correction guidance.

## First-Principles Protocol (Hard Gate)
MUST apply `docs/agents/00-principles/principles.md` as the delegated owner for model/scope, authority-first correction, structural consolidation, task control artifacts, design, and proof obligations; its diagnosis route owns the required defect vocabulary.

## First-Principles + SSOT + Evidence Model (Hard Gate)
MUST apply `docs/agents/00-principles/evidence/evidence.md` as the delegated owner for R/S/D truth, invariant and authority-application witnesses, evidence presentation, verification floors, rewrite risk, and measured performance boundaries.

That owner retains **Invariants + Witnesses**, **Authority-Constrained Reasoning**, **Scannable Output Shape**, **Verification Floors**, and **Rewrite Risk Policy** with their binding scope and verification duties.

### Authority Graph (Required for non-trivial systems)
MUST apply `docs/agents/35-coding-principles/coding-principles.md`.

### Implementation Write State Machine + Two-Phase Commit (When repository or external writes occur)
MUST apply `docs/agents/70-io-data-integrity/io-data-integrity.md`.

### Bias-Resistant Debugging (Hard Gate)
MUST apply `docs/agents/00-principles/diagnosis/diagnosis.md`.

## Agent Orchestration (Hard Gate)
All delegation, role boundaries, planning, principle review, confirmation, execution, final review, critical correction, and terminal behavior MUST follow `Orchestration.md`. No other active surface may define or extend that lifecycle.

Project docs own durable repository truth. Plans and agent working records remain ephemeral and untracked unless a durable fact is promoted into its declared project-doc owner.

## Governance Auto-Edit Gate (Hard Gate)
Governance learnings auto-edit requires explicit invocation of its playbook; otherwise learning-derived suggestions remain proposals. A directly requested owner update is authorized task work. Scope defaults to governance docs/playbooks and `agents-manifest.yaml`; its plan, review, confirmation, execution, and final review follow `Orchestration.md`.
Confirmation gate: include new rules, invariants, jurisdictions, or owners not grounded in existing authority in the plan and satisfy FP-30 through `Orchestration.md`. AGENTS edits require explicit authorization covering the owner update, except changes limited to this Confirmation gate. Existing authorization satisfies FP-30; do not request it again.

## Non-Negotiables (Hard Gates)
### 1) Single Source of Truth (SSOT) — The Foundational Rule
FP-08 through FP-16 govern SSOT ownership and consolidation. The concept-to-owner route is `docs/agents/20-sources-of-truth-map/sources-of-truth-map.md`.

**SSOT jurisdiction and duplication pruning rule:** apply those principles at the highest owning contract, schema, config, validator, registry, public entrypoint, or data authority. Non-owner callers, docs, tests, scripts, checkers, projections, and generated artifacts MUST consume that owner; they MUST NOT define private rules or preserve owner defects through wrappers, shadow contracts, or test-only allowances.

Runtime workflow composition mechanics are owned by `docs/agents/35-coding-principles/coding-principles.md`; config and changing source values are owned through `docs/agents/40-config-constants/config-constants.md` and their declared data authorities.

**File/folder structure IS SSOT enforcement.** Related artifacts within one authority boundary MUST share the existing SSOT parent. A broader domain's non-owner workspace path requires a governance authority decision declaring the canonical owner, permitted non-owner path, and forbidden duplicates. Scattered same-authority artifacts MUST be consolidated within the authorized change, with affected consumers migrated and required behavior preserved.

### 1A) Instruction Derivation Gate (Hard Gate)
Every agent-authored normative statement must derive from a declared SSOT owner before it is treated as an instruction, requirement, checklist item, plan step, prompt scaffold, doc record, or user-facing obligation.

Hard rules:
- Classify each source before deriving obligations: owner, routed support, reference/example, scaffold, generated artifact, user intent, or explicit user decision.
- Only a declared owner defines obligations. Non-owner text routes, cites, illustrates, scaffolds, or records evidence; it does not create policy, weaken policy, broaden policy, or select runtime behavior.
- Controlling user intent includes all binding user messages in the current workflow, not only the latest prompt. A user message contains an explicit user decision when it states a desired outcome, correction, constraint, supersession, acceptance criterion, data-truth assertion, or owner update. Within its stated scope, an explicit user decision supersedes conflicting agent-originated assumptions, plans, council conclusions, summaries, reports, stale recorded decisions, or implementation choices. Preserve unrelated binding user intent when applying a later decision. User silence, user inability to monitor autonomous agent choices, generated artifacts, or prior agent consensus never converts an agent-originated choice into a user decision.
- Before decision-critical work, agents must retrieve and apply relevant durable project authority records through their assigned source jurisdictions under `Orchestration.md`; the user must not have to identify those records or restate their binding facts. Apply explicit user supersession through the owning authority rather than letting stale agent-originated records override the user.
- During authorized work, agents must automatically maintain the declared documentation owners of all material knowledge relevant to future reasoning and decisions, without waiting for user reminders or file identification. Apply `docs/agents/25-docs-ssot-policy/docs-ssot-policy.md` for admission, concise placement, provenance, uncertainty, agent-decision attribution, safe supersession, and source-owned value routing. Documentation is the primary durable governing record for reasoning and work; recorded claims neither verify themselves nor create authority. Temporary coordination and raw sensitive prompts remain excluded.
- User-prompt supersession does not make unverifiable runtime facts true, bypass required verification, or authorize destructive, disruptive, externally visible, or difficult-to-recover side effects beyond the user's stated scope. If an explicit user decision changes reusable governance policy, update the owning governance authority through the SSOT path instead of leaving the prompt as a standing exception.
- Derived statements must preserve the owner's scope, preconditions, ordering, optionality/defaultability, allowed states, terminal outcomes, and verification witness. If the owner declares exact terms, states, phases, reason codes, or outcome values, use those owner-declared terms or cite the owner instead of restating them.
- Derived normative statements must use deterministic obligation language. Binding requirements must use explicit required/prohibited terms such as `must`, `must not`, `required`, `prohibited`, `fail`, or `hold`. Permission terms such as `may` or `allowed` may define only a bounded permission with a declared owner, conditions, and witness. Advisory terms such as `should`, `prefer`, `can`, or `likely` must not define requirements, gate behavior, or weaken an owner obligation. If a statement is optional, it must name the decision owner, the conditions for choosing it, and the witness that proves the choice stayed within owner scope.
- User prompts provide intent, scope, acceptance criteria, and explicit user decisions. Repo owners constrain allowed behavior unless the explicit user decision requests an owner update or supersession through the SSOT path. A conflict between prompt intent and a declared owner is an authority conflict until the owner is updated or the task is held; it is not permission for an agent to synthesize a replacement rule.
- Generated plans, checklists, prompt packs, summaries, and examples are non-authoritative unless each normative item cites or routes to the owner that makes it binding.
- Missing owner, conflicting owners, unknown optionality/defaultability, missing witness, or unclear precedence is an authority gap. Stop and report the gap before editing or executing; do not infer, duplicate, downgrade, or continue through a substitute path.

### 1B) SSOT Jurisdiction and Purification (Hard Gate)
SSOT jurisdiction defines where a decision-critical fact, rule, state, side effect, lifecycle, contract, output, witness, finding, or verification obligation is owned. The requested file or symptom is an entry into that authority graph, not its scope ceiling. Apply FP-04, FP-08, FP-09, FP-12, and FP-27 across affected owners and consumers; implementation evidence mechanics are owned by `docs/agents/35-coding-principles/coding-principles.md`.

### 2) No Duplicates (Operational Meaning)
MUST apply `docs/agents/35-coding-principles/coding-principles.md`.

### 2A) No Fallback or Legacy Runtime Paths
MUST apply `docs/agents/35-coding-principles/coding-principles.md`.

### 3) No Orphan Code / No Orphan Docs
Code must be reachable from a workflow or documented entrypoint; docs must be reachable from a docs index or README. Unreferenced helpers and floating docs are prohibited. Apply the coding and docs owners below.

### 4) Logging + Explicit Failure
MUST apply `docs/agents/30-logging-errors/logging-errors.md`.

### 5) Resource Safety
MUST apply `docs/agents/70-io-data-integrity/io-data-integrity.md`.

### 6) Excel COM Lifecycle Safety (If Applicable)
MUST apply `docs/agents/50-excel-com-lifecycle/excel-com-lifecycle.md`.

### 7) GUI Thread Safety (If Applicable)
MUST apply `docs/agents/60-gui-threading/gui-threading.md`.

### 8) Security Baseline
Never hardcode secrets; use environment variables or secret stores. Refuse security weakening (such as disabling TLS validation) unless the user explicitly accepts the risk and confines it to a safe environment. Avoid shell, SQL, and template injection.

### 9) Performance & Speed (When Relevant)
MUST apply `docs/agents/00-principles/evidence/evidence.md`.

### 10) Coding Architecture — Hard Gate
MUST apply `docs/agents/35-coding-principles/coding-principles.md` before planning, adding, reviewing, refactoring, purifying, or wiring implementation code. It owns the detailed coding mechanics and evidence; independent review applies it through `Orchestration.md`. Governance, docs, repository structure, and Python safety use the `scripts/check_governance_core/check_governance_core_main.py` public contract; `agents-manifest.yaml` routes Governance Agent authorities only. Missing, conflicting, or inaccessible coding authority requires `hold: <reason>`.

## Governance Templates (Required)
### Change Contract (Required for behavior changes and bugfixes)
Use `docs/agents/playbooks/change-contract-template/change-contract-template.md` as the temporary scaffold; promote durable facts into their highest project owner. Keep bug/regression evidence reproducible through owner docs, tests, fixtures, and verification output; route additional evidence through docs-policy with ownership and update triggers.

### Standard Log Schema (Required when logs are emitted)
Full schema: `docs/agents/playbooks/log-schema-template/log-schema-template.md`.

Apply Non-Negotiable #4 and FP-12 to the schema and reason-code owner; extend the existing owner only.

## Self‑Decision Procedure (Repo‑Agnostic)
Apply FP-04, FP-05, FP-08, FP-26, and FP-28 through `docs/agents/10-repo-discovery/repo-discovery.md` and `docs/agents/05-context-retrieval/context-retrieval.md`. Discovery MUST resolve the owning constants/config, rules, workflow, logging, lifecycle, GUI, and documentation jurisdictions before the corresponding change.

## Documentation SSOT Policy (Hard Gate)
Documentation must be maintained as the primary durable governing record for reasoning and work, within each declared SSOT jurisdiction. Apply `docs/agents/25-docs-ssot-policy/docs-ssot-policy.md` before adding, changing, splitting, routing, or superseding documentation. That owner defines the required project branches and README links, admission and maintenance, safe supersession, headers, concise authoring, recursive folder contracts, and the universal documentation line limit; it must retain their binding details.

### Project docs (Hard Gate)
If a required project doc is missing, MUST create it before other changes using `docs/agents/playbooks/project-docs-template/project-docs-template.md`. The docs-policy owner declares the baseline; mutable values remain at their actual source owners.

### Docs Branching Architecture (Hard Gate)
Every docs folder exposes its owner-resolved router and routes direct children; narrative facts live in linked public leaves. Apply the docs-policy owner for all details, including payload navigation and direct narrative-leaf references.

## Code Comment Policy (Hard Gate)
MUST apply `docs/agents/35-coding-principles/coding-principles.md`.

## Supporting Docs
Start here: `docs/agents/agents_index.md`
