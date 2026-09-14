---
doc_type: policy
ssot_owner: AGENTS.md
update_trigger: docs governance rules change OR new doc categories are added
---

# 25 - Docs SSOT Policy (Prevent Drift)

Docs are permitted only if they do not become a second SSOT.

## File/Folder Structure and Docs
Follow the file/folder SSOT rule in `AGENTS.md`.
This doc governs how documentation participates in that structure; it does not redefine the core SSOT rule.
Universal instruction derivation across prompts, plans, checklists, examples, generated artifacts, and downstream scaffolds is owned by `AGENTS.md`; this doc applies that owner contract only to docs surfaces.
Automatic constitutional application, complete binding user-intent preservation, user-decision precedence, and durable-record retrieval and maintenance are owned by `AGENTS.md`; this doc governs the placement and promotion mechanics for those records.

Authority role:
- `AGENTS.md` owns Mandatory Foundations membership and the docs-modularity hard gate; `Orchestration.md` owns foundation loading, application, and parent accountability.
- This doc owns delegated docs-family mechanics under that gate: placement, headers, routers, public leaves, project-doc placement, owner-doc promotion, optional leaf routing, and drift-prevention boundaries.
- `scripts/check_governance_core/check_governance_core_main.py` owns the public docs router and public-leaf validation contract.
- Mandatory loading follows those owners; apply these docs-family mechanics whenever docs are added, moved, split, routed, or promoted into project authority records.

## Bounded Project Authority Memory
Documentation is the primary durable governing record for reasoning and work within each declared subject jurisdiction. Routine authorized work must maintain material knowledge that can affect future decisions, including findings, uncertainty, constraints, intent, protected behavior, rationale, agent decisions, and reusable lessons. Admission is not limited to user-provided facts or changes to future allowed behavior.

- Record a concise owner fact when losing it could materially change a future decision; exclude raw working transcripts, routine commands, transient coordination, discarded noise, and redundant summaries.
- Preserve origin, decision basis, verification status and limits, and the relevant re-evaluation or supersession trigger. Attribute agent decisions as agent decisions; user silence, agent consensus, or a recorded choice never becomes an explicit user decision.
- An uncertain observation can be material: state what was observed, its supporting evidence and uncertainty, and the validation needed. An observed defect must not be silently recorded as intended or protected behavior.
- Recording neither verifies a claim nor grants permission. Source-owned values stay in code/config/data/artifact/external owners; docs route to those identifiers and record only their own provenance or decision knowledge.
- Runtime consumption of a value does not transfer its fact ownership.
- Automatically update the existing subject owner while doing authorized work. Keep one maintained record per fact; when an owner is missing, create only the minimum routed owner required by its stable jurisdiction. Unresolved ownership or authority conflicts require `hold` under `AGENTS.md`.
- Apply `AGENTS.md` user-decision precedence and `Orchestration.md` role boundaries; plans and working evidence remain ephemeral unless a material fact is promoted through its owner.

### Safe supersession
Before changing an established approach or governing record, MUST establish the full applicable baseline: controlling intent, constraints, dependencies, affected consumers, and proven behavior. MUST explain how the replacement improves the outcome; preserve every required outcome or complete the already-authorized migration. MUST verify the resulting design and its affected consumers, then update the single owner with the material basis, old-to-new supersession relationship, evidence, and residual uncertainty. Preserve necessary historical evidence without keeping superseded runtime authority active.

Apply existing authorization under `AGENTS.md` FP-30 and `Orchestration.md`; recording a supersession does not self-authorize new side effects. Missing required evidence or authority blocks the dependent change. This is an owner-maintenance contract, not another agent lifecycle or a requirement to ask for duplicate permission.

### Concise owner records
MUST use the minimum structured authority statements, short notes, lists, or tables that expose jurisdiction, facts, rationale, uncertainty, and evidence. Do not require essays, a universal record schema, or a new status/log system. Materiality selects knowledge; concision must preserve scope, force, ordering, exceptions, and witnesses.

Baseline placement:
- Durable project intent, stable objective, acceptance criteria, non-goals, and verification intent: `docs/project/goal/goal.md`
- Project-specific protected boundaries: `docs/project/rules/rules.md`
- Verified behavior, implementation rationale, accepted tradeoffs, owner graph, and protected behavior invariants: `docs/project/architecture/architecture.md` and triggered leaf `docs/project/architecture/protected-behavior.md`
- Data-truth ownership, provenance, validation expectations, schemas, source artifacts, mappings, config/default/constant ownership, sample-data authority, workbook/header truth, machine paths, and external-system field authority: `docs/project/data-truth/data-truth.md`
- Tracked closure records for completed non-trivial work: `docs/project/changelog/changelog.md`
- Durable operational learnings and recurring pitfalls, not per-change history: `docs/project/learning/learning.md`

