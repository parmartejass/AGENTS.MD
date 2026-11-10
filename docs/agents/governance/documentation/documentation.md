---
doc_type: policy
ssot_owner: docs/agents/governance/documentation/documentation.md
update_trigger: docs governance rules change OR new doc categories are added
---

# Documentation

Jurisdiction: docs admission, provenance, supersession, concise records, headers, routers and public leaves, required project-doc branches, and README links.

## Admission

- MUST record a concise owner fact when losing it could materially change a future decision.
- Tracked docs MUST NOT carry raw transcripts, routine commands, temporary coordination, noise, or redundant summaries.
- Tracked docs MUST NOT carry raw prompts containing secrets, credentials, PII, customer data, or oversized pasted artifacts; record a redacted statement at the owner instead.
- Every record MUST preserve origin, decision basis, verification status and limits, and its supersession trigger.
- Agent decisions MUST be attributed as agent decisions; silence, agent consensus, or a recorded choice MUST NOT be recorded as a user decision.
- An uncertain observation MAY be recorded with its evidence, uncertainty, and the validation needed.
- An observed defect MUST NOT be recorded as intended or protected behavior.
- Runtime consumption of a value MUST NOT transfer its fact ownership.
- Runtime status and review state MUST NOT own project truth.
- A verified-behavior record MUST carry its evidence and re-verification trigger.

## Safe supersession

- MUST update the single owner with the basis, the old-to-new relationship, evidence, and residual uncertainty.
- MUST preserve necessary historical evidence without keeping superseded authority active.

## Concise owner records

- Records MUST be minimal statements, lists, or tables; no essays.
- Concision MUST preserve scope, force, ordering, exceptions, and witnesses.
- Information-preserving compression ranks first (explicit user decision 2026-10-05): the shorter of two wordings carrying the same information MUST replace the longer; useless or overburdening instructions, records, and process MUST be removed and fundamental ones kept.
- Non-owner docs MUST NOT copy owned values, mappings, defaults, tables, or code; they reference the SSOT identifier and owner route, and literal examples MUST be marked as examples.

## Required project-doc branches
- `goal/`: durable project intent, objective, acceptance criteria, non-goals, and verification intent.
- `rules/`: standing project-specific do/don't rules.
- `architecture/`: architecture, implementation rationale, and protected-behavior records.
- `data-truth/`: data-truth ownership, provenance, validation, schemas, mappings, config/default/constant ownership, sample-data authority, workbook and header truth, machine paths, external field authority, and routing.
- `changelog/`: tracked closure records for completed non-trivial work.
- `learning/`: durable operational learnings and recurring pitfalls; not a change-history surface.

## Project docs

- Missing required project docs MUST exist before dependent work.
- Additional routed branches are allowed.
- Incidental project paths in constitution text, examples, or optional-leaf references MUST NOT declare required branches.
- Branch-local owner subdocs MUST live under the branch owning their truth.
- User-protected or regression-sensitive behavior MUST be recorded at its architecture owner and changed only by explicit supersession.
- Changed owner docs and changed implementation MUST agree before commit.
- The project `README.md` MUST link the constitution and `docs/project/project_index.md`, and MUST contain a `## Checks` section owning the verification commands.

## Required header template

Every Markdown doc under `docs/` except routers and `SKILL.md` (frontmatter owned by the skill runtime format) MUST start with:

```
---
doc_type: policy|reference|runbook|playbook|decision|generated
ssot_owner: AGENTS.md | <owner path>
update_trigger: <what change requires updating this doc>
---
```

## Routers and public leaves

- Every directory under `docs/` MUST contain its router `<authority>_index.md` (custom entry-file exception `SSOT-DEC-003`); the router is the docs public entrypoint, and the files and child folders it routes are its public members.
- Routers MUST remain routing-only and catalog direct children only, each with a `Required when:` statement.
- A docs folder with narrative content MUST expose the route-owner-resolved primary public leaf, plus any additional router-exposed public leaves that do not compete with it.

## Validation boundary

- Scripts MUST NOT enforce closed truth-kind lists, exact subdoc names, semantic categories, or brittle text scans.
