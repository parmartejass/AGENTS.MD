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

## Bounded Project Authority Memory
Project docs record only declared durable authority records that constrain future agent behavior until explicitly superseded. This is a docs-first authority path, not a broad memory system.

The boundary is:
- preserve what changes future allowed behavior
- reject raw transcript/session memory, temporary plans, discarded ideas, and intermediate debugging noise
- facts are owned by their declared source of truth, not by file type
- route to code/config/data/workflow owners by identifier when those owners hold the fact
- allow project docs or doc-owned artifacts to own facts only when explicitly declared as the SSOT with validation and update triggers
- keep each promoted fact in one project-doc owner
- do not create parallel project memory, session history, transcript, or authority-memory doc trees; use the required project-doc branches and triggered leaves below

Durable means binding across future sessions until superseded. Ephemeral commands, exploration, local scratch work, and routine task mechanics are non-authority by default unless they create, change, supersede, or rely on a declared authority record.

Authority-changing actions use this classification:
- `REJECT`: not durable or not authority-changing; do not record
- `ROUTE`: point to an existing owner without copying the fact
- `UPDATE`: edit the declared owner
- `CREATE`: add the minimal missing owner when no owner exists
- `SUPERSEDE`: replace an older authority through an explicit supersession link
- `ESCALATE`: stop for user/council review because owner, durability, or conflict is not clear

Placement:
- Stable objective and acceptance criteria: `docs/project/goal/goal.md`
- Active intent and current work status: triggered leaf `docs/project/goal/current-work.md`
- Project-specific protected boundaries: `docs/project/rules/rules.md`
- Verified behavior, implementation rationale, accepted tradeoffs, owner graph, and protected behavior invariants: `docs/project/architecture/architecture.md` and triggered leaf `docs/project/architecture/protected-behavior.md`
- Data-truth ownership, provenance, validation expectations, schemas, source artifacts, mappings, config/default/constant ownership, sample-data authority, workbook/header truth, machine paths, and external-system field authority: `docs/project/data-truth/data-truth.md`
- Durable operational learnings and concise change/supersession notes: `docs/project/learning/learning.md` and triggered leaf `docs/project/learning/changelog.md`
- Structured evidence artifacts: `docs/project/change-records/*.json`

Promotion rule: if a candidate record does not name the future behavior it changes, its owner, and its verification or supersession trigger, keep it out of project docs.

Precedence:
- `AGENTS.md` and active protected behavior records constrain changes first.
- The declared owner of the specific fact owns the fact.
- Routers, manifests, summaries, templates, and non-owner docs route or support only; they do not override a declared owner.
- A conflict between a declared owner and `AGENTS.md` or an active protected behavior is a supersession event. Stop, prove equivalence or request approval; do not silently choose one side.

Verified behavior records must include evidence, command or artifact, commit/version/date when available, and a re-verification trigger. A verification claim without a trigger can go stale silently and must not be treated as permanent proof.

Required project-doc branches:
- `goal/`: project objective, accepted intent, and triggered current-work handoff.
- `rules/`: standing project-specific do/don't rules.
- `architecture/`: architecture, authority graph, implementation rationale, and triggered protected-behavior records.
- `data-truth/`: data-truth ownership, provenance, validation, and routing.
- `learning/`: durable operational learnings and triggered authority changelog.

Triggered leaves:
- Create `docs/project/goal/current-work.md` only when active or paused work must affect a future agent. Clear, delete, or reset it after durable outcomes are folded into owner docs.
- Create `docs/project/architecture/protected-behavior.md` when behavior is user-protected, regression-sensitive, intentionally preserved, or replaceable only under an equivalence rule.
- Create `docs/project/learning/changelog.md` when a durable authority record is added, superseded, retired, weakened, or changed.
- Absence of an optional leaf means no project-doc record is declared in that leaf. It does not prove no runtime behavior, active work, or change exists elsewhere; agents must still check the relevant declared owners for the task.

Decision tree:
1. Ask: "What prior truth must affect this change?"
2. Classify it:
   - binding goal or accepted intent -> `goal/goal.md`
   - active handoff state -> `goal/current-work.md`
   - standing project rule -> `rules/rules.md`
   - architecture/rationale/mechanism -> `architecture/architecture.md`
   - protected observable behavior -> `architecture/protected-behavior.md`
   - data value, mapping, schema, workbook/header truth, config/default, threshold, path, source artifact, sample data, or external field -> `data-truth/data-truth.md` or the routed data owner
   - reusable verified lesson -> `learning/learning.md`
   - accepted change, tradeoff, supersession, or owner change -> `learning/changelog.md`
