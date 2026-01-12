---
doc_type: runbook
ssot_owner: AGENTS.md
update_trigger: verification expectations change
---

# 80 — Testing With Real Files

Acceptance criteria are often I/O driven; tests must include real representative inputs when possible.

## Minimum expectations per change
1) One happy-path run on a representative real input.
2) One failure-path run covering at least one of:
   - missing file
   - missing required header/sheet
   - permission denied path
3) Confirm:
   - logs contain key stages
   - run outcomes/report exist
   - Excel.exe is not left running (if Excel is involved)

