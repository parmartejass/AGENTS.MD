---
doc_type: policy
ssot_owner: docs/agents/governance/documentation/documentation.md
update_trigger: docs governance rules change OR new doc categories are added
---

# Documentation

Jurisdiction: docs admission and maintenance, safe supersession, concise owner records, headers, routers and public leaves, required project-doc branches and README links, payload navigation, and the structural validation boundary for all repository Markdown.

## Admission

- MUST record a concise owner fact when losing it could materially change a future decision.
- Prohibited in tracked docs: raw working transcripts, routine commands, transient coordination, discarded noise, redundant summaries.
- Prohibited in tracked docs: raw prompts containing secrets, credentials, PII, customer data, or oversized pasted artifacts; record a redacted durable statement in the owning doc instead.
- Every record MUST preserve origin, decision basis, verification status and limits, and its re-evaluation or supersession trigger.
- Agent decisions MUST be attributed as agent decisions; user silence, agent consensus, or a recorded choice MUST NOT be recorded as an explicit user decision.
- An uncertain observation MAY be material: state the observation, its evidence, its uncertainty, and the validation needed.
- An observed defect MUST NOT be recorded as intended or protected behavior.
- Recording neither verifies a claim nor grants permission; source-owned values MUST stay in their code, config, data, artifact, or external owner, and docs route to those identifiers and record only their own provenance or decision knowledge.
- Runtime consumption of a value MUST NOT transfer its fact ownership.
- Runtime status and review state MAY serve as review evidence; they MUST NOT own project truth.

## Maintenance

- MUST update the existing subject owner automatically while doing authorized work, without waiting for a user reminder.
- MUST keep exactly one maintained record per fact; when its owner is missing, MUST create only the minimum routed owner required by its stable jurisdiction.
- Unresolved ownership or authority conflict MUST produce `hold: <reason>`.
- Before claiming closure, MUST verify every material future-decision fact is maintained into its owner doc.
- Verified-behavior records MUST include evidence, the command or artifact, commit/version/date when available, and a re-verification trigger; a verification claim without that trigger MUST NOT be treated as permanent proof.

## Safe supersession

- Before changing an established approach or governing record, MUST establish the full applicable baseline: controlling intent, constraints, dependencies, affected consumers, and proven behavior.
- MUST explain how the replacement improves the outcome and preserve every required outcome or complete the already-authorized migration, then verify the resulting design and its affected consumers.
- MUST update the single owner with the material basis, the old-to-new supersession relationship, evidence, and residual uncertainty.
- MUST preserve necessary historical evidence without keeping superseded runtime authority active.
- Recording a supersession MUST NOT self-authorize new side effects; missing required evidence or authority blocks the dependent change.

## Concise owner records

- MUST use the minimum structured authority statements, short notes, lists, or tables that expose jurisdiction, facts, rationale, uncertainty, and evidence.
- Prohibited: essays, a universal record schema, or a new status/log system. Materiality selects knowledge; concision MUST preserve scope, force, ordering, exceptions, and witnesses.
- Non-owner docs MUST NOT copy large mappings, defaults, headers, tables, config values, non-owner summaries, prose implementations of business rules, or hand-maintained code blocks mirroring production code unless clearly marked as examples.
- Non-owner docs MAY describe intent and invariants, contracts and interfaces by SSOT symbol, runbooks by workflow entrypoint and config key identifier, decision records, and the provenance, validation expectations, interpretation, and change rules for data truths owned elsewhere.
- Allowed fact owners include code, config files, constants modules, schemas, input artifacts, external systems, workbooks, sample data, and project docs explicitly marked as owner.

## Reference by identifier

- When mentioning a non-owned value, MUST use the SSOT identifier and owner route; literal examples MUST be explicitly classified as examples.
- When describing a rule, MUST reference the named rule function or its equivalent.
- When tooling supports it, MUST anchor doc sections to source locations so referenced-code changes surface stale docs.
- If a doc might drift, MUST tighten its `update_trigger` and MUST NOT add it to broad profile routing.

