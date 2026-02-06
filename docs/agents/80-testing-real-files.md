---
doc_type: runbook
ssot_owner: AGENTS.md
update_trigger: verification expectations change
---

# 80 — Testing With Real Files

Acceptance criteria are often I/O driven; when changes affect I/O or file processing, tests must include real representative inputs (see fixture hygiene in `AGENTS.md`) when possible. If not feasible, record why in the final response or run report per repo conventions.
Baseline verification floors live in `AGENTS.md` ("Verification Floors (Hard Gate)"); this runbook adds I/O-specific expectations.
Follow `AGENTS.md` for verification command ownership and manual-check recording.
For I/O bugfix/regression changes, also satisfy `AGENTS.md` "Bias-Resistant Debugging (Hard Gate)" evidence (MRE + regression + disconfirming + failure-path).

## Minimum expectations when changes affect I/O or file processing
1) One happy-path run on a representative real input.
2) One failure-path run covering at least one I/O failure mode (examples):
   - missing file
   - missing required header/sheet
   - permission denied path
   This failure-path run satisfies the "failure-path check" requirement in `AGENTS.md` for I/O changes.
3) Confirm (per repo logging/reporting conventions; do not invent new locations):
   - logs contain key stages
   - run outcomes/report exist
   - Excel.exe is not left running (if Excel is involved)
4) Use copies of real inputs; do not mutate source files. Record fixture paths and clean up outputs.
5) If performance is an acceptance criterion, capture timing on a representative input and record where it is stored.

