---
doc_type: reference
ssot_owner: docs/agents/governance/ssot/ssot.md
update_trigger: governance responsibilities change, a jurisdiction is added or declared, OR the repo adopts a new SSOT layout
---

# SSOT

Jurisdiction: concept -> owner -> path routing, file/folder SSOT co-location mechanics, and the jurisdiction hand-off table; no concept policy is defined here.

## File/folder structure rule

- Every cross-jurisdiction dependency is recorded here; owner docs name a dependency only by its jurisdiction noun.
- A concrete project owner resolves through the project architecture record and its declared public contract.
- When this map is too abstract for a case, the cross-project decisions register is the next authority.
- Related artifacts within one authority boundary MUST share the existing SSOT parent.
- Scattered same-authority artifacts MUST be consolidated under that parent in the authorized change; affected consumers MUST be migrated and required behavior preserved.

## Resolve-once structural routing

`AGENTS.md` section `Resolve once before fan-out` is the sole rule owner; this table routes its structural applications and defines no second rule.

| Application under the constitutional rule | Existing owner and route |
| --- | --- |
| Documentation defines the business meaning once and routes to its owner. | documentation -> `docs/agents/governance/documentation/documentation.md` |
| Configuration maps a semantic role to the owner; it does not duplicate formatting grammar. | config -> `docs/agents/playbooks/config/config.md` |
| The domain package owns the resolver and canonical projection. | concrete project owner through project architecture; implementation boundary -> `docs/agents/governance/coding/coding.md` |
| Stable callers provide raw evidence and context only. | coding -> `docs/agents/governance/coding/coding.md` |
| Review, import, challenge, commit, receipt, and recovery all consume the same projection. | declared workflow owner; composition mechanics -> `docs/agents/governance/coding/coding.md` |
| Validation independently replays the same public owner and requires exact equality. | declared rule owner; witnesses -> `docs/agents/governance/evidence/evidence.md` and `docs/agents/governance/testing/testing.md` |
| Tests assert cross-surface parity, not just isolated component correctness. | testing -> `docs/agents/governance/testing/testing.md`; witness contract -> `docs/agents/governance/evidence/evidence.md` |
| Raw evidence is preserved for audit but never becomes a second SSOT. | declared data/evidence owner; witness and permitted storage -> `docs/agents/governance/evidence/evidence.md` and `docs/agents/governance/security/security.md` |

### Bilty illustration

Illustrative only; this declares no project runtime owner or verified implementation fact:

```text
raw document = 2807
received package total = 6
PackageCountV2 canonical projection = 2807/6
```

Under the constitutional rule, the illustration requires the owner-issued `2807/6` to be identical in the matrix, Review XLSX, import XLSX, append challenge, workbook write, and receipt.

## Constants

| Concept | Owner | Route |
| --- | --- | --- |
| Sheet names, headers, statuses | declared constants authority | `docs/agents/playbooks/config/config.md` |
| Folder names, prefixes, patterns | declared constants authority | `docs/agents/playbooks/config/config.md` |
| Column identifiers and keys | declared constants authority | `docs/agents/playbooks/config/config.md` |

## Data-facing truth

| Concept | Owner | Route |
| --- | --- | --- |
| Workbook/sheet/header truth, portal fields, user-facing mappings, source records, machine paths | input artifact, external system, declared config/constants owner, or data authority | the declared data owner |
| Permitted fact owners and data-truth categories | documentation | `docs/agents/governance/documentation/documentation.md` sections "Concise owner records", "Admission" |
| Project ownership, provenance, validation records within branch scope | project data-truth | `docs/project/data-truth/data-truth.md` |

- A project data-truth record is used only when no more specific declared data owner holds the fact.

## Config

| Concept | Owner | Route |
| --- | --- | --- |
| Keys, defaults, schema | config | `docs/agents/playbooks/config/config.md` |
| Loader, normalization, deterministic repair, repair outcomes | config | `docs/agents/playbooks/config/config.md` |
| Defaultable vs required-without-default classification | config | `docs/agents/playbooks/config/config.md` |
| Config-driven selection surfaces and live-sync | config | `docs/agents/playbooks/config/config.md` |

## Schema and types

| Concept | Owner | Route |
| --- | --- | --- |
| Shared data shape and type definitions | exactly one place | `docs/project/architecture/architecture.md` |
| Permitted owner forms, doc-owned authority conditions | documentation | `docs/agents/governance/documentation/documentation.md` section "Concise owner records" |
| Config-owned schemas | config | `docs/agents/playbooks/config/config.md` |
| Schema provenance and validation expectations | declared data owner | `docs/project/data-truth/data-truth.md` |
| Validation rules for a schema | rules jurisdiction | the declared rule owner |

- A project routing record does not replace an existing schema artifact owner.

## Rules and validations

| Concept | Owner | Route |
| --- | --- | --- |
| `is_*` predicates, `require_*` requirements, `validate_*` validators | exactly one place | the declared rule owner |
| Consumer boundaries for rules | coding | `docs/agents/governance/coding/coding.md` |