## Required project-doc branches
- `goal/`: durable project intent, objective, acceptance criteria, non-goals, and verification intent.
- `rules/`: standing project-specific do/don't rules.
- `architecture/`: architecture, authority graph, implementation rationale, and triggered protected-behavior records.
- `data-truth/`: data-truth ownership, provenance, validation, schemas, mappings, config/default/constant ownership, sample-data authority, workbook and header truth, machine paths, external field authority, and routing.
- `changelog/`: tracked closure records for completed non-trivial work.
- `learning/`: durable operational learnings and recurring pitfalls; not a change-history surface.

## Project-doc placement

- Each required branch MUST be one exactly spelled, safe, direct folder name with a trailing slash; missing, malformed, duplicate, or unsafe declarations fail explicitly.
- Additional routed branches are allowed when declared as owner docs with scope, update trigger, and verification witness.
- Incidental project paths in constitution text, examples, or optional-leaf references MUST NOT declare required branches.
- If any required project doc is missing, MUST create it before other changes using `docs/agents/governance/documentation/project-docs-template/project-docs-template.md`, which owns the scaffold contract for baseline branches, root docs, and branch-local owner subdocs.
- Governance-core derives each branch router and primary leaf through its public filename contract.
- Root docs are jurisdiction/index surfaces; they MUST NOT absorb every branch truth when a stable cluster needs a smaller owner.
- Branch-local owner subdocs MUST live under the project-doc branch that owns the truth and MUST follow the template scaffold contract.
- `docs/project/goal/goal.md` MUST exist and owns durable project intent, objective, acceptance criteria, non-goals, and verification intent.
- A durable user-intent change MUST update `goal.md` when it changes objective, acceptance criteria, non-goals, or verification intent, and otherwise updates the owning project doc for that fact; temporary task coordination MUST NOT be stored in project docs.
- User-provided data assertions MUST preserve provenance, verification status, validation expectations, and supersession trigger while routing source-owned values to their actual data owner.
- `docs/project/changelog/changelog.md` owns tracked `Changelog` closure records; mirror-surface validity is governed by `SSOT-DEC-004` and field template/order by the release owner.
- Durable facts referenced by `Changelog` MUST resolve to their declared owner doc, code, config, data, or workflow authority before closure.
- Commit reconciliation MUST check docs-first truth against the intended commit set: changed owner docs are doc-only steering truth or carry matching implementation and verification evidence, and changed implementation is backed by existing or updated owner truth when durable behavior changes.
- Missing routes, orphan docs, stale duplicate truth, and dead artifacts introduced by the same change are owner-scoped fixes when intent is clear; unclear intent, ownership, scope, deletion, or risk requires `hold: <reason>`.

## Triggered leaves

- MUST create `docs/project/architecture/protected-behavior.md` when behavior is user-protected, regression-sensitive, intentionally preserved, or replaceable only under an equivalence rule.
- Absence of an optional leaf means only that no record is declared there; it MUST NOT be read as proof that no runtime behavior, active work, or change exists elsewhere.
- Active protected-behavior records constrain changes; a conflict requires an explicit owner supersession and a preservation or equivalence witness where applicable.

## Placement decision

1. Ask which prior truth must affect this change, then classify it:
2. binding goal, accepted intent, objective, acceptance criteria, non-goal, verification intent -> `goal/goal.md`
3. standing project rule -> `rules/rules.md`
4. architecture, rationale, mechanism -> `architecture/architecture.md`
5. protected observable behavior -> `architecture/protected-behavior.md`
6. data value, mapping, schema, workbook/header truth, config/default, threshold, path, source artifact, sample data, external field -> `data-truth/data-truth.md` or the routed data owner
7. reusable verified lesson -> `learning/learning.md`
8. closure-record fact for completed non-trivial work -> `changelog/changelog.md`
9. material behavior, tradeoff, supersession, owner change, finding, uncertainty, agent decision, implementation rationale -> the highest declared owner doc for the fact; `Changelog` may reference it but MUST NOT substitute for it
10. MUST update only the owner of each fact; a non-owner doc MUST route to the owner.

## Required project-doc linkage

- The project `README.md` MUST link `docs/project/project_index.md` and the constitution, and MUST contain a short `## Checks` section owning the deterministic verification commands.

## Required header template

