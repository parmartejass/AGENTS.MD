---
doc_type: policy
ssot_owner: docs/agents/governance/documentation/documentation.md
update_trigger: docs governance rules change OR new doc categories are added
---

# Documentation

Jurisdiction: docs admission and maintenance, safe supersession, concise owner records, headers, routers and public leaves, required project-doc branches and README links, payload navigation, and the structural validation boundary for all repository Markdown.

## Admission

- MUST record a concise owner fact when losing it could materially change a future decision.
- MUST keep tracked docs free of raw working transcripts, routine commands, transient coordination, discarded noise, and redundant summaries.
- Prohibited in tracked docs: raw prompts containing secrets, credentials, PII, customer data, or oversized pasted artifacts; record a redacted durable statement in the owning doc instead.
- Every record MUST preserve origin, decision basis, verification status and limits, and its re-evaluation or supersession trigger.
- MUST attribute agent decisions as agent decisions.
- MUST record an explicit user decision only when the user made it explicitly; user silence, agent consensus, and recorded choices never count as one.
- An uncertain observation MAY be material: state the observation, its evidence, its uncertainty, and the validation needed.
- MUST record an observed defect as a defect, never as intended or protected behavior.
- Recording neither verifies a claim nor grants permission.
- Source-owned values MUST stay in their code, config, data, artifact, or external owner, and docs route to those identifiers and record only their own provenance or decision knowledge.
- Fact ownership of a value MUST stay with its owner when runtime code consumes the value.
- Runtime status and review state MAY serve as review evidence. Project truth MUST stay with its declared owner.

## Maintenance

- Prompt receipt, controlling-intent precedence, and capture ordering follow the constitutional User Prompt Intake and Durable Project Truth contract. This owner holds record admission and maintenance mechanics.
- Unresolved ownership or authority conflict MUST produce `hold: <reason>`.
- Before claiming closure, MUST verify every material future-decision fact is maintained into its owner doc.
- Verified-behavior records MUST include evidence, the command or artifact, commit/version/date when available, and a re-verification trigger.
- MUST treat a verification claim that lacks that trigger as provisional, not as permanent proof.

## Safe supersession

- Before changing an established approach or governing record, MUST establish the full applicable baseline: controlling intent, constraints, dependencies, affected consumers, and proven behavior.
- MUST explain how the replacement improves the outcome.
- MUST preserve every required outcome or complete the already-authorized migration.
- MUST then verify the resulting design and its affected consumers.
- MUST update the single owner with the material basis, evidence, and residual uncertainty.
- MUST record the old-to-new relationship in the project changelog.
- MUST preserve necessary historical evidence without keeping superseded runtime authority active.
- A supersession record authorizes no new side effects.
- Missing required evidence or authority blocks the dependent change.

## Concise owner records

- MUST use the minimum structured authority statements, short notes, lists, or tables that expose jurisdiction, facts, rationale, uncertainty, and evidence.
- MUST keep records free of essays, a universal record schema, and new status or log systems.
- Materiality selects knowledge.
- Concision MUST preserve scope, force, ordering, exceptions, and witnesses.
- Information-preserving compression ranks first (explicit user decision 2026-10-05).
- The shorter of two wordings that carry the same information MUST replace the longer.
- Shorter wording alone is not acceptance.
- MUST remove useless or overburdening instructions, records, and process, and keep the fundamental ones.
- Non-owner docs MUST link to, not copy, large mappings, defaults, headers, tables, config values, non-owner summaries, prose implementations of business rules, and hand-maintained code blocks mirroring production code. Clearly marked examples are the exception.
- Non-owner docs MAY describe:
  - intent and invariants;
  - contracts and interfaces by SSOT symbol;
  - runbooks by workflow entrypoint and config key identifier;
  - decision records;
  - the provenance, validation expectations, interpretation, and change rules for data truths owned elsewhere.
- Allowed fact owners include code, config files, constants modules, schemas, input artifacts, external systems, workbooks, sample data, and project docs explicitly marked as owner.