## Workflows

| Concept | Owner | Route |
| --- | --- | --- |
| Runtime composition, child authority boundaries | one module or cohesive package | `docs/agents/governance/coding/coding.md` |
| Workflow index, IDs, entrypoints, coverage witness | declared registry | `docs/agents/governance/coding/workflow-registry/workflow-registry.md` |
| Selected-stage inputs | config | `docs/agents/playbooks/config/config.md` |
| Run and stage outcomes | run-outcomes | `docs/agents/playbooks/run-outcomes/run-outcomes.md` |

## Runtime path and backend selection

| Concept | Owner | Route |
| --- | --- | --- |
| Selected runtime path, backend, library, execution mode | workflow entrypoint, unless a dedicated config SSOT is declared | the declared entrypoint or config owner |
| Backend-selection rules | their rule or config authority | `docs/agents/playbooks/config/config.md` |
| Selection record made before execution and referenced by owner path | workflow entrypoint | the declared entrypoint |
| Failure and cleanup behavior | coding, No Fallback or Legacy Runtime Paths | `docs/agents/governance/coding/coding.md` |

## Coding principles and module boundaries

| Concept | Owner | Route |
| --- | --- | --- |
| Coding hard-gate trigger and precedence | constitution | `AGENTS.md` |
| Coding-principles and runtime-code authority-design mechanics | coding | `docs/agents/governance/coding/coding.md` |
| Logging channels, error taxonomy, catching policy, silent failures, static witness | logging | `docs/agents/governance/coding/logging/logging.md` |
| Repository structure and Python entrypoint enforcement | governance-core public contract | `scripts/check_governance_core/check_governance_core_main.py` |
| Authority boundaries recorded per project | project architecture | `docs/project/architecture/architecture.md` |
| Module contracts | authority module entrypoint | the declared entrypoint |

## Governance core

| Concept | Owner | Route |
| --- | --- | --- |
| First-principles gate, authority uplift, control artifacts, baseline and supersession schema | principles | `docs/agents/governance/principles/principles.md` |
| Truth layers, invariant witnesses, verification floors, rewrite risk, performance measurement, change contract | evidence | `docs/agents/governance/evidence/evidence.md` |
| Defect vocabulary, RCA workflow and methods, bugfix verification floor, bugfix scaffold | bugfix | `docs/agents/governance/bugfix/bugfix.md` |
| Real-file verification minimums, fixture and coverage rules, guard checks, test-runner baseline | testing | `docs/agents/governance/testing/testing.md` |
| Secrets, redaction list, injection and transport, asset permission boundaries | security | `docs/agents/governance/security/security.md` |
| Release evidence, rollback readiness, Changelog field template and order | release | `docs/agents/governance/release/release.md` |
| Session-evidenced governance-learning candidates, promotion gate, log evidence acquisition | governance-learning | `docs/agents/governance/governance-learning/governance-learning.md` |
| Dependency admission, lockfile and hashes, frozen install, cooldown upgrade, vulnerability scan | dependencies | `docs/agents/governance/dependencies/dependencies.md` |

## Jurisdictional decomposition and purification

| Concept | Owner | Route |
| --- | --- | --- |
| Prompt decomposition into SSOT/SRP jurisdictions, entry-not-ceiling scope, no literal or hardcoded building (highest operating rule) | constitution | `AGENTS.md` Jurisdictional Decomposition |
| Implementation-code jurisdiction, drift ledgers, fix points, deletion and reroute plans, post-diff purification | coding | `docs/agents/governance/coding/coding.md` |
| Docs placement and non-owner doc boundaries | documentation | `docs/agents/governance/documentation/documentation.md` |
| Task-signal routing for jurisdiction work | manifest | `agents-manifest.yaml` |
| Project-local owner graph records | project architecture | `docs/project/architecture/architecture.md` |

## Docs modularity

| Concept | Owner | Route |
| --- | --- | --- |
| Docs-modularity hard gate | constitution | `AGENTS.md` |
| Docs-family mechanics | documentation | `docs/agents/governance/documentation/documentation.md` |
| Project-doc scaffold shape | documentation template | `docs/agents/governance/documentation/project-docs-template/project-docs-template.md` |
| Docs router and public leaf validation facts | governance-core public contract | `scripts/check_governance_core/check_governance_core_main.py` |

## Bounded project authority memory

| Concept | Owner | Route |
| --- | --- | --- |
| Material-knowledge admission, maintenance, safe supersession, concise records, baseline placement | documentation | `docs/agents/governance/documentation/documentation.md` |
| Durable project intent, objective, acceptance criteria, non-goals, verification intent | project goal | `docs/project/goal/goal.md` |
| Project-specific protected boundaries | project rules | `docs/project/rules/rules.md` |
| Authority pointers, verified behavior, rationale, tradeoffs, protected invariants | project architecture | `docs/project/architecture/architecture.md` |
| Data-truth ownership, provenance, validation, source routing | project data-truth | `docs/project/data-truth/data-truth.md` |
| Tracked closure records for completed non-trivial work | project changelog | `docs/project/changelog/changelog.md` |
| Reusable operational learnings only; change-specific what/how/why and supersession truth stay at the highest owner doc | project learning | `docs/project/learning/learning.md` |
| Branch routing entrypoint | project router | `docs/project/project_index.md` |

