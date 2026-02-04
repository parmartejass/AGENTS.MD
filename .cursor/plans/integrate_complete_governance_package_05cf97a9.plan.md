---
name: Integrate complete governance package
overview: Integrate the pasted “Complete AGENTS.md Governance Package” into this canonical governance pack while preserving existing SSOT boundaries (commands in README Checks; hard gates in AGENTS.md; supporting guidance in docs/) and avoiding duplicate/competing authorities.
todos:
  - id: ssot-map
    content: Map pasted package sections to existing SSOT owners; decide which pieces are genuinely missing vs already covered.
    status: pending
  - id: add-new-governance-docs
    content: Create new supporting docs under `docs/agents/` for security/testing/git workflow/planning/anti-patterns (non-duplicative, header-compliant).
    status: pending
  - id: add-top-level-alias-docs
    content: Create `docs/*.md` entrypoint/alias docs (ARCHITECTURE/SECURITY/TESTING/GIT-WORKFLOW/PLANNING/ANTI-PATTERNS) that link to canonical owners.
    status: pending
  - id: platform-adapters
    content: Add `.claude/skills/*` wrappers and `.cursor/rules/project.mdc`; update `docs/agents/skills/10-platform-adapters.md` accordingly.
    status: pending
  - id: context-injection
    content: Update `agents-manifest.yaml` with new profiles to inject the new docs only when relevant (keep default injection minimal).
    status: pending
  - id: guardrails
    content: Harden `scripts/check_docs_ssot.ps1` and `scripts/check_agents_manifest.ps1` (and optionally add an orphan-docs check) to prevent drift and path traversal.
    status: pending
  - id: verify
    content: Run README “Checks” commands and ensure all new/updated files pass the repo’s deterministic checks.
    status: pending
isProject: false
---

# Integrate “Complete Governance Package” into canonical pack

## Goal / acceptance criteria

- Add first-class governance coverage for: architecture/SSOT, security, testing, git workflow, planning, and anti-patterns.
- Preserve existing SSOT rules:
  - Verification commands stay SSOT in `[README.md](README.md)` “Checks” (no pnpm/vitest/etc hardcoding in canonical policy).
  - Hard gates remain in `[AGENTS.md](AGENTS.md)`; new docs are supporting guidance only.
  - No duplicate/competing authorities (new files should be pointer-first and reference existing owners).
- Repo verification passes (existing + any new checks added):
  - `scripts/check_agents_manifest.ps1`
  - `scripts/check_docs_ssot.ps1`
  - `scripts/check_project_docs.ps1`
  - `scripts/check_repo_hygiene.ps1`
  - `scripts/check_python_safety.py`

## What exists already (extend, don’t duplicate)

- **SSOT + hard gates**: `[AGENTS.md](AGENTS.md)`
- **Docs anti-drift + headers**: `[docs/agents/25-docs-ssot-policy.md](docs/agents/25-docs-ssot-policy.md)` + `[scripts/check_docs_ssot.ps1](scripts/check_docs_ssot.ps1)`
- **Planning + verification floors**: `[AGENTS.md](AGENTS.md)` (“Mandatory Execution Loop”, “Verification Floors”) + `[docs/agents/playbooks/ai-coding-prompt-template.md](docs/agents/playbooks/ai-coding-prompt-template.md)`
- **Testing guidance (real files)**: `[docs/agents/80-testing-real-files.md](docs/agents/80-testing-real-files.md)`
- **Release checklist**: `[docs/agents/90-release-checklist.md](docs/agents/90-release-checklist.md)`

## Add the “package docs” (standalone-friendly) as navigation aliases

Create the following **thin, pointer-first** docs (each with required YAML header) that map to canonical owners under `docs/agents/` + `AGENTS.md`:

- `[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)`
- `[docs/SECURITY.md](docs/SECURITY.md)`
- `[docs/TESTING.md](docs/TESTING.md)`
- `[docs/GIT-WORKFLOW.md](docs/GIT-WORKFLOW.md)`
- `[docs/PLANNING.md](docs/PLANNING.md)`
- `[docs/ANTI-PATTERNS.md](docs/ANTI-PATTERNS.md)`

Design constraints for these docs:

- No duplicated command lists (link to README “Checks”).
- No re-stated hard gates; link to `AGENTS.md` section anchors/titles.
- Add only content that is truly new and can’t live better in existing SSOT owners (e.g., qualitative anti-pattern narratives).

## Add missing canonical supporting docs under `docs/agents/`

Add new supporting docs (with YAML headers) to hold the *actual* content behind the aliases:

