# Agents Branch Index


- [00-principles/principles_index.md](00-principles/principles_index.md) - First-principles operating guidance. Required when: modeling a task, defining invariants, or planning verification.
- [05-context-retrieval/context-retrieval_index.md](05-context-retrieval/context-retrieval_index.md) - Context retrieval guidance. Required when: choosing what files to read and how to keep discovery precise.
- [10-repo-discovery/repo-discovery_index.md](10-repo-discovery/repo-discovery_index.md) - Repo discovery guidance. Required when: locating SSOT owners before implementation.
- [15-stuck-in-loop-generate-fresh-restart-prompt/stuck-in-loop-generate-fresh-restart-prompt_index.md](15-stuck-in-loop-generate-fresh-restart-prompt/stuck-in-loop-generate-fresh-restart-prompt_index.md) - Restart prompt playbook. Required when: the same failure repeats twice or verification contradicts claims.
- [20-sources-of-truth-map/sources-of-truth-map_index.md](20-sources-of-truth-map/sources-of-truth-map_index.md) - Concept-to-owner routing map. Required when: identifying which authority owns a concept.
- [22-ssot-authority-decisions/ssot-authority-decisions_index.md](22-ssot-authority-decisions/ssot-authority-decisions_index.md) - Cross-project authority decisions (`docs/agents/22-ssot-authority-decisions/ssot-authority-decisions_index.md`). Required when: a mixed-owner or migration decision needs a canonical decision record.
- [25-docs-ssot-policy/docs-ssot-policy_index.md](25-docs-ssot-policy/docs-ssot-policy_index.md) - Docs structure and drift-prevention policy. Required when: changing docs layout, headers, or doc routing rules.
- [30-logging-errors/logging-errors_index.md](30-logging-errors/logging-errors_index.md) - Logging and explicit-failure policy. Required when: changing logging, error handling, or skip/failure reporting.
- [35-coding-principles/coding-principles_index.md](35-coding-principles/coding-principles_index.md) - Delegated coding-principles and runtime-code authority-design policy under the `AGENTS.md` coding hard gates. Required when: planning, implementing, reviewing, refactoring, or purifying implementation code.
- [40-config-constants/config-constants_index.md](40-config-constants/config-constants_index.md) - Config/constants ownership policy. Required when: adding or changing repeated literals, config keys, or defaults.
- [50-excel-com-lifecycle/excel-com-lifecycle_index.md](50-excel-com-lifecycle/excel-com-lifecycle_index.md) - Excel COM lifecycle policy. Required when: Excel COM automation is in scope.
- [60-gui-threading/gui-threading_index.md](60-gui-threading/gui-threading_index.md) - GUI threading policy. Required when: GUI or main-thread updates are involved.
- [70-io-data-integrity/io-data-integrity_index.md](70-io-data-integrity/io-data-integrity_index.md) - I/O integrity policy. Required when: file processing or batch writes are changed.
- [80-testing-real-files/testing-real-files_index.md](80-testing-real-files/testing-real-files_index.md) - Real-file testing guidance. Required when: I/O changes need fixture-backed verification.
- [85-dual-entry-template/dual-entry-template_index.md](85-dual-entry-template/dual-entry-template_index.md) - Dual-entry reference template guidance. Required when: copying or adapting the GUI+CLI template.
- [90-release-checklist/release-checklist_index.md](90-release-checklist/release-checklist_index.md) - Final release/merge checklist. Required when: doing the last verification pass before merge.
- [`link_repo_assets.ps1`](link_repo_assets.ps1) - Repo-owned asset linker. Required when: projecting skills, settings, or MCP assets into runtime locations.
- [mcp/mcp_index.md](mcp/mcp_index.md) - MCP asset branch. Required when: repo-owned MCP config assets change.
- [platforms/platforms_index.md](platforms/platforms_index.md) - Platform runtime notes branch. Required when: runtime support levels, dated platform evidence, or projection rules change.
- [playbooks/playbooks_index.md](playbooks/playbooks_index.md) - Playbook branch. Required when: a task needs a structured scaffold or template.
- [settings/settings_index.md](settings/settings_index.md) - Shared settings branch. Required when: repo-owned settings payloads or settings projections change.
- [skills/skills_index.md](skills/skills_index.md) - Skill branch. Required when: repo-owned reusable skill bundles or platform adapters change.
- [workflow-registry/workflow-registry_index.md](workflow-registry/workflow-registry_index.md) - Workflow indexing standard. Required when: defining how workflows are named, surfaced, and cataloged.