## Cross-project authority decisions

| Concept | Owner | Route |
| --- | --- | --- |
| Governance-level authority choices across repos using this pack | decisions register | `docs/agents/governance/ssot/authority-decisions/authority-decisions.md` |
| Project-local adoption details | project architecture | `docs/project/architecture/architecture.md` |

## Repo-owned agent assets

| Concept | Owner | Route |
| --- | --- | --- |
| Reusable skill bundles and platform adapters | skills | `docs/agents/governance/skills/skills.md` |
| Shared non-secret settings payloads | settings | `docs/agents/governance/settings/settings.md` |
| Shared non-secret MCP payloads | mcp | `docs/agents/governance/mcp/mcp.md` |
| Deterministic hard-gate enforcement through runtime hooks | hooks | `docs/agents/governance/hooks/hooks.md` |
| Runtime installation; tracked root runtime copies and projection mappings are retired | consumer | the consuming environment |

## Runtime config and secret boundary

| Concept | Owner | Route |
| --- | --- | --- |
| Non-secret repo-owned settings examples and parseability by owning format | settings | `docs/agents/governance/settings/settings.md` |
| Secrets never hardcoded; OS user-scoped credential store, CI managed injection as the only exception; machine-local secret files untracked | security | `docs/agents/governance/security/security.md` |
| Redaction list for logs, reports, evidence, handoffs | security | `docs/agents/governance/security/security.md` |
| Injection avoidance and TLS or security-weakening risk acceptance | security | `docs/agents/governance/security/security.md` |

## Interfaces

| Concept | Owner | Route |
| --- | --- | --- |
| Excel backend selection, OOXML-first rule, Excel-specific COM lifecycle, Excel data rules | exactly one implementation (excel jurisdiction) | `docs/agents/interfaces/excel/excel.md` |
| PDF invariants, witnesses, procedure | pdf | `docs/agents/interfaces/pdf/pdf.md` |
| Path and destination validation, write state machine, two-phase commit | filesystem | `docs/agents/interfaces/filesystem/filesystem.md` |
| Subprocess bounds, OS containment at creation, PID plus start time identity, bounded containment-scoped termination, cleanup in finally, terminal cleanup outcome | os-processes | `docs/agents/interfaces/os-processes/os-processes.md` |
| Worker posts to queue; UI drains via `after(...)`; shutdown and cancel event enforcement | exactly one implementation (gui-toolkit jurisdiction) | `docs/agents/interfaces/gui-toolkit/gui-toolkit.md` |

## Playbooks

| Concept | Owner | Route |
| --- | --- | --- |
| Transformation authorization, bounded processing, aggregation and merge integrity | io-batch | `docs/agents/playbooks/io-batch/io-batch.md` |
| Presentation and feedback design, UI requirements scaffold | gui-guidelines | `docs/agents/playbooks/gui-guidelines/gui-guidelines.md` |
| Design tokens, scales, interaction states, keyboard and focus model, accessibility floor | design-system | `docs/agents/playbooks/design-system/design-system.md` |
| Artifact build, version identity, signing, provenance, inventory, downgrade | packaging | `docs/agents/playbooks/packaging/packaging.md` |
| Reserved: printer, web-api, database (interfaces); naming (playbooks) | declared on first use through a supersession record | none until declared |

## Agent instructions and prompt configuration

| Concept | Owner | Route |
| --- | --- | --- |
| Prompt scaffolds | prompt-authoring | `docs/agents/governance/prompt-authoring/prompt-authoring.md` |
| Reusable prompt and instruction policy | its declared governance owner | the declared owner |
| Skill and settings source formats and placement | asset roots | see Repo-owned agent assets |
| Durable prompt-originated project intent, after classification under the constitution | project goal | `docs/project/goal/goal.md` |
| Other durable project facts; temporary prompt context stays non-authoritative until promoted | documentation | `docs/agents/governance/documentation/documentation.md` |

## Run outcomes and reporting

| Concept | Owner | Route |
| --- | --- | --- |
| Per-item outcome `EXECUTED`, `SKIPPED`, `FAILED` plus reason | run-outcomes | `docs/agents/playbooks/run-outcomes/run-outcomes.md` |
| Output location policy | run-outcomes | `docs/agents/playbooks/run-outcomes/run-outcomes.md` |
| Known-work reconciliation: `planned`, `eligible`, `executed`, `skipped`, `failed` | run-outcomes | `docs/agents/playbooks/run-outcomes/run-outcomes.md` |
| Changelog closure-record owner and valid mirror surfaces | `SSOT-DEC-004` | `docs/agents/governance/ssot/authority-decisions/authority-decisions.md` |
| Changelog field template and order | release | `docs/agents/governance/release/release.md` |
