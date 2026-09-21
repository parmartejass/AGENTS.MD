---
doc_type: policy
ssot_owner: docs/agents/interfaces/pdf/pdf.md
update_trigger: PDF merge, validation, or witness expectations change
---

# PDF

Jurisdiction: PDF generation, overlay, merge, and merge-integrity verification evidence.

## Model
```yaml
baseline:
  interface: direct PDF object and page-tree operations on validated structures
  pattern: "validation-phase input freeze, deterministic ordering, writer determinism pinned before execution (content-derived document ID, declared date source, declared object-stream mode), single merge attempt with recorded witnesses, terminal outcome on failure"
  reason: "the ISO 32000-2 file structure is the universal direct interface; a model library drifts per library and a default writer drifts per run"
  exception: one library backend for a recorded capability gap, selected once as the deterministic SSOT backend before execution
```
- Inputs: ordered source PDFs, plus expected identifiers when the source owner asserts them.
- Transformation: source-owner-declared normalization and duplicate handling, merge through the selected backend contract, then witness validation.
- Transformation MUST record preservation evidence for every change.
- Outputs: merged PDF plus log and run-report entries.
- Side effects: file writes and temp files; temp artifacts MUST be cleaned up.
- Selection owner: Record the workflow coordinator entrypoint or config SSOT path before execution.

## Invariants
- INV-PDF-D1: Every source PDF MUST contribute its full page set to the merged output.
- INV-PDF-D2: The merged output MUST be structurally readable by the chosen reader(s).
- INV-PDF-O1: Merge order MUST be deterministic; nondeterministic directory iteration is prohibited.
- INV-PDF-I1: Re-merging identical inputs MUST NOT drift on page count, identifier coverage, or size ratio within tolerance; drift is a failed integrity witness that no backend selection waives.
- INV-PDF-OBS1: Logs MUST record backend used, page counts, validation outcomes, and retry attempt number.
- INV-PDF-I2: The document `/ID` and document dates MUST derive from declared inputs, never from wall-clock time or randomness, when INV-PDF-I1 is asserted; a fixed `/ID` is permitted in fixtures only.
- INV-PDF-D3: Outlines, named destinations, link annotations, and form fields MUST be counted before and after merge; colliding form-field names across sources MUST Return `FAILED` or be namespaced under a recorded grouping.
- INV-PDF-D4: The merged output MUST declare the maximum PDF version across its sources, and the object-stream mode MUST be recorded by the selection owner before execution.

## Witnesses
Use multiple witnesses; size alone is a heuristic, and optimized formats legitimately shrink.

| Invariant | Witness signal | Where recorded | Pass criteria |
|---|---|---|---|
| INV-PDF-D1 | merged_pages vs sum(source_pages) | log + run report | merged_pages == expected_pages |
| INV-PDF-I1 | witness drift across attempts | log fields per attempt | no drift for same inputs |
| INV-PDF-OBS1 | backend + counts recorded | logs | present for each attempt |
| Identifier assertion from source owner | identifier coverage | logs/report | missing_ids == 0 when that owner requires it |
| Size heuristic from validation owner | size ratio | logs | configured ratio plus required content witnesses |

## Merge decisions
- Duplicate handling MUST come from the upstream SSOT before ordering.
- Merge ordering MUST be deterministic.
- Expected witnesses (expected_pages, expected_sum_bytes, expected_ids, backend, attempt number) MUST be captured before merge, never from the merged output.
- A page-count mismatch MUST Return `FAILED`; passing on size is prohibited.
- Missing or duplicate inputs MUST keep their identity and Return the input owner's `FAILED` or `SKIPPED + reason`; silent coverage reduction is prohibited.
- A missing asserted identifier MUST Return `FAILED`.
- Record terminal failure.
- A proven heuristic defect MUST be corrected at the validation or config owner under authorization, with preserved content requirements and regression evidence.
- A heuristic correction MUST NOT convert the failed run to success.
- Observed backend drift MUST change the selection owner's backend before the next execution.
