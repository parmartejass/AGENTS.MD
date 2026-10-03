---
doc_type: reference
ssot_owner: docs/project/goal/goal.md
update_trigger: project objective, accepted intent, or verification requirements change
---

# Goal

## Objective
- Maintain a reusable, repo-agnostic governance pack for autonomous coding agents.

## Acceptance criteria
- Apply the single documentation size/cohesion declaration in `docs/agents/governance/documentation/documentation.md` to every repository Markdown file, including authorities, reports, templates, routers, and operational assets.
- Preserve meaning by coherent owner decomposition, never minification or exemptions.
- `AGENTS.md` MUST retain the complete user-supplied Fundamental Principles in authorized wording, order, and MUST tone as the highest repository-internal authority.
- Owner-local identifiers supply stable routes without a second principles document or policy registry.
- Every lower document MUST be fully audited for owner derivation, necessity, duplication, and weakened obligations.
- Each declared lower owner retains its jurisdiction-specific rules, contracts, safeguards, mechanics, examples, and verification requirements.
- Pruning removes demonstrated duplication or conflict only; keyword replacement or acknowledgment is not acceptance.
- Constitutional application, complete binding user intent, user-decision precedence, and automatic durable-record maintenance stay governed by `AGENTS.md` without user reminders or file identification.
- `Orchestration.md` remains the sole agent-lifecycle owner, including Main's user-representative role, source separation, and independent review.
- Supporting surfaces route to that owner; a parallel project lifecycle is Prohibited.
- Foundation acceptance requires one constitutional membership declaration, lifecycle-owned source/application witnesses, unconditional consumer routing, and preserved source isolation.
- Static validation cannot substitute for parent accountability.
- `agents-manifest.yaml` routes Governance Agent governance authorities only.
- Governance research corpus membership comes from the governance-core public `resolve_documents` contract and router topology.
- Governance-core consumers retain one plain-data public API with deterministic check ordering and reconciliation behind the boundary.
- Structural validation MUST NOT claim source equality, semantic compliance, live agent obedience, or uninstrumented timing evidence.
- Project docs retain declared durable project facts and owner routes; reusable source assets stay under `docs/agents/`.
- Retired runtime projections, tracked root runtime copies, and reference application templates remain retired.