## Reference by identifier

- When mentioning a non-owned value, MUST use the SSOT identifier and owner route.
- MUST classify literal examples explicitly as examples.
- When describing a rule, MUST reference the named rule function or its equivalent.
- When tooling supports it, MUST anchor doc sections to source locations so referenced-code changes surface stale docs.
- If a doc might drift, MUST tighten its `update_trigger` and keep it out of broad profile routing.

## Required project-doc branches
- `goal/`: durable project intent, objective, acceptance criteria, non-goals, and verification intent.
- `rules/`: standing project-specific do/don't rules.
- `architecture/`: architecture, authority graph, implementation rationale, and triggered protected-behavior records.
- `data-truth/`: data-truth ownership, provenance, validation, schemas, mappings, config/default/constant ownership, sample-data authority, workbook and header truth, machine paths, external field authority, and routing.
- `changelog/`: tracked closure records for completed non-trivial work.
- `learning/`: durable operational learnings and recurring pitfalls; not a change-history surface.

## Project-doc placement

- Each required branch MUST be one exactly spelled, safe, direct folder name with a trailing slash.
- A missing, malformed, duplicate, or unsafe branch declaration fails explicitly.
- Additional routed branches are allowed when declared as owner docs with scope, update trigger, and verification witness.
- Declare required branches only in the list above; incidental project paths in constitution text, examples, or optional-leaf references are not declarations.
- If any required project doc is missing, MUST create it before other changes, within constitutional prompt intake and the orchestration lifecycle.
- Build it from `docs/agents/governance/documentation/project-docs-template/project-docs-template.md`, which owns the scaffold contract for baseline branches, root docs, and branch-local owner subdocs.
- Governance-core derives each branch router and primary leaf through its public filename contract.
- Root docs are jurisdiction/index surfaces.
- A stable cluster that needs a smaller owner MUST get its own branch-local owner subdoc instead of growing the root doc.
- Branch-local owner subdocs MUST live under the project-doc branch that owns the truth and MUST follow the template scaffold contract.
- User-provided data assertions MUST retain validation expectations alongside the provenance, verification limits, supersession trigger, and source-owner routing required by Admission.
- Changelog closure-record ownership and mirror surfaces follow `SSOT-DEC-004`.
- Durable facts referenced by `Changelog` MUST resolve to their declared owner doc, code, config, data, or workflow authority before closure.
- Commit reconciliation MUST check docs-first truth against the intended commit set:
  - a changed owner doc is doc-only steering truth or carries matching implementation and verification evidence;
  - when durable behavior changes, changed implementation is backed by existing or updated owner truth.
- Missing routes, orphan docs, stale duplicate truth, and dead artifacts introduced by the same change are fixed at their owner when intent is clear.
- Unclear intent, ownership, scope, deletion, or risk requires `hold: <reason>`.

## Triggered leaves

- MUST create `docs/project/architecture/protected-behavior.md` when behavior is user-protected, regression-sensitive, intentionally preserved, or replaceable only under an equivalence rule.
- An absent optional leaf means only that no record is declared there. It proves nothing about runtime behavior, active work, or changes elsewhere.
- Active protected-behavior records constrain changes.
- A conflict with one requires an explicit owner supersession and, where applicable, a preservation or equivalence witness.

## Placement decision

1. Ask which prior truth must affect this change, then classify it against the Required project-doc branches above and these rules:
2. protected observable behavior -> `architecture/protected-behavior.md`
3. material behavior, tradeoff, owner change, finding, uncertainty, agent decision, implementation rationale -> the highest declared owner doc for the fact
4. supersession history -> the project changelog; the changelog MAY reference an owner doc and never substitutes for owner promotion
5. MUST update only the owner of each fact. A non-owner doc MUST route to the owner.

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

