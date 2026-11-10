# Governance Layer Index

- [principles/principles_index.md](principles/principles_index.md) - Baseline and supersession schema. Required when: declaring or superseding a baseline.
- [evidence/evidence_index.md](evidence/evidence_index.md) - Invariant and authority-application witnesses, README Checks. Required when: proving a change or a decision.
- [ssot/ssot_index.md](ssot/ssot_index.md) - Concept-to-owner map, jurisdiction hand-offs, and cross-project authority decisions. Required when: identifying which jurisdiction owns a concept or resolving an ownership dispute.
- [coding/coding_index.md](coding/coding_index.md) - Coding foundation with the logging sub-doc. Required when: loading the AGENTS-declared foundations or changing implementation code.
- [documentation/documentation_index.md](documentation/documentation_index.md) - Docs foundation. Required when: loading the AGENTS-declared foundations or changing documentation.
- [testing/testing_index.md](testing/testing_index.md) - Shipped-behavior verification, fixed-defect witnesses, fixture provenance. Required when: verifying any change.
- [security/security_index.md](security/security_index.md) - Secrets, redaction, injection, transport, permissions. Required when: handling secrets, logs with sensitive data, or security-relevant configuration.
- [release/release_index.md](release/release_index.md) - Release evidence, rollback, closure record. Required when: doing the last verification pass or closing non-trivial work.
- [prompt-authoring/prompt-authoring_index.md](prompt-authoring/prompt-authoring_index.md) - Task prompt content and user reply style. Required when: supplying task intent to an AI coding workflow or replying to the user.
- [governance-learning/governance-learning_index.md](governance-learning/governance-learning_index.md) - Candidate promotion and session-log evidence acquisition. Required when: reviewing sessions or logs for governance-level improvements.
- [skills/skills_index.md](skills/skills_index.md) - Skill bundle standard, platform adapters, and repo-owned bundles. Required when: writing, packaging, or changing a reusable skill.
- [settings/settings_index.md](settings/settings_index.md) - Shared settings standard and payloads. Required when: repo-owned platform settings change.
- [mcp/mcp_index.md](mcp/mcp_index.md) - MCP standard and shared payload. Required when: repo-owned MCP configuration changes.
- [dependencies/dependencies_index.md](dependencies/dependencies_index.md) - Hashed lockfile. Required when: adding, upgrading, or installing a dependency.
- [hooks/hooks_index.md](hooks/hooks_index.md) - Deterministic enforcement of gates through platform hooks. Required when: a gate must be enforced rather than instructed.