Promotion rule: record material future-decision knowledge in its subject owner with the evidence and limits above; route non-owned facts and omit immaterial working noise.

Precedence:
- `AGENTS.md`'s Fundamental Principles have highest repository-internal precedence; every other section and document is subordinate. Higher-priority platform instructions remain controlling.
- `Orchestration.md` owns agent roles and workflow; plans and agent working records remain ephemeral under that contract.
- The declared owner of the specific fact owns the fact.
- Routers, manifests, summaries, templates, and non-owner docs route or support only; they do not override a declared owner.
- Active protected-behavior records constrain changes within constitutional authority. A conflict requires an explicit owner supersession and preservation/equivalence witness where applicable. Apply existing user authorization through `Orchestration.md`; unresolved authority or required authorization produces `HOLD`.

Verified behavior records must include evidence, command or artifact, commit/version/date when available, and a re-verification trigger. A verification claim without a trigger can go stale silently and must not be treated as permanent proof.

## Required project-doc branches
- `goal/`: durable project intent/objective.
- `rules/`: standing project-specific do/don't rules.
- `architecture/`: architecture, authority graph, implementation rationale, and triggered protected-behavior records.
- `data-truth/`: data-truth ownership, provenance, validation, and routing.
- `changelog/`: tracked closure records for completed non-trivial work.
- `learning/`: durable operational learnings and recurring pitfalls; not a change-history surface.

## Project-doc creation contract
Additional project-doc branches are allowed when routed as declared owner docs with scope, update trigger, and verification witness.
- `docs/agents/playbooks/project-docs-template/project-docs-template.md` owns the required scaffold contract for creating baseline project-doc branches, baseline root docs, and branch-local owner-subdoc scaffold, including what each root doc must own, must not own, and how its initial jurisdiction/index shape is formed.
- This policy owns cross-doc mechanics and validation boundaries; do not duplicate the template contract here.

Root docs are jurisdiction/index docs:
- Use the creation shape owned by `docs/agents/playbooks/project-docs-template/project-docs-template.md`.
- Do not force every branch truth into the root doc.
- Do not make a root doc own all project truth for its branch when a stable cluster needs a smaller owner.

Branch-local owner subdocs:
- Live under the existing project-doc jurisdiction branch that owns the truth.
- Follow the creation and scaffold contract owned by `docs/agents/playbooks/project-docs-template/project-docs-template.md`.
- This policy validates cross-doc mechanics: routed placement, required headers, no orphan subdocs, and structural boundaries without semantic category enforcement.

Mandatory goal-branch leaf:
- `docs/project/goal/goal.md` must exist and owns durable project intent, objective, acceptance criteria, non-goals, and verification intent.
- If user intent changes durable project objective, acceptance criteria, non-goals, or verification intent, update `goal.md`. If it changes another durable fact, update the owning project doc for that fact. If it is temporary task coordination, do not store it in project docs.
- Apply the automatic retrieval and maintenance duties in `AGENTS.md` to all material future-decision knowledge, including facts from all binding user messages. Place each redacted fact in its declared project-doc owner; for user-provided data assertions, preserve provenance, verification status, validation expectations, and the supersession trigger while routing source-owned values to their actual data owner.
- Raw prompts containing secrets, credentials, PII, customer data, or oversized pasted artifacts must not be stored in tracked docs. When a durable fact must be recorded, use a redacted durable statement in the owning doc.
- Runtime status and review state may be used as evidence during review, but they do not own project truth. Before claiming closure, verify that every material future-decision fact is maintained into its owner doc.
- `docs/project/changelog/changelog.md` owns tracked `Changelog` closure records; valid/invalid mirror surfaces are governed by `SSOT-DEC-004`; field template/order is governed by `docs/agents/90-release-checklist/release-checklist.md`.
- Durable facts referenced by `Changelog` resolve to their declared owner docs/code/config/data/workflow authority before closure.
- Commit reconciliation checks docs-first truth against the intended commit set. Changed owner docs must either be doc-only steering truth or have matching implementation and verification evidence. Changed implementation must be backed by existing or updated owner truth when it changes durable behavior. Missing routes, orphan docs, stale duplicate truth, and dead artifacts introduced by the same change are owner-scoped fixes when intent is clear; unclear intent, ownership, scope, deletion, or risk requires `hold: <reason>`.