- The governance-core package public contract (`scripts/check_governance_core/`) enforces the executable filename contract.
- This doc owns the docs-family behavior that contract encodes. The naming rule MUST stay in that contract alone.
- A docs folder is a packaged folder under the constitutional packaged-folder contract: its router is the public entrypoint, and the files and child folders it routes are its public members.
- Every directory under `docs/` MUST contain the canonical router file resolved by that contract.
- Docs routers follow the folder-owned pattern `<authority>_index.md` (the retained custom entry-file exception recorded in `SSOT-DEC-003`) and MUST remain routing-only.
- Routers MUST catalog direct children only and MUST include a `Required when:` statement for each child.
- A docs folder with narrative content MUST expose its route-owner-resolved primary public leaf. It MAY also expose router-exposed public leaves that do not compete with it.
- Direct references MAY target a router-linked public leaf when the caller needs that leaf's facts.
- Branch navigation MUST enter through the folder router.
- Parent routers route to child authorities.
- Routers, manifests, summaries, templates, and non-owner docs route or support only. They MUST NOT duplicate a child doc's rules or facts, override a declared owner, or substitute for verification against that owner.
- Artifact-first or payload directories under `docs/` MUST also carry the canonical router file.
- Such a directory MAY stay router-only when it catalogs only payload or dated-child evidence.
- Governance-level cross-project SSOT authority decisions live in the SSOT authority-decisions owner; project-local adoption stays in `docs/project/architecture/architecture.md`.

## Operational asset carveouts

- Installable skill bundles under `docs/agents/governance/skills/<skill-name>/` are operational artifacts, identified by a local `SKILL.md`.
- `SKILL.md` frontmatter is owned by the skill runtime format, not by the docs header schema.
- Repo checks MUST exclude those operational asset paths from docs header enforcement.
- Governance docs describing these asset types MUST live directly under `docs/agents/governance/<category>/` and keep the standard docs header in the canonical leaf doc.

## Size and cohesion
documentation_line_limit: 300

- The declaration above is the sole line-limit value.
- Governance-core consumes it without a default; a missing, malformed, duplicate, or nonpositive declaration fails explicitly.
- It counts physical line records: LF delimiters, plus one when nonempty content lacks a final LF. CRLF counts once; BOM and a final LF add nothing.
- It applies to every repository Markdown document, including root authorities, reports, routers, templates, ignored, untracked and vendored files, uppercase extensions, and operational assets.
- A header-format exception is not a size exception.
- The limit is met only with meaning intact, never by exemption, minification, or loss of meaning.
- MUST split by stable subject responsibility inside the existing packaged folder.
- A split that creates a new jurisdiction creates its child packaged folder with its router and primary public leaf.
- MUST keep each file to one coherent subject: no god files and no arbitrary flat fragments.
- A split MUST move the whole coherent responsibility, migrate links and consumers, and remove superseded duplication in the same change.

## Validation boundary

- Governance-core's public contract owns structural validation of inventoried Markdown physical-line counts, required baseline branches, branch routers, routed branch-local subdocs, headers and update triggers, route links, local reference shape, and orphan-subdoc absence.
- Structural validation MUST remain separate from operational validation.
- Scripts MUST enforce no closed truth-kind lists, exact subdoc names, semantic categories, brittle text scans, or immediate subdocs in every branch. One exception: the repeat report.
- The repeat report flags normative sentences and declared constants that repeat across files. It only warns; it never fails a run.
- The repeat report reads these three operative declarations:

normative_repeat_terms: must|never|always|only|shall|required|banned|prohibited
normative_repeat_shingle_words: 5
normative_repeat_min_percent: 60

- Whether a doc duplicates a non-owner fact, whether an owner is correct, whether a record is durable, and whether protected-behavior equivalence holds stay review decisions, made by source-separated principle review or deterministic manual review. The repeat report is a witness for them.
- Under-routing is a defect. Every task class MUST route to the owners it needs, so no authority is silently missed.
- Broad "all docs" routing is a false-context risk.
- A manifest profile too broad or too narrow to explain its relevance MUST be fixed before relying on its routed authorities.
- Project-specific docs MUST be created only for declared authority records or routed handoff/runbook needs, kept minimal, and MUST reference other SSOT owners by identifier.