- **Security guidance**: `[docs/agents/45-security-governance.md](docs/agents/45-security-governance.md)`
  - Pointer-first to `AGENTS.md` Security Baseline.
  - Add non-duplicative “how to apply” patterns (input validation checklist, secrets handling patterns, safe error handling examples).
  - Any quantitative claims must be either cited + reproducible or explicitly labeled `UNVERIFIED`.
- **Testing governance**: `[docs/agents/75-testing-governance.md](docs/agents/75-testing-governance.md)`
  - Pointer-first to `AGENTS.md` Verification Floors + `docs/agents/80-testing-real-files.md`.
  - Add TDD guidance and edge-case testing patterns *without* duplicating repo-specific commands.
- **Git workflow**: `[docs/agents/92-git-workflow.md](docs/agents/92-git-workflow.md)` and/or a playbook `[docs/agents/playbooks/git-workflow-template.md](docs/agents/playbooks/git-workflow-template.md)`
  - Provide AI-safe conventions (atomic commits, PR size guidance, human review checklist).
  - Keep repo-specific submodule editing rules referenced (already in `AGENTS.md` + README).
- **Planning**: `[docs/agents/93-planning.md](docs/agents/93-planning.md)`
  - Map the pasted “SPECIFY/PLAN/TASKS/IMPLEMENT” flow onto the existing Mandatory Execution Loop.
  - Link to the AI prompt template playbook; avoid creating a second planning SSOT.
- **Anti-patterns**: `[docs/agents/94-anti-patterns.md](docs/agents/94-anti-patterns.md)`
  - Capture “vibe coding” and other failure modes as *supporting* guidance, with references back to hard gates (Verify-then-trust, no duplicates, verification floors).

Update navigation so none of these are orphan docs:

- Update `[docs/agents/index.md](docs/agents/index.md)` to include the new docs and the new top-level alias docs.
- Optionally add a short “Package docs” section in `[README.md](README.md)` pointing to the new `docs/*.md` entrypoints.

## Platform adapters: add `.claude/skills` and `.cursor/rules`

- Add Claude Code skill wrappers (no policy duplication; just operational wrappers pointing to SSOT):
  - `[.claude/skills/commit/SKILL.md](.claude/skills/commit/SKILL.md)`
  - `[.claude/skills/review/SKILL.md](.claude/skills/review/SKILL.md)`
  - `[.claude/skills/test/SKILL.md](.claude/skills/test/SKILL.md)`
- Add Cursor rule file:
  - `[.cursor/rules/project.mdc](.cursor/rules/project.mdc)`
  - Keep it minimal and pointer-first (reference `AGENTS.md` + the new docs). Avoid restating hard gates.
- Update platform adapter guidance:
  - Extend `[docs/agents/skills/10-platform-adapters.md](docs/agents/skills/10-platform-adapters.md)` with sections documenting:
    - where `.claude/skills` live and what they may/must not contain
    - how `.cursor/rules/*.mdc` should reference SSOT without duplicating policy

## Context injection: teach agents to load the new docs when relevant

Update `[agents-manifest.yaml](agents-manifest.yaml)`:

- Add new profiles (keep `default_inject` minimal):
  - `security_review` → inject `docs/agents/45-security-governance.md`
  - `testing_task` → inject `docs/agents/75-testing-governance.md`
  - `git_workflow` → inject `docs/agents/92-git-workflow.md` (and/or playbook)
  - `planning` → inject `docs/agents/93-planning.md`
  - Optional stack profile: `typescript_node` (detect `package.json`, `tsconfig.json`, `pnpm-lock.yaml`, `*.ts(x)`), inject a small TS/Node runbook **without** making TS rules global.
- Ensure all manifest paths are **quoted** and exist (enforced by `scripts/check_agents_manifest.ps1`).

## Hardening (recommended guardrails)

To prevent drift and security footguns introduced by the new docs/manifest surface area:

- Tighten `[scripts/check_docs_ssot.ps1](scripts/check_docs_ssot.ps1)` to require YAML front matter at the very top (line 1 `---`) so example code blocks can’t false-pass.
- Harden `[scripts/check_agents_manifest.ps1](scripts/check_agents_manifest.ps1)` to disallow absolute paths and `..` traversal in injected paths (must remain within the governance root).
- (Optional) Add a new check script to fail on orphan docs (docs not referenced from an index), and add it to `README.md` “Checks”.

## Verification

- Run the repo checks from `[README.md](README.md)` “Checks”.
- Spot-check that new docs don’t duplicate commands/policies and that aliases point to canonical owners.
- Confirm `agents-manifest.yaml` passes `scripts/check_agents_manifest.ps1` after adding profiles and paths.

