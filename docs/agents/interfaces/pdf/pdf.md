---
doc_type: policy
ssot_owner: docs/agents/interfaces/pdf/pdf.md
update_trigger: PDF interface baseline or merge-integrity platform facts change
---

# PDF

Jurisdiction: PDF generation, overlay, merge, and merge integrity.

## Baseline
```yaml
baseline:
  interface: direct PDF object and page-tree operations on validated structures
  pattern: "deterministic merge: identical inputs yield identical output; every source page preserved; failure terminal"
  reason: "the ISO 32000-2 file structure is the universal direct interface; a model library drifts per library and a default writer drifts per run"
  exception: one library backend for a recorded capability gap, selected once as the deterministic SSOT backend before execution
```

## Merge
- Every source PDF MUST contribute its full page set to the merged output.
- The merged output MUST be structurally readable.
- The document `/ID` and dates MUST derive from the inputs, never from wall-clock time or randomness.
- Outlines, destinations, links, and form fields MUST survive the merge; colliding field names MUST fail the merge or be namespaced.
- The output MUST declare the highest PDF version among its sources.
- Expected page counts MUST come from the sources; a mismatch MUST fail the merge regardless of size.
- Text extraction can return empty or wrong text for scanned, vector-only, or oddly encoded pages; it MUST NOT be the only content witness.