Every Markdown doc (`*.md`) under `docs/` except router indexes MUST start with the header below. Router files are exempt at any nesting level (for example `goal_index.md` or `evidence_index.md`).

```
---
doc_type: policy|reference|runbook|playbook|decision|generated
ssot_owner: AGENTS.md | <module path> | <workflow registry location>
update_trigger: <what change requires updating this doc>
---
```

## Routers and public leaves

- The executable filename contract is exposed by `scripts/check_governance_core/check_governance_core_main.py`; this doc owns the docs-family behavior that contract encodes and MUST NOT restate a second naming rule.
- Every directory under `docs/` MUST contain the canonical router file resolved by that contract.
- Docs routers follow the folder-owned pattern `<authority>_index.md` and MUST remain routing-only.
- Routers MUST catalog direct children only and MUST include a `Required when:` statement for each child.
- A docs folder with narrative content MUST expose the route-owner-resolved primary public leaf, plus any additional router-exposed public leaves that do not compete with it.
- Direct references MAY target a router-linked public leaf when the caller needs that leaf's facts; branch navigation MUST enter through the folder router.
- Parent routers route to child authorities; routers, manifests, summaries, templates, and non-owner docs route or support only and MUST NOT duplicate a child doc's rules or facts, override a declared owner, or substitute for verification against that owner.
- Artifact-first or payload directories under `docs/` are not exempt and MUST carry the canonical router file; they MAY remain router-only when they catalog payload or dated-child evidence only.
- Governance-level cross-project SSOT authority decisions live in the SSOT authority-decisions owner; project-local adoption stays in `docs/project/architecture/architecture.md`.

## Operational asset carveouts

- Installable skill bundles under `docs/agents/governance/skills/<skill-name>/` are operational artifacts, identified by a local `SKILL.md`.
- `SKILL.md` frontmatter is owned by the skill runtime format, not by the docs header schema.
- Repo checks MUST exclude those operational asset paths from docs header enforcement.
- Governance docs describing these asset types MUST live directly under `docs/agents/governance/<category>/` and keep the standard docs header in the canonical leaf doc.

## Size and cohesion
documentation_line_limit: 300

- The declaration above is the sole line-limit value; governance-core consumes it without a default, and a missing, malformed, duplicate, or nonpositive declaration is an explicit validation failure.
- Counting MUST use physical LF delimiters plus one when nonempty content lacks a final LF; CRLF contributes one delimiter, an empty file has zero records, a final LF creates no phantom record, and a BOM creates no extra record.
- Every repository Markdown document is subject to it, including root authorities, reports, routers, templates, ignored, untracked and vendored files, uppercase extensions, and operational assets.
- Header-format exceptions are not size exceptions; no exemption, minification, or loss of meaning satisfies the limit.
- MUST split by stable subject responsibility inside the existing authority parent, applying SRP and SSOT recursively to nested folders.
- Each new jurisdiction MUST have one declared owner and a stable router/public boundary with direct routes and no competing authority.
- Prohibited: god files and arbitrary flat fragments.
- A split MUST move the whole coherent responsibility, migrate links and consumers, and remove superseded duplication in the same change.

## Validation boundary

- Governance-core's public contract owns structural validation, which MUST remain separate from operational validation, of inventoried Markdown physical-line counts, required baseline branches, branch routers, routed branch-local subdocs, headers and update triggers, route links, local reference shape, and orphan-subdoc absence.
- Scripts MUST NOT enforce closed truth-kind lists, exact subdoc names, semantic categories, brittle text scans, or immediate subdocs in every branch.
- Whether the declared owner is correct, whether a record is durable enough, whether a doc duplicates a non-owner fact, and whether protected-behavior equivalence is proven are decided by source-separated principle review or deterministic manual review.
- Checker-green means structure passed; it is not semantic approval.
- Under-routing is a defect: every task class MUST route to the owners required to avoid silently missing authority; broad "all docs" routing is a false-context risk.
- A manifest profile too broad or too narrow to explain its relevance MUST be fixed before relying on its routed authorities.
- Project-specific docs MUST be created only for declared authority records or routed handoff/runbook needs, kept minimal, and MUST reference other SSOT owners by identifier.