## Durable intent
- 2026-10-03: explicit user direction to consolidate the packaged-folder rules into one top-level instruction governed by `AGENTS.md`: the rules for scalable, reusable code must always be followed so SRP modules stay inside their SSOT jurisdiction as packaged folders, and every code or doc artifact created goes through a stable SSOT/SRP module inside an existing or new packaged folder with a stable public entrypoint, without hardcoding, always by reuse, extension, or a new packaged-folder build. The user asked to confirm that the default native-language packaged folder, with stable internal SRP modules and their public entrypoint, is the fundamental rule; called the `<feature>_main` convention an old learning introduced before they knew much about packaged folders; and said older custom instructions "may not" be the best default structured-practice wording. This extends, without withdrawing, the 2026-09-20 Jurisdictional Decomposition and packaged-folder records below. It is requested intent, not an implementation or compliance claim; current owners stay in force until the substantive workflow updates them; validate against the resulting owner contracts and independent review, and re-evaluate when user intent or those contracts change.
- 2026-10-03: explicit user decision (scope) for full migration: a new `AGENTS.md` packaged-folder rule, the affected lower governance docs, and governance-core converted to a native Python package (`__init__.py` public API, `__main__.py` launcher) with its tests and README. `scripts/check_governance_core/check_governance_core_main.py` is removed with no compatibility shim; the user accepted that vendored repositories update their check command when they bump the submodule. This supersedes the `scripts/<feature>/<feature>_main.py` entrypoint convention of the coding owner and `SSOT-DEC-003`, which stays enforced until the migration lands. Pending implementation and independent review; re-evaluate if that migration stops or user intent changes.
- 2026-10-03: explicit user decision to keep the `<authority>_index.md` docs-router naming, recorded as a retained custom exception to the packaged-folder rule. Agent-verified provenance: commit `3ca56b9` (2026-04-17) introduced this naming together with `*_main.py`. Agent-proposed re-evaluation trigger: a user decision revisiting docs-folder entry naming, or any change to the `SSOT-DEC-003` router contract.
- 2026-10-03: explicit user decision to defer packaging `X-Bookmarks Import/` (non-owner workspace under `SSOT-DEC-001`) and record it as non-conformant with the packaged-folder rule; agent-verified 2026-10-03: it contains no `__init__.py`, its modules sit flat at the workspace root or as directly launched skill scripts, and its folder name is not an importable Python package name. Migrating its existing governance-core import stays within the full migration (agent derivation: every active consumer is migrated). Agent-proposed re-evaluation trigger: the next non-trivial change to its code beyond that import, any `SSOT-DEC-001` change, or a user request.
- 2026-10-03: explicit user decision that when nested subagents are unavailable, the owning task agent handles its explorer jurisdictions itself because it is responsible, not Main through proxy dispatch (user: "the owing subagents can handle it as it's responsible"). Owner: `Orchestration.md` Task agents and focused exploration. Re-evaluate when that owner or the runtime spawning capability changes.
- 2026-09-27: explicit user decision to consolidate scattered prompt-to-project-doc instructions into one stable SSOT/SRP block in `AGENTS.md`, capturing admitted durable intent before dependent substantive work. This is requested intent, not an implementation or live-compliance claim; validate against the resulting owner contract and independent review, and re-evaluate when user intent or that contract changes.
- 2026-09-27: explicit user verification decision requires both `claude-fable-5-1` and `claude-opus-5-5` with `--effort xhigh` to complete read-only reviews of the same frozen final result of the prompt-intake consolidation, and requires the final independent Review Agent to disposition both reviews before Main declares full success. This verification remains pending until both exact-model reviews and their finding dispositions are recorded; they do not authorize mutation or replace repository checks or independent review, no model substitution is allowed, and any post-review change to the frozen result requires both reviews again unless a later explicit user decision supersedes this requirement.
- 2026-09-20: user decision that AGENTS.md's top SSOT rule owns the universal "Resolve once before fan-out" standard as part of the existing SSOT/SRP/no-duplication/stable-public-interface intent; the Bilty case is illustrative only.
- 2026-09-20: user decision (chat-mined 2026-09-20) that this repository is the baseline every downstream harness instruction file imports; "this project is the highest governing repo which i import in all".
- 2026-09-20: user decision (chat-mined 2026-09-20) that replies use few words per line, one item per line; owner: prompt-authoring; "reply in few words per line, one finding per bullet".
- 2026-09-20: user decision (chat-mined 2026-09-20) that questions to the user are jurisdiction-level choices with a named default; owner: prompt-authoring; "I can just answer through jurisdiction fundamental".
- 2026-09-20: user decision that the fundamentals of speed (FP-03) and the Fundamental Principles in `AGENTS.md` are the main choice for every baseline decision.
- 2026-09-20: user decision that `docs/agents/` has three stable layers: `governance/` (task jurisdictions; the task type selects the owner), `interfaces/` (external systems the work touches), and `playbooks/` (the user's design and product choices for internal layers); every interfaces and playbooks owner carries one YAML `baseline` block.
- 2026-09-20: user decision that each owner doc holds only its own internal single-responsibility content with no cross-doc relations (no route or applies lines, no paths to other owners); `docs/agents/governance/ssot/ssot.md` is the single relation owner (concept -> owner -> path plus jurisdiction hand-offs), and a rule depending on another jurisdiction names it by its jurisdiction noun.
- 2026-09-20: user decision that numeric prefixes are dropped from every `docs/agents/` folder name and title; each jurisdiction is one packaged folder with its owner doc and router, sub-docs only inside the same folder.
- 2026-09-20: user decision that skills, settings, and MCP are governance standards under `docs/agents/governance/`, not a parallel asset tree.
- 2026-09-20: user decision that reserved jurisdictions (listed in `docs/project/architecture/architecture.md`) are declared on first use through a supersession record; nothing is created for them in advance.
- 2026-09-20 (confirmed by the baseline-criterion decision above, applied) S-1 os-processes: interface moves from PID-scoped termination to OS containment.
- 2026-09-20 (confirmed by the baseline-criterion decision above, applied) S-2 config: interface moves to the standard-library JSON/TOML reader.
- 2026-09-20 (agent-proposed declaration of a reserved jurisdiction, applied) S-3 packaging: owner declared under `docs/agents/playbooks/packaging/`.
- 2026-09-20 (confirmed by the baseline-criterion decision above, applied) P-3 governance-learning: `subagent` is a permitted packaging form.
- 2026-09-20: user decision that `docs/agents/playbooks/` is now the design-choice layer of owner docs (config, run outcomes, I/O batch, GUI guidelines), not the retired cross-cutting template folder; this supersedes the folder meaning of the 2026-09-19 dissolution note while task scaffolds stay inside their jurisdiction owner.
- 2026-09-20: user decision that `AGENTS.md` carries a highest operating rule, Jurisdictional Decomposition: every prompt is broken into SSOT/SRP jurisdictions first, each built inside its stable packaged folder behind its interface, API, or caller, reusing and consolidating existing owners; building literally to the prompt is prohibited. It absorbs the former "SSOT Jurisdiction and Purification" gate.
- 2026-09-19: user decision that the Excel hierarchy (OOXML as the stable direct interface, COM only for what surgical OOXML cannot do, near-instant processing as driver) is the universal selection hierarchy: the stable, universal, direct interface of the underlying format, platform, language, or system, never an external wrapper or patchy workaround, is the baseline choice in every jurisdiction.
- 2026-09-19: user decision that `AGENTS.md` owns this as one stable Baseline Interface Rule hard gate; agents MAY supersede a declared baseline in real work only with recorded justification (baseline, verified gap, evidence, preserved outcomes) promoted into the owning jurisdiction so baselines improve (for example PDF libraries per task, or language-specific baselines) without restating the rule everywhere. Mechanics: `docs/agents/governance/principles/principles.md` Stable baseline interface; each domain owner declares its `baseline` block.
- 2026-09-19: user decision to consolidate every governance instruction into single-jurisdiction SSOT owner docs with terse per-line obligations.
- 2026-09-19: playbooks live inside their jurisdiction owner; the cross-cutting playbooks folder is dissolved and duplication/drift removed.
- 2026-09-19: foundations are unchanged except path migration and the user-authorized Baseline Interface Rule hard gate in `AGENTS.md`; no obligation is weakened by the consolidation.
- 2026-09-15: user clarification supersedes FP-03's decision-only scope with a universal end-to-end performance design goal; the amended constitutional paragraph owns goal and timing values.
- 2026-09-15: Excel creation and updates share the stable selection block in `docs/agents/interfaces/excel/excel.md`; earlier general-workbook-library eligibility is superseded.
- 2026-09-15: lower owners retain domain mechanics and honest measurement evidence without copying or narrowing the constitutional goal.
- 2026-09-13: user deduplication direction removes demonstrated duplicate obligations and mutable values through their SSOT owners, with complete consumer migration.
- 2026-09-13: implementation and declaration facts resolve through their coding/docs owners and `docs/project/architecture/architecture.md`.
- 2026-09-13: accepted foundation placement/loading, module API boundary, jurisdiction-driven decomposition, and distinct code-review/documentation-limit meanings remain intact.
- 2026-09-13: user foundation decision keeps current locations and makes loading mandatory, with the parent accountable before work.
- 2026-09-13: `AGENTS.md` Mandatory Foundations owns membership and rationale; `Orchestration.md` owns loading, application evidence, and source boundaries.
- 2026-09-13: this supersedes the earlier two-owner Main read allowance and conditional foundation profiles; code-blind Main, exact principles, deeper obligations, and owner-declared choices are preserved.
- 2026-09-13: no relocation or second policy layer is intended.
- 2026-09-13: module-boundary consolidation supersedes earlier wording of `AGENTS.md` FP-13 and FP-15; unrelated principles and delegated mechanics remain in force.
- 2026-09-08: user documentation direction makes concise maintained documentation the primary durable governing record for reasoning and work.
- 2026-09-08: routine owner maintenance covers all material future-decision knowledge, consequential uncertainty, and agent decisions with origin, basis, and verification status.
- 2026-09-08: supersession must establish the complete baseline, justify better outcomes, preserve requirements or complete authorized migration, verify the design, and record owner evidence.
- 2026-09-08: recording never verifies a claim and never self-authorizes.
- 2026-09-08: user direction to question and justify every retained word through its jurisdiction, refactor and prune existing owners, and preserve the full force of the supplied principles.
- 2026-09-08: lower documents cannot become alternate fundamental authority; each document serves its own SSOT jurisdiction.
- 2026-09-08: shorter wording alone is not acceptance; demonstrated losses require repair at that owner.
- Earlier accepted constitutional, user-intent, source-only asset, and finite-lifecycle outcomes remain in force through the owner routes above.
- Completed non-trivial work stays auditable through `docs/project/changelog/changelog.md` after durable fact promotion.
- Project truth and closure-surface authority resolve through architecture's `SSOT-DEC-004` route.
- Working plans and audit ledgers remain ephemeral; selected durable facts are promoted under `docs/agents/governance/documentation/documentation.md`.

## Boundary
- This file owns stable project purpose, accepted scope, non-goals, and verification intent.
- Architecture, data truth, project rules, closure records, and operational learnings keep their routed project owners.
- Reusable policy remains outside this branch.

## Current Summary
- This governance-pack source preserves constitutional authority in `AGENTS.md` and delegated authority through declared owner routes.

## Branch-local owner subdocs
- None currently declared.
- Apply `docs/agents/governance/documentation/project-docs-template/project-docs-template.md` when a stable intent cluster needs a separate owner.

## Non-goals
- This repo does not define domain business logic or a second governance framework.
- Static validation is not a semantic or platform-performance guarantee.

## Verification
- Run root `README.md` Checks.
- For principle updates, compare canonical paragraphs with the authorized source after line-ending normalization only.
- Reconcile every scoped document's full-read outcome and review the resulting owner graph under `Orchestration.md`.
- Re-verify when principles, lower-doc derivation, the public checker boundary, or accepted intent changes.
