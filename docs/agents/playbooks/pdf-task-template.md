---
doc_type: playbook
ssot_owner: AGENTS.md
update_trigger: PDF workflow/integrity guidance changes OR new recurring PDF merge failure modes emerge
---

# Playbook — PDF Tasks (Merge, Integrity, Verification)

Use when:
- Working on PDF generation/overlay/merge workflows
- Investigating missing/duplicate pages, “merge drift”, or integrity validation failures
- Introducing or tuning PDF validation (size checks, page checks, identifier checks)

Non-goals:
- This is not a library specification. Library notes are examples; verify in your environment.
- Do not duplicate constants/defaults here; reference SSOT owners (config/constants/workflows).

## Model (first principles)
- Inputs: ordered list of source PDFs (and optionally expected identifiers like tracking/order IDs)
- Transformation: optional normalize/dedupe → merge using a backend → validate witnesses
- Outputs: merged PDF + logs/report entries
- Side effects: file writes, temp files, optional cleanup

## Invariants (Semantic Truth: S)

### Data invariants
- INV-PDF-D1: Every source PDF contributes its full page set to the merged output.
- INV-PDF-D2: The merged output is structurally readable by the chosen PDF reader(s).

### Ordering invariants
- INV-PDF-O1: Merge order is deterministic (stable ordering rule; no nondeterministic directory iteration).

### Idempotency invariants
- INV-PDF-I1: Re-merging identical inputs must not drift on core witnesses (page count, identifier coverage, size ratio within tolerance).
  - If drift occurs, treat it as corruption (switch backend or fail fast; do not blindly retry same strategy).

### Observability invariants
- INV-PDF-OBS1: Logs record: backend used, page counts, validation outcomes, and any retry attempt number.

## Witnesses (Runtime Evidence: R / Recorded Truth: D)

Use multiple witnesses; size alone is a heuristic.

| Invariant | Witness signal | Where recorded | Pass criteria |
|---|---|---|---|
| INV-PDF-D1 | merged_pages vs sum(source_pages) | log + run report | merged_pages == expected_pages |
| INV-PDF-I1 | witness drift across attempts | log fields per attempt | no drift for same inputs |
| INV-PDF-OBS1 | backend + counts recorded | logs | present for each attempt |
| (optional) | identifier coverage | logs/report | missing_ids == 0 (if identifiers are asserted) |
| (optional) | size ratio | logs | output_size >= expected_sum * ratio |

## Procedure (decision tree)

1) Freeze inputs (validation phase, side-effect free)
- Decide duplicate handling from upstream SSOT:
  - If inputs must be unique: deduplicate by real path and record duplicates explicitly (FAILED or SKIPPED with reason).
  - If duplicates are meaningful: preserve duplicates and include them in deterministic ordering.
- Drop missing files explicitly (log SKIPPED/FAILED with reason).
- Establish deterministic ordering.
- Capture expected witnesses:
  - expected_pages = sum(page_count(source_i))
  - expected_sum_bytes = sum(size_bytes(source_i))
  - expected_ids (if available) from upstream SSOT (not from merged output)

2) Choose witnesses (minimum set)
- Required: page count, backend, output size, attempt number
- Optional: expected IDs coverage (only if IDs are reliably extractable/defined upstream)

3) Merge attempt
- Use the default (most deterministic) backend.
- Emit attempt-level logs with witness values.

4) Validate
- If page count mismatches: FAIL (do not “pass” on size).
- If IDs are asserted and missing: FAIL (but be aware of text extraction limits; see notes).
- If size check is used:
  - Use a tolerance ratio (configurable per repo).
  - Interpret small deficits as “possible optimization” only if other witnesses pass.

5) If validation fails
- If witnesses drift across repeated attempts with identical inputs: treat as corruption
  - Switch backend OR restart process OR fail fast (pick one per repo policy).
- If failure is stable and explainable (e.g., optimization delta): adjust tolerance (project-level config), not the invariant.

## Notes (common pitfalls)

- PDF text extraction is imperfect. “Missing IDs” can be false negatives if the PDF contains images or non-extractable text.
  - If IDs are a hard requirement, define them upstream and validate via a robust method (or acknowledge extraction limits).
- Size validation is a heuristic. Optimized formats can legitimately shrink due to deduplication/structure optimization.

## Library notes (examples; verify in your environment)

- PyPDF2 vs PyMuPDF:
  - Some workflows observe drift across repeated merges in the same process with certain libraries.
  - If you observe drift (same inputs → different outputs), prefer a more deterministic backend and keep the other as fallback.
  - Always rely on witnesses (page count / ID coverage / size ratio) to confirm.

## Deterministic verification checklist

- [ ] Happy path: representative multi-file merge; verify page count and (if asserted) IDs.
- [ ] Failure path: remove one input or include an unreadable PDF; ensure explicit FAILED with reason.
- [ ] Retry path (if implemented): confirm witnesses do not drift across attempts for identical inputs.