3. Update only the owner of each fact. If a doc is not the owner, route to the owner.
4. Do not copy large mappings, defaults, headers, tables, or config values into narrative docs unless that doc or a doc-owned artifact is the declared owner.

Validation boundary:
- Scripts may validate required files, routers, headers, route links, record IDs, allowed status values, local reference shape, and required record fields.
- Council/manual review decides whether the declared owner is correct, whether a record is durable enough, whether a doc duplicates a non-owner fact, and whether protected-behavior equivalence is proven.
- Checker-green means structure passed; it is not semantic approval.

## Docs branch rule
- The machine-readable filename contract lives in `scripts/entrypoint_contracts.json`; this doc owns the docs-family behavior that the registry encodes.
- Every directory under `docs/` must contain the canonical router file resolved from `scripts/entrypoint_contracts.json`.
- Docs routers follow the folder-owned pattern `<authority>_index.md` and must remain routing-only.
- Router files must catalog direct children only and include a `Required when:` statement for each child.
- Docs folders with narrative content must expose one-or-more router-linked public leaf markdown files in the same folder authority.
- The registry-resolved primary public leaf must exist whenever a docs folder exposes narrative content.
- Direct references to actual narrative content may target a router-linked public leaf doc; external navigation into a docs branch should enter through the folder router.
- Parent routers route to child authorities; they do not duplicate the child doc's full rules or facts.
- Artifact-first or payload directories under `docs/` are not exempt; they still need the canonical router file so the branch remains navigable.

## Rule: Declared owners own facts

These facts must have exactly one declared owner:
- constants and repeated literals
- config keys/defaults/schema
- rules/conditions/validation logic
- workflow behavior details and branching
- business/source data, mappings, workbook/sheet/header truth, portal fields, machine paths, sample artifacts, and external-system records

Allowed owners include code, config files, constants modules, schemas, input artifacts, external systems, workbooks, sample data, and project docs explicitly marked as owner. Non-owner docs may describe:
- intent (“why”) and invariants
- contracts and interfaces (reference SSOT symbols/entrypoints)
- runbooks/playbooks (reference workflow entrypoints + config keys by identifier)
- decision records (ADR-style)
- provenance, validation expectations, interpretation, and change rules for data truths owned elsewhere

Governance-level cross-project SSOT authority decisions live in `docs/agents/22-ssot-authority-decisions/ssot-authority-decisions.md`.
Project-local adoption of those decisions remains in `docs/project/architecture/architecture.md`.

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
- Project docs should use the folder purpose as the filename (`goal.md`, `rules.md`, `architecture.md`, `learning.md`).
- Numbered governance folders should use the semantic slug without the numeric prefix (`principles.md`, `docs-ssot-policy.md`, `release-checklist.md`).
- Dated evidence folders should use `evidence.md` when they need a canonical narrative leaf.
- Additional public leaf docs may coexist in the same folder authority when the router exposes them explicitly and they do not compete with the registry-resolved primary leaf.
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
When mentioning a value, prefer the SSOT identifier name, not the literal.
When describing a rule, reference the named rule function (or equivalent).

## Context injection guardrails (avoid stale-doc confidence)
Context injection should reduce bloat and prevent “random docs” from becoming implicit requirements:
- Keep always-on manifest injection minimal; inject supporting docs via narrowly-scoped profiles.
- Inject only authority owners and routers relevant to the task. Broad "all docs" context is a false-context risk.
- Under-injection is also a defect: every task class must route to the owners required to avoid silently missing authority.
- Project-doc profile injection may start with `docs/project/project_index.md`; agents must follow that router to any triggered owner leaf in scope instead of injecting optional leaves unconditionally.
- Treat injected non-owner docs as supporting context only; verify behavior against the declared owner, whether code, config, artifact, external system, workbook, schema, or project doc.
- If a manifest profile is too broad or too narrow to explain its relevance, fix the profile before relying on injected context.
- Create project-specific docs only for declared authority records or routed handoff/runbook needs, keep them minimal, and reference other SSOT owners by identifier (do not re-encode constants/rules owned elsewhere).
- If a doc might drift, tighten its `update_trigger` and avoid adding it to broad/always-on injection.
- When tooling supports it, anchor doc sections to source code locations so changes in the referenced code surface stale docs automatically (e.g., code-anchored linters).
