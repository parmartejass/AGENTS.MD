---
doc_type: runbook
ssot_owner: docs/agents/governance/testing/testing.md
update_trigger: the shipped-behavior verification, fixed-defect witness, or fixture rules, or the test baseline change
---

# Testing

Jurisdiction: verification of shipped behavior through its public entry point on representative real input, fixed-defect witnesses, and tracked-fixture provenance.

```yaml
baseline:
  interface: the repeatable commands in the repository README Checks section
  pattern: "shipped behavior verified through its public entry point on representative real input, with the source input left unchanged"
  reason: "one runner behind README Checks keeps every witness reproducible; it avoids ad hoc scripts and invented commands"
  exception: none
```

- Verification MUST exercise the shipped public entry point, as its users consume it, on representative real input when feasible, without mutating the source input; the verification owns no logic, paths, or expected values.
- A fixed defect MUST keep a reproducible witness that fails without the fix and passes with it.
- Tracked fixtures MUST NOT carry licensed data; a fixture derived from real records MUST record its origin.