Triggered leaves:
- Create `docs/project/architecture/protected-behavior.md` when behavior is user-protected, regression-sensitive, intentionally preserved, or replaceable only under an equivalence rule.
- Absence of an optional leaf means no project-doc record is declared in that leaf. It does not prove no runtime behavior, active work, or change exists elsewhere; agents must still check the relevant declared owners for the task.

Decision tree:
1. Ask: "What prior truth must affect this change?"
2. Classify it:
   - binding goal, accepted intent, objective, acceptance criteria, non-goal, or verification intent -> `goal/goal.md`
   - standing project rule -> `rules/rules.md`
   - architecture/rationale/mechanism -> `architecture/architecture.md`
   - protected observable behavior -> `architecture/protected-behavior.md`
   - data value, mapping, schema, workbook/header truth, config/default, threshold, path, source artifact, sample data, or external field -> `data-truth/data-truth.md` or the routed data owner
   - reusable verified lesson -> `learning/learning.md`
   - closure-record fact for completed non-trivial work -> `changelog/changelog.md`
   - material behavior, tradeoff, supersession, owner change, finding, uncertainty, agent decision, implementation rationale, or verification intent -> the highest declared owner doc for the fact; the `Changelog` may reference that owner but must not substitute for it
3. Update only the owner of each fact. If a doc is not the owner, route to the owner.
4. Do not copy large mappings, defaults, headers, tables, config values, or non-owner summaries into narrative docs unless that doc is the declared owner of that current truth.

Validation boundary:
- Governance-core's public contract owns structural validation of all inventoried Markdown physical-line counts, required baseline branches, branch routers, routed branch-local subdocs, markdown headers and update triggers, route links, local reference shape, and orphan subdoc absence. Structural validation MUST remain separate from operational validation under `AGENTS.md` FP-23.
- Scripts must not enforce closed truth-kind lists, exact subdoc names, semantic categories, brittle text scans, or require every branch to have subdocs immediately.
- Source-separated principle review or deterministic manual review decides whether the declared owner is correct, whether a record is durable enough, whether a doc duplicates a non-owner fact, and whether protected-behavior equivalence is proven; lifecycle behavior remains owned by `Orchestration.md`.
- Checker-green means structure passed; it is not semantic approval.

## Documentation size and cohesion
documentation_line_limit: 300

This operative declaration is the sole documentation-line-limit value. Governance-core consumes it without a default; a missing, malformed, duplicate, or nonpositive declaration is an explicit validation failure. Count physical LF delimiters plus one when nonempty content lacks a final LF; CRLF contributes one delimiter, an empty file has zero records, a final LF creates no phantom record, and a BOM creates no extra record.

Every repository Markdown document is subject to the declaration, including root authorities, reports, routers, templates, ignored/untracked and vendored files, uppercase extensions, and operational assets. Header-format exceptions below are not size exceptions. Exceeding the declaration fails the existing docs check; no exemption, minification, or loss of meaning satisfies it.

MUST split by stable subject responsibility inside the existing authority parent; apply SRP and SSOT recursively to nested folders. Each new jurisdiction has one declared owner and a stable router/public boundary, with direct routes and no competing authority. Root docs remain concise jurisdiction/index surfaces; avoid god files and arbitrary flat fragments. Move the whole coherent responsibility, migrate links/consumers, and remove superseded duplication in the same change. Direct links to router-linked narrative leaves remain allowed.

## Required project-doc linkage
- The project `README.md` must link to `docs/project/project_index.md` and `AGENTS.md`, and contain a short Checks section owning deterministic verification commands.
- The required branch declaration above supplies the baseline. Governance-core derives each branch router and primary leaf through its existing public filename contract; incidental project paths in AGENTS, examples, or optional-leaf references do not declare required branches.
- A required branch is one exactly spelled, safe direct folder name with a trailing slash. Missing, malformed, duplicate, or unsafe declarations fail explicitly; additional routed branches remain allowed.
- If any required project doc is missing, create it before other changes using the existing project-doc scaffold owner.

## Docs branch rule
- The executable filename contract is exposed by `scripts/check_governance_core/check_governance_core_main.py`; this doc owns the docs-family behavior that contract encodes.
- Every directory under `docs/` must contain the canonical router file resolved by that public governance-core contract.
- Docs routers follow the folder-owned pattern `<authority>_index.md` and must remain routing-only.
- Router files must catalog direct children only and include a `Required when:` statement for each child.
- Docs folders with narrative content must expose one-or-more router-linked public leaf markdown files in the same folder authority.
- The route-owner-resolved primary public leaf must exist whenever a docs folder exposes narrative content.
- Direct references to actual narrative content may target a router-linked public leaf doc when the caller needs that leaf's facts and the router exposes it. Branch navigation must enter through the folder router.
- Parent routers route to child authorities; they do not duplicate the child doc's full rules or facts.
- Artifact-first or payload directories under `docs/` are not exempt; they still need the canonical router file so the branch remains navigable.

