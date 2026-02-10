# Agents Docs Index (Supporting Material)

Canonical policy: `AGENTS.md`
Context injection manifest: `agents-manifest.yaml`
Council guidance (authoritative): `AGENTS.md` section "Subagent Council (Hard Gate)"

If any wording conflicts with `AGENTS.md`, `AGENTS.md` wins.

## Read Order by Task Type

### Always
1. `AGENTS.md`
2. `agents-manifest.yaml`
3. `docs/agents/05-context-retrieval.md`
4. `docs/agents/10-repo-discovery.md`

### Bugfix or regression
1. `docs/agents/00-principles.md`
2. `docs/agents/playbooks/bugfix-template.md`
3. `docs/agents/playbooks/rca-methods-template.md`
4. Domain-specific docs (`50/60/70/80` as applicable)

### New feature or behavior change
1. `docs/agents/00-principles.md`
2. `docs/agents/35-authority-bounded-modules.md`
3. `docs/agents/playbooks/design-principles-checklist.md`
4. Relevant task playbook (`excel/gui/io/perf/pdf`)

### Docs or governance updates
1. `docs/agents/25-docs-ssot-policy.md`
2. `docs/agents/playbooks/project-docs-template.md`
3. `docs/agents/playbooks/governance-learnings-template.md` (when explicitly invoked)

## Branches (Top -> Down)

### Core governance branches
- Principles: `docs/agents/00-principles.md`
- Context retrieval: `docs/agents/05-context-retrieval.md`
- Repo discovery: `docs/agents/10-repo-discovery.md`
- Stuck-loop restart prompt: `docs/agents/15-stuck-in-loop-generate-fresh-restart-prompt.md`
- Sources of truth map: `docs/agents/20-sources-of-truth-map.md`
- Docs SSOT policy: `docs/agents/25-docs-ssot-policy.md`
- Logging + errors: `docs/agents/30-logging-errors.md`
- Authority-bounded modules: `docs/agents/35-authority-bounded-modules.md`
- Config + constants: `docs/agents/40-config-constants.md`
- Excel COM lifecycle: `docs/agents/50-excel-com-lifecycle.md`
- GUI threading: `docs/agents/60-gui-threading.md`
- I/O + data integrity: `docs/agents/70-io-data-integrity.md`
- Testing with real files: `docs/agents/80-testing-real-files.md`
- Dual-entry template (GUI+CLI): `docs/agents/85-dual-entry-template.md`
- Release checklist: `docs/agents/90-release-checklist.md`
- Workflow registry standard: `docs/agents/workflow-registry.md`

### Playbooks (copy/paste task templates)
- AI prompt template: `docs/agents/playbooks/ai-coding-prompt-template.md`
- Project docs (minimal): `docs/agents/playbooks/project-docs-template.md`
- Governance learnings: `docs/agents/playbooks/governance-learnings-template.md`
- RCA methods: `docs/agents/playbooks/rca-methods-template.md`
- Design principles checklist: `docs/agents/playbooks/design-principles-checklist.md`
- Excel tasks: `docs/agents/playbooks/excel-task-template.md`
- Excel library selection: `docs/agents/playbooks/excel-library-selection-playbook.md`
- GUI tasks: `docs/agents/playbooks/gui-task-template.md`
- High I/O / batch processing: `docs/agents/playbooks/io-batch-task-template.md`
- PDF tasks: `docs/agents/playbooks/pdf-task-template.md`
- Performance hotspots: `docs/agents/playbooks/perf-hotspots-template.md`
- Bugfixes: `docs/agents/playbooks/bugfix-template.md`

### Skills
- Skill standards: `docs/agents/skills/00-skill-standards.md`
- Platform adapters: `docs/agents/skills/10-platform-adapters.md`

### Automation
- Overview: `docs/agents/automation/overview.md`
- Nightly compound loop: `docs/agents/automation/nightly-compound-loop.md`
- Templates: `templates/automation-loop/`

### Schemas
- Change record artifact schema: `docs/agents/schemas/change-record.schema.json`

## Checks

- Docs SSOT headers: `scripts/check_docs_ssot.ps1`
- Agents manifest references: `scripts/check_agents_manifest.ps1`
- Project docs exist + README linkage: `scripts/check_project_docs.ps1`
- Repo hygiene (no generated artifacts tracked): `scripts/check_repo_hygiene.ps1`
- Cross-platform core governance checks: `scripts/check_governance_core.py`
- Change record artifacts: `scripts/check_change_records.ps1`
- Python safety baseline (print/except/timeout/file handles): `scripts/check_python_safety.py`

When this pack is vendored under `.governance/`, invoke checks via `.governance/scripts/...` and pass `-RepoRoot .` for repo-scoped checks.
