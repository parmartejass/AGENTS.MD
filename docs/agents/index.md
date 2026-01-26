# Agents Docs Index (Supporting Material)

Canonical policy: `/AGENTS.md`
Context injection manifest: `agents-manifest.yaml`

Core docs:
- Principles: `docs/agents/00-principles.md`
- Context retrieval: `docs/agents/05-context-retrieval.md`
- Repo discovery: `docs/agents/10-repo-discovery.md`
- Stuck-loop restart prompt: `docs/agents/15-stuck-in-loop-generate-fresh-restart-prompt.md`
- Sources of truth map: `docs/agents/20-sources-of-truth-map.md`
- Docs SSOT policy: `docs/agents/25-docs-ssot-policy.md`
- Logging + errors: `docs/agents/30-logging-errors.md`
- Config + constants: `docs/agents/40-config-constants.md`
- Excel COM lifecycle: `docs/agents/50-excel-com-lifecycle.md`
- GUI threading: `docs/agents/60-gui-threading.md`
- I/O + data integrity: `docs/agents/70-io-data-integrity.md`
- Testing with real files: `docs/agents/80-testing-real-files.md`
- Dual-entry template (GUI+CLI): `docs/agents/85-dual-entry-template.md`
- Release checklist: `docs/agents/90-release-checklist.md`
- Workflow registry standard: `docs/agents/workflow-registry.md`

Playbooks (copy/paste templates):
- AI prompt template: `docs/agents/playbooks/ai-coding-prompt-template.md`
- Project docs (minimal): `docs/agents/playbooks/project-docs-template.md`
- Governance learnings (session → governance deltas): `docs/agents/playbooks/governance-learnings-template.md`
- Excel tasks: `docs/agents/playbooks/excel-task-template.md`
- GUI tasks: `docs/agents/playbooks/gui-task-template.md`
- High I/O / batch processing: `docs/agents/playbooks/io-batch-task-template.md`
- Performance hotspots: `docs/agents/playbooks/perf-hotspots-template.md`
- Bugfixes: `docs/agents/playbooks/bugfix-template.md`

Checks:
- Docs SSOT headers: `scripts/check_docs_ssot.ps1`
- Agents manifest references: `scripts/check_agents_manifest.ps1`
- Project docs exist + README linkage: `scripts/check_project_docs.ps1`
- Repo hygiene (no generated artifacts tracked): `scripts/check_repo_hygiene.ps1`
- Python safety baseline (print/except/timeout/file handles): `scripts/check_python_safety.py`
