---
doc_type: reference
ssot_owner: docs/agents/governance/ssot/hand-offs/hand-offs.md
update_trigger: a cross-jurisdiction dependency is added, moved between owners, or retired
---

# Hand-offs

Jurisdiction: cross-jurisdiction dependencies that owner docs express only by noun.

## Jurisdiction hand-offs

| From jurisdiction | Depends on | Owner path |
| --- | --- | --- |
| all interfaces and playbooks owners, and any governance owner that selects a tool interface | baseline block schema, supersession record, reserved-jurisdiction declaration | `docs/agents/governance/principles/principles.md` |
| principles | performance measurement rules and verification floors | `docs/agents/governance/evidence/evidence.md` |
| principles | defect vocabulary | `docs/agents/governance/bugfix/bugfix.md` |
| principles | process cleanup mechanics for owned handles and PIDs | `docs/agents/interfaces/os-processes/os-processes.md` |
| principles | file cleanup and write-safety mechanics | `docs/agents/interfaces/filesystem/filesystem.md` |
| principles | supersession promotion into the owning baseline | `docs/agents/governance/ssot/ssot.md` |
| principles | reference instance for the stable baseline interface | `docs/agents/interfaces/excel/excel.md` |
| principles | authority-uplift worked example | `docs/agents/governance/coding/coding.md` |
| evidence | real-file verification minimums, fixture and coverage rules | `docs/agents/governance/testing/testing.md` |
| evidence | `VALIDATED` state and two-phase commit tokens in witness rows | `docs/agents/interfaces/filesystem/filesystem.md` |
| evidence | bugfix verification floor and bugfix scaffold fields cited by the change contract | `docs/agents/governance/bugfix/bugfix.md` |
| bugfix | modularity decision in the bugfix scaffold | `docs/agents/governance/coding/coding.md` |
| bugfix | regression fixture rules | `docs/agents/governance/testing/testing.md` |
| testing | verification floors by change type and change-contract scaffold | `docs/agents/governance/evidence/evidence.md` |
| testing | bugfix verification floor for I/O bugfixes | `docs/agents/governance/bugfix/bugfix.md` |
| testing | terminal cleanup outcome for owned external processes | `docs/agents/interfaces/os-processes/os-processes.md` |
| testing | baseline block schema | `docs/agents/governance/principles/principles.md` |
| testing | runner version pin | `docs/agents/governance/dependencies/dependencies.md` |
| discovery | Governance Agent authority routing and detection lists | `agents-manifest.yaml` |
| workflow-registry | composition contract and dependency-direction rules | `docs/agents/governance/coding/coding.md` |
| workflow-registry | silent-failure rules and failure reporting | `docs/agents/governance/coding/logging/logging.md` |
| workflow-registry | outcome contract and run reporting | `docs/agents/playbooks/run-outcomes/run-outcomes.md` |
| workflow-registry | config-driven workflow selection | `docs/agents/playbooks/config/config.md` |
| workflow-registry | concrete workflow registry declaration | `docs/project/architecture/architecture.md` |
| coding | third-party dependency admission and lockfile presence | `docs/agents/governance/dependencies/dependencies.md` |
| excel | COM process ownership, PID capture, OS containment, bounded containment-scoped termination, cleanup in finally | `docs/agents/interfaces/os-processes/os-processes.md` |
| excel | filesystem write safety for saved workbooks | `docs/agents/interfaces/filesystem/filesystem.md` |
| excel | real-file fixture selection for validation witnesses | `docs/agents/governance/testing/testing.md` |
| os-processes | generic resource release in `finally` or a context manager | `docs/agents/governance/principles/principles.md` |
| pdf | filesystem write safety for merged outputs | `docs/agents/interfaces/filesystem/filesystem.md` |
| pdf | aggregation and merge integrity | `docs/agents/playbooks/io-batch/io-batch.md` |
| pdf | backend license class recorded at admission | `docs/agents/governance/dependencies/dependencies.md` |
| io-batch | filesystem write safety and two-phase commit | `docs/agents/interfaces/filesystem/filesystem.md` |
| io-batch | real-file verification minimums | `docs/agents/governance/testing/testing.md` |
| gui-toolkit | feedback vocabulary and outcome states | `docs/agents/playbooks/run-outcomes/run-outcomes.md` |
| gui-guidelines | config live-sync mechanics | `docs/agents/playbooks/config/config.md` |
| gui-guidelines | user-facing summary content and progress-for-long-work obligations | `docs/agents/playbooks/run-outcomes/run-outcomes.md` |
| gui-guidelines | declared styles and token set (styles section handed off 2026-09-20) | `docs/agents/playbooks/design-system/design-system.md` |
| design-system | UI-thread and scheduler mechanics for DPI setup ordering | `docs/agents/interfaces/gui-toolkit/gui-toolkit.md` |
| design-system | feedback vocabulary presented on styled surfaces | `docs/agents/playbooks/gui-guidelines/gui-guidelines.md` |
| config | UI mechanics for config-driven selection surfaces | `docs/agents/interfaces/gui-toolkit/gui-toolkit.md` |
| config | secret boundary and redaction for repo-owned config JSON and its mutation records | `docs/agents/governance/security/security.md` |
| config | write safety and two-phase commit | `docs/agents/interfaces/filesystem/filesystem.md` |
| logging | log schema, reason-code scaffold, and the user-facing feedback channel | `docs/agents/playbooks/run-outcomes/run-outcomes.md` |
| logging | redaction list and payload summarization | `docs/agents/governance/security/security.md` |
| logging | static witness for logging rules | `scripts/check_governance_core/check_governance_core_main.py` |
| run-outcomes | redaction list for reports and summaries | `docs/agents/governance/security/security.md` |
| settings | MCP payload sources | `docs/agents/governance/mcp/mcp.md` |
| settings | secret boundary for machine-local files | `docs/agents/governance/security/security.md` |
| mcp | shared platform settings payloads | `docs/agents/governance/settings/settings.md` |
| mcp | secret injection and implicit permission boundary | `docs/agents/governance/security/security.md` |
| hooks | committed settings payload that carries hook declarations | `docs/agents/governance/settings/settings.md` |
| hooks | executable-code review and secret boundary | `docs/agents/governance/security/security.md` |
| skills | project-doc owner for installation evidence and header carveouts | `docs/agents/governance/documentation/documentation.md` |
| skills | update-together set for bundle identity and platform behavior | `docs/agents/agents_index.md`; `README.md` |
| prompt-authoring | bugfix evidence inputs | `docs/agents/governance/bugfix/bugfix.md` |
| prompt-authoring | release evidence | `docs/agents/governance/release/release.md` |
| release | SSOT, contracts, dependency direction, pruning | `docs/agents/governance/coding/coding.md` |
| release | logging channels and error taxonomy | `docs/agents/governance/coding/logging/logging.md` |
| release | explicit outcomes and work reconciliation | `docs/agents/playbooks/run-outcomes/run-outcomes.md` |
| release | owned process ownership and cleanup | `docs/agents/interfaces/os-processes/os-processes.md` |
| release | Excel COM lifecycle | `docs/agents/interfaces/excel/excel.md` |
| release | write safety and destination validation | `docs/agents/interfaces/filesystem/filesystem.md` |
| release | UI thread and cancellation | `docs/agents/interfaces/gui-toolkit/gui-toolkit.md` |
| release | documentation placement and owner promotion | `docs/agents/governance/documentation/documentation.md` |
| release | bugfix and regression evidence | `docs/agents/governance/bugfix/bugfix.md` |
| release | behavior-change and new-feature evidence | `docs/agents/governance/evidence/evidence.md` |
| release | real-file and fixture evidence | `docs/agents/governance/testing/testing.md` |
| release | secret handling and redaction | `docs/agents/governance/security/security.md` |
| release | closure-record owner and mirror surfaces (`SSOT-DEC-004`) | `docs/agents/governance/ssot/authority-decisions/authority-decisions.md` |
| release | artifact build, version identity, signing, inventory | `docs/agents/playbooks/packaging/packaging.md` |
| release | dependency lockfile state and vulnerability scan | `docs/agents/governance/dependencies/dependencies.md` |
| packaging | locked dependency set and hashes | `docs/agents/governance/dependencies/dependencies.md` |
| packaging | changelog closure record fields | `docs/agents/governance/release/release.md` |
| dependencies | secret boundary and permission boundary for install tooling | `docs/agents/governance/security/security.md` |
| governance-learning | redaction rules and root authorization for session-log evidence | `docs/agents/governance/security/security.md` |
| governance-learning | skill creation standard | `docs/agents/governance/skills/skills.md` |
| governance-learning | docs placement and promotion of durable facts | `docs/agents/governance/documentation/documentation.md` |
| governance-learning | prevention-point owner for write-before-validation example | `docs/agents/interfaces/filesystem/filesystem.md` |
| governance-learning | Change Contract alignment fields | `docs/agents/governance/evidence/evidence.md` |
| governance-learning | authority routes by declared role | `agents-manifest.yaml` |
| governance-learning | hook packaging form | `docs/agents/governance/hooks/hooks.md` |
| project-docs-template | placement, promotion, header, router, and supersession mechanics | `docs/agents/governance/documentation/documentation.md` |
| project-docs-template | changelog closure-record field order | `docs/agents/governance/release/release.md` |
| ssot | coordinated update sets and migration contracts | `docs/agents/governance/ssot/authority-decisions/authority-decisions.md` |
