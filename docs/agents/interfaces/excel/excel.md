---
doc_type: policy
ssot_owner: docs/agents/interfaces/excel/excel.md
update_trigger: Excel interface baseline, workbook data facts, or COM platform facts change
---

# Excel

Jurisdiction: Excel workbook interface selection, workbook data facts, and COM automation constraints.

## Baseline
```yaml
baseline:
  interface: direct OOXML package parts and relationships
  pattern: "package parts mutated surgically; unowned parts preserved; derived parts never left stale"
  reason: stable, engine-independent package format; no drift from Excel and no external-library dependency
  exception: "COM only for what OOXML cannot do (user decision 2026-09-19)"
```

## Workbook
- Derived parts (`calcChain`, shared-string counts) MUST be recomputed, or dropped with their content-type Override and relationship; a stale or dangling one triggers Excel repair.
- A package write stores no computed formula results; cached values stay stale until an engine recalculates.
- Workbook writes MUST preserve every input-declared feature or return unsupported.
- Zeros and formula cells MUST NOT be treated as empty.

## COM
- Each COM call is a cross-process round trip; per-cell automation is the known hotspot.
- A workflow MUST NOT quit an Excel instance it does not own; attaching to a user instance never grants quit authority.
- `Dispatch`, `GetObject`, and `GetActiveObject` can bind to a running user instance; only new-instance activation yields a workflow-owned one.
- A separate instance still shares the user profile, add-ins, and file locks; it is not isolation.
- COM MUST NOT be used for unattended or service-hosted execution.
- An owned instance MUST be closed; references MUST be released before quit; COM initialization MUST be paired with uninitialization.
- Changed application settings MUST be restored on every exit path.
- Every COM call wait MUST be time-bounded.
- An Excel prompt MUST NOT block an owned instance; a prompt MUST terminalize with reason.
