---
doc_type: reference
ssot_owner: docs/agents/governance/ssot/hand-offs/hand-offs.md
update_trigger: a cross-jurisdiction dependency is added, moved between owners, or retired
---

# Hand-offs

Jurisdiction: cross-jurisdiction dependencies that owner docs express only by noun.

| From jurisdiction | Depends on | Owner path |
| --- | --- | --- |
| every owner declaring a baseline | baseline schema, supersession record, reserved-jurisdiction declaration | `docs/agents/governance/principles/principles.md` |
| excel | COM process containment and cleanup | `docs/agents/interfaces/os-processes/os-processes.md` |
| excel | write safety | `docs/agents/interfaces/filesystem/filesystem.md` |
| pdf | write safety | `docs/agents/interfaces/filesystem/filesystem.md` |
| io-batch | write safety | `docs/agents/interfaces/filesystem/filesystem.md` |
| gui-guidelines | run outcomes shown to the operator | `docs/agents/playbooks/run-outcomes/run-outcomes.md` |
| config | secret boundary | `docs/agents/governance/security/security.md` |
| logging | redaction | `docs/agents/governance/security/security.md` |
| logging | static witness | `scripts/check_governance_core/` |
| run-outcomes | redaction | `docs/agents/governance/security/security.md` |
| settings | MCP payloads | `docs/agents/governance/mcp/mcp.md` |
| settings | machine-local secret boundary | `docs/agents/governance/security/security.md` |
| mcp | shared settings payloads | `docs/agents/governance/settings/settings.md` |
| mcp | secret injection and implicit permission boundary | `docs/agents/governance/security/security.md` |
| hooks | settings payload carrying hook declarations | `docs/agents/governance/settings/settings.md` |
| hooks | executable-code review and secret boundary | `docs/agents/governance/security/security.md` |
| skills | `SKILL.md` header exemption | `docs/agents/governance/documentation/documentation.md` |
| skills | update-together set for bundle identity | `docs/agents/agents_index.md`; `README.md` |
| release | each applicable jurisdiction's witness; closure-record owner `SSOT-DEC-004` | each owner doc; `docs/agents/governance/ssot/authority-decisions/authority-decisions.md` |
| dependencies | secret and permission boundary for install tooling | `docs/agents/governance/security/security.md` |
| governance-learning | redaction and log-root authorization | `docs/agents/governance/security/security.md` |
| governance-learning | skill form | `docs/agents/governance/skills/skills.md` |
| governance-learning | hook form | `docs/agents/governance/hooks/hooks.md` |
| governance-learning | durable fact promotion | `docs/agents/governance/documentation/documentation.md` |
| ssot | coordinated update sets | `docs/agents/governance/ssot/authority-decisions/authority-decisions.md` |
