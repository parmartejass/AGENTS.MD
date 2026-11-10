---
doc_type: policy
ssot_owner: docs/agents/governance/principles/principles.md
update_trigger: the baseline and supersession schema changes
---

# Principles

Jurisdiction: the baseline and supersession record schema.

## Stable baseline interface

```yaml
baseline:            # required in every interfaces owner and playbooks owner doc
  interface: <the stable, universal, direct interface chosen>
  pattern: <the required outcome shape, not an implementation method>
  reason: <why it is the direct interface; what it avoids>
  exception: <the only permitted secondary path and its trigger, or none>
supersession:        # required whenever real work departs from a declared baseline
  baseline: <declared baseline being superseded>
  gap: <verified capability or performance gap>
  evidence: <witness proving the gap>
  preserved_outcomes: <correctness, preservation, explicit outcomes kept>
  proposed_baseline: <update to promote into the owning jurisdiction>
```

- Every interfaces owner and every playbooks owner MUST carry one `baseline` block.
- A governance owner MAY carry one `baseline` block.
- `pattern` records the required outcome shape, not an implementation method.
- A reserved jurisdiction MUST be declared on first use through one `supersession` record naming its proposed baseline.
