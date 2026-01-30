---
doc_type: runbook
ssot_owner: AGENTS.md
update_trigger: automation loop flow, config keys, or governance constraints change
---

# Nightly Compound Loop (Simple Two-Step Automation)

## Purpose
A minimal nightly loop that:
1) Reviews the last day of work and captures learnings.
2) Implements the top priority item with the latest learnings applied.

This is a template and runbook. It is not a mandate to auto-edit governance.

## Scope and governance constraints
- Follow `AGENTS.md` (SSOT) and the Context Injection Procedure.
- In repos that use `.governance/` as a submodule, do NOT edit `.governance/` from the parent repo.
  - Governance changes must be proposed only, unless the governance learnings playbook is explicitly invoked
    and council review is completed.
  - See `docs/agents/playbooks/governance-learnings-template.md`.

## Where this runs
- The loop runs inside a target repo (not inside the `.governance/` submodule).
- Copy the template folder from `.governance/templates/automation-loop/` into the target repo.

## Minimal loop (two steps)
### Step A: Review (learning capture)
- Review the last 24 hours of work (threads/logs/notes).
- Update the project learning doc (default: `docs/project/learning.md`).
- Write governance proposals to a report file (do not edit `.governance/`).

### Step B: Implement (top priority)
- Read the priority report and pick the top item.
- Create a feature branch and implement with the latest learnings.
- Verify deterministically (tests or explicit manual checks).

## Template location (SSOT for files and scripts)
- Canonical templates live in: `templates/automation-loop/`
- Copy that folder into your target repo (example: `automation/`).
- Do not run the scripts directly from `.governance/`.

## Configuration (single SSOT)
- The template config is `automation.config.json` (in the copied folder).
- This config is the single SSOT for paths and loop settings.
- Refer to config keys by name; do not duplicate literals in docs.

Required keys (by identifier only):
- `paths.learning_doc`
- `paths.priority_report`
- `paths.governance_proposals`
- `paths.review_report`
- `paths.logs_dir`
- `git.main_branch`, `git.remote`
- `runner.command`, `runner.args`, `runner.prompt_mode`
- `review.prompt_template`, `implement.prompt_template`

Example layout (non-authoritative):
```
repo-root/
  automation/
    automation.config.json
    review.ps1
    implement.ps1
    nightly.ps1
    prompts/
      review.md
      implement.md
  docs/project/learning.md
  reports/
  logs/
```

## Prompt templates
- The prompt templates live under `prompts/` in the copied folder.
- Placeholders are replaced by the scripts at runtime:
  - `{{REPO_ROOT}}`
  - `{{LEARNING_DOC}}`
  - `{{PRIORITY_REPORT}}`
  - `{{GOVERNANCE_PROPOSALS}}`
  - `{{REVIEW_REPORT}}`
  - `{{AUTOMATION_ROOT}}`

## Windows scheduling (Task Scheduler)
Use Task Scheduler to run:
- `review.ps1` at your review time (example: 22:30)
- `implement.ps1` at your implement time (example: 23:00)

Guidelines:
- Enable "Wake the computer to run this task" if you want overnight runs.
- Set the "Start in" directory to your repo root.
- Use the same PowerShell version you use interactively.

## Logs and artifacts
- Logs go to `paths.logs_dir` (config).
- Reports go to `paths.review_report` and `paths.governance_proposals`.
- The project learning doc is updated at `paths.learning_doc`.

## Verification
- If you modify docs under `docs/`, ensure required headers are present.
- If your repo uses this governance pack, you can run:
  - `.governance/scripts/check_docs_ssot.ps1 -RepoRoot .`
  - `.governance/scripts/check_project_docs.ps1 -RepoRoot .`