## Rule: Declared owners own facts

Fact ownership is defined by `AGENTS.md` FP-10 through FP-15 and the SSOT jurisdiction and duplication pruning rule. This document owns the binding docs-family rules and contracts declared in its Authority role, including placement, promotion, headers, routers, public leaves, project branches, owner-subdocs, optional leaves, and validation boundaries.

Allowed owners include code, config files, constants modules, schemas, input artifacts, external systems, workbooks, sample data, and project docs explicitly marked as owner. Non-owner docs may describe:
- intent (“why”) and invariants
- contracts and interfaces (reference SSOT symbols/entrypoints)
- runbooks/playbooks (reference workflow entrypoints + config keys by identifier)
- decision records (ADR-style)
- provenance, validation expectations, interpretation, and change rules for data truths owned elsewhere

Governance-level cross-project SSOT authority decisions live in `docs/agents/22-ssot-authority-decisions/ssot-authority-decisions.md`.
Project-local adoption of those decisions remains in `docs/project/architecture/architecture.md`.

Non-owner docs must not duplicate constants/default tables, prose implementations of business rules, or manually maintained code blocks mirroring production code, unless clearly marked as examples. Reference their declared owners instead.

## Required header template
Every Markdown doc (`*.md`) under `docs/` except router indexes must start with:

Router files are exempt at any nesting level (for example `goal_index.md`, `principles_index.md`, or `evidence_index.md`).

```
---
doc_type: policy|reference|runbook|playbook|decision|generated
ssot_owner: AGENTS.md | <module path> | <workflow registry location>
update_trigger: <what change requires updating this doc>
---
```

## Canonical narrative leaf naming
- The primary narrative leaf filename must resolve through the public governance-core filename contract; do not maintain a second naming rule here.
- Additional public leaf docs may coexist in the same folder authority when the router exposes them explicitly and they do not compete with the route-owner-resolved primary leaf.
- Artifact-first folders may remain router-only when they only catalog payload or dated-child evidence.

## Operational asset carveouts
Operational agent assets under `docs/agents/` can coexist with governance docs when their runtime format is not the docs header schema.

- Skills:
  - Installable skill bundles under `docs/agents/skills/<skill-name>/` are operational artifacts.
  - A skill bundle directory is identified by a local `SKILL.md`.
  - `SKILL.md` frontmatter is owned by the skill runtime format, not the docs header schema.

- Repo checks exclude those operational asset paths from docs header enforcement.
- Governance docs that describe these asset types still live directly under `docs/agents/<category>/` and must keep the standard docs header in the canonical leaf doc.

## “Reference by identifier” convention
When mentioning a non-owned value, use the SSOT identifier and owner route; literal examples must be explicitly classified as examples.
When describing a rule, reference the named rule function (or equivalent).

## Authority-routing guardrails (avoid stale-doc confidence)
Authority routing must preserve declared ownership:
- Keep constitutional authority and conflict precedence in `AGENTS.md`, and route every agent lifecycle mechanic to `Orchestration.md`.
- Use `agents-manifest.yaml` only for Governance Agent governance-authority routing; it must not route repository or project task sources.
- Foundation membership follows `AGENTS.md` Mandatory Foundations through `Orchestration.md`; task routing selects additional applicable owners and routers without making a foundation conditional. Broad "all docs" routing is a false-context risk.
- Under-routing is also a defect: every task class must route to the owners required to avoid silently missing authority.
- Role-bounded repository readers follow the relevant project router to triggered owner leaves; the Governance Agent must not read those sources.
- Treat routed non-owner docs as supporting context only; verify behavior against the declared owner, whether code, config, artifact, external system, workbook, schema, or project doc.
- If a manifest profile is too broad or too narrow to explain its relevance, fix the profile before relying on routed authorities.
- Create project-specific docs only for declared authority records or routed handoff/runbook needs, keep them minimal, and reference other SSOT owners by identifier (do not re-encode constants/rules owned elsewhere).
- If a doc might drift, tighten its `update_trigger` and avoid adding it to broad profile routing.
- When tooling supports it, anchor doc sections to source code locations so changes in the referenced code surface stale docs automatically (e.g., code-anchored linters).
