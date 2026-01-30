# Automation Loop Template (Windows)

This folder is a copyable template for a simple nightly automation loop:
- Review the last day of work and capture learnings.
- Implement the top priority item.

## How to use
1) Copy this folder into your target repo (example: `automation/`).
2) Update `automation.config.json` with your repo-specific paths and your agent runner command.
3) Schedule `review.ps1` and `implement.ps1` using Task Scheduler.

## Notes
- Do not run these scripts from `.governance/`. Copy them into the repo.
- The config file is the SSOT for paths and settings. Avoid duplicating literals elsewhere.
- If your repo uses `.governance/`, do not edit `.governance/` from the parent repo. Write governance proposals to the report file instead.
- Add the log directory to your repo `.gitignore` (default: `logs/`) to keep the worktree clean.

## Files
- `automation.config.json` - SSOT config for paths and runner settings.
- `review.ps1` - nightly learning capture step.
- `implement.ps1` - nightly implementation step.
- `nightly.ps1` - optional wrapper (runs review then implement).
- `automation-lib.ps1` - shared helpers.
- `verify.ps1` - optional harness that runs template checks in a temp repo.
- `prompts/` - prompt templates used by the scripts.

## Verification (optional)

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File verify.ps1
```

Options:
- `-IncludePrCheck` (adds a stub `gh` to verify non-interactive PR creation)
- `-KeepWorkDir` (retain temp repo for inspection)
- `-WorkingRoot <path>` (use a specific working directory; not auto-deleted)

## Risk-accepted runner examples (non-interactive)

Claude Code (no approvals, non-interactive):
```powershell
claude -p --dangerously-skip-permissions --max-turns 20 "Review repo, update learning doc, write review report."
```

Config snippet:
```json
"runner": {
  "command": "claude",
  "args": ["-p", "--dangerously-skip-permissions", "--max-turns", "20"],
  "prompt_mode": "arg"
}
```

Codex CLI (no approvals/sandbox, non-interactive):
```powershell
"Review repo, update learning doc, write review report." | codex exec --dangerously-bypass-approvals-and-sandbox -
```

Config snippet:
```json
"runner": {
  "command": "codex",
  "args": ["exec", "--dangerously-bypass-approvals-and-sandbox", "-"],
  "prompt_mode": "stdin"
}
```
