---
doc_type: runbook
ssot_owner: AGENTS.md
update_trigger: discovery signals or SSOT adoption rules change
---

# 10 — Repo Discovery (Mandatory Before Writing)

Goal: find existing SSOT owners and adopt them instead of creating parallel modules/docs.

## What to search for

### Constants / config
- `constants`, `config`, `settings`, `defaults`, `env`
- `CFG_`, `CONST_`, `SHEET_`, `HDR_`, `STATUS_`

### Logging / errors
- `logging.getLogger(__name__)`
- `errors`, `exceptions`, `ErrorCode`, `ValidationError`

### Excel automation
Use `agents-manifest.yaml` profile `excel_automation` detection lists (keep them SSOT in the manifest; do not duplicate here):
- `profiles.excel_automation.detect.keywords`
- `profiles.excel_automation.detect.code_patterns`
- `profiles.excel_automation.detect.file_globs`

### GUI
Use `agents-manifest.yaml` profile `gui_task` detection lists (keep them SSOT in the manifest; do not duplicate here):
- `profiles.gui_task.detect.keywords`
- `profiles.gui_task.detect.code_patterns`

### Workflows
- `workflow`, `pipeline`, `runner`, `dispatcher`, `run_`, `main()`

## Decision rules
- If an SSOT owner exists for a responsibility: extend it.
- If it does not exist: create one minimally and wire all call sites through it.
