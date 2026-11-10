---
doc_type: reference
ssot_owner: docs/agents/governance/ssot/ssot.md
update_trigger: governance responsibilities change, a jurisdiction is added or declared, OR the repo adopts a new SSOT layout
---

# SSOT

Jurisdiction: concept -> owner -> path routing; no concept policy is defined here.

## Relation routing rule

- Cross-jurisdiction dependencies are recorded in hand-offs; owner docs name a dependency only by its jurisdiction noun.
- A concrete project owner resolves through the project architecture record.
- When this map is too abstract for a case, the cross-project decisions register is the next authority.

## Resolve-once routing

Concrete resolvers resolve through the project architecture record. Illustration (non-normative, declares no runtime owner): raw document `2807`, received total `6`, owner-issued projection `2807/6` identical in matrix, review workbook, import, challenge, write, and receipt.

## Data and config

| Concept | Owner | Route |
| --- | --- | --- |
| Config keys, defaults, schemas, reader | config | `docs/agents/playbooks/config/config.md` |
| Workbook, header, portal-field, mapping, source-record, machine-path truth | declared data owner | the declared data owner |
| Project data ownership, provenance, validation (when no more specific owner holds the fact) | project data-truth | `docs/project/data-truth/data-truth.md` |
| Shared data shapes and types | project architecture | `docs/project/architecture/architecture.md` |
| Predicates, requirements, validators | declared rule owner | the declared rule owner |

## Workflows and runtime

| Concept | Owner | Route |
| --- | --- | --- |
| Selected runtime path, backend, execution mode | workflow entrypoint or declared config owner | the declared owner |
| Stage inputs | config | `docs/agents/playbooks/config/config.md` |
| Run outcomes | run-outcomes | `docs/agents/playbooks/run-outcomes/run-outcomes.md` |

## Coding

| Concept | Owner | Route |
| --- | --- | --- |
| Packaged-folder mechanics, Python table, review trigger, one runtime path | coding | `docs/agents/governance/coding/coding.md` |
| Log boundaries, failures, no print, no swallowed failures | logging | `docs/agents/governance/coding/logging/logging.md` |
| Repository structure and Python packaged-folder validation | governance-core | `scripts/check_governance_core/` |
| Module contracts | packaged-folder public entrypoint | the declared entrypoint |
| Project owner graph and authority boundaries | project architecture | `docs/project/architecture/architecture.md` |
| Task-signal routing | manifest | `agents-manifest.yaml` |

## Governance core

| Concept | Owner | Route |
| --- | --- | --- |
| Baseline and supersession schema | principles | `docs/agents/governance/principles/principles.md` |
| Invariant witness, authority-application witness, README Checks | evidence | `docs/agents/governance/evidence/evidence.md` |
| Shipped-behavior verification, fixed-defect witnesses, fixture provenance | testing | `docs/agents/governance/testing/testing.md` |
| Secrets, redaction, injection, transport, permissions | security | `docs/agents/governance/security/security.md` |
| Release evidence, rollback readiness, closure records | release | `docs/agents/governance/release/release.md` |
| Governance-learning candidates and log evidence acquisition | governance-learning | `docs/agents/governance/governance-learning/governance-learning.md` |
| Hashed lockfile | dependencies | `docs/agents/governance/dependencies/dependencies.md` |
| Task prompt content, user reply style | prompt-authoring | `docs/agents/governance/prompt-authoring/prompt-authoring.md` |
| Reusable prompt and instruction policy | declared governance owner | the declared owner |

## Documentation and project memory

| Concept | Owner | Route |
| --- | --- | --- |
| Admission, supersession, concise records, headers, routers, public leaves | documentation | `docs/agents/governance/documentation/documentation.md` |
| Docs router and public-leaf validation | governance-core | `scripts/check_governance_core/` |
| Durable project intent, acceptance, non-goals | project goal | `docs/project/goal/goal.md` |
| Project-specific rules | project rules | `docs/project/rules/rules.md` |
| Verified behavior, rationale, protected behavior | project architecture | `docs/project/architecture/architecture.md` |
| Closure records | project changelog | `docs/project/changelog/changelog.md` |
| Closure-record owner and mirror surfaces | `SSOT-DEC-004` | `docs/agents/governance/ssot/authority-decisions/authority-decisions.md` |
| Reusable operational learnings | project learning | `docs/project/learning/learning.md` |
| Project branch routing | project router | `docs/project/project_index.md` |
| Cross-project authority decisions | decisions register | `docs/agents/governance/ssot/authority-decisions/authority-decisions.md` |

## Repo-owned agent assets

| Concept | Owner | Route |
| --- | --- | --- |
| Skill bundles and platform adapters | skills | `docs/agents/governance/skills/skills.md` |
| Shared non-secret settings payloads | settings | `docs/agents/governance/settings/settings.md` |
| Shared non-secret MCP payloads | mcp | `docs/agents/governance/mcp/mcp.md` |
| Deterministic hard-gate enforcement | hooks | `docs/agents/governance/hooks/hooks.md` |
| Runtime installation | consumer | the consuming environment |

## Interfaces and playbooks

| Concept | Owner | Route |
| --- | --- | --- |
| Excel OOXML-first, COM safety | excel | `docs/agents/interfaces/excel/excel.md` |
| PDF | pdf | `docs/agents/interfaces/pdf/pdf.md` |
| Path, destination, and write safety | filesystem | `docs/agents/interfaces/filesystem/filesystem.md` |
| Subprocess bounds, OS containment, cleanup | os-processes | `docs/agents/interfaces/os-processes/os-processes.md` |
| GUI thread safety | gui-toolkit | `docs/agents/interfaces/gui-toolkit/gui-toolkit.md` |
| Bounded inputs, keyed lookups | io-batch | `docs/agents/playbooks/io-batch/io-batch.md` |
| Presentation and feedback design | gui-guidelines | `docs/agents/playbooks/gui-guidelines/gui-guidelines.md` |
| Reserved: printer, web-api, database (interfaces); naming, packaging (playbooks) | declared on first use through a supersession record | none until declared |
