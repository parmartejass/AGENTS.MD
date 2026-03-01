---
doc_type: runbook
ssot_owner: AGENTS.md
update_trigger: verification expectations change
---

# 80 - Testing With Real Files

Acceptance criteria are often I/O driven. When changes affect I/O or file processing, tests must include representative real inputs when feasible.
If real inputs are not feasible, document why and use a deterministic surrogate fixture plus an explicit failure-path witness in the final response or run report.

This runbook adds I/O-specific expectations on top of the baseline verification floors.
For I/O bugfix/regression changes, include bias-resistant debugging evidence (MRE + regression + disconfirming + failure-path).

## Minimum expectations when changes affect I/O or file processing
1) One happy-path run on a representative real input.
2) One failure-path run covering at least one I/O failure mode (examples):
   - missing file
   - missing required header/sheet
   - permission denied path
   This failure-path run satisfies the failure-path check requirement for I/O changes.
3) Confirm (per repo logging/reporting conventions; do not invent new locations):
   - logs contain key stages
   - run outcomes/report exist
   - Excel.exe is not left running (if Excel is involved)
4) Use copies of real inputs; do not mutate source files. Record fixture paths and clean up outputs.
5) If performance is an acceptance criterion, capture timing on a representative input and record where it is stored.

