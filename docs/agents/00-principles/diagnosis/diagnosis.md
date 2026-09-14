---
doc_type: policy
ssot_owner: docs/agents/00-principles/diagnosis/diagnosis.md
update_trigger: defect terminology, diagnosis sequence, or anti-bias evidence obligations change
---

# Diagnosis and Root-Cause Evidence

This delegated owner applies `AGENTS.md` to bug, error, and regression work. Verification floors resolve through `docs/agents/00-principles/evidence/evidence.md`.

## Defect vocabulary

Use these terms precisely in reports/reviews:
- symptom/manifestation: where the bug is observed
- root cause: earliest defect/condition that makes the symptom inevitable
- workaround: avoids symptom without removing cause
- patch: code change (root-cause or symptom-level)
- regression: new failure introduced by the fix
- blast radius: scope of impacted modules/workflows/users

### Bias-Resistant Debugging (Hard Gate)
Biases to guard against:
- premature closure, confirmation bias, anchoring, novelty/recency bias

Required terminology for defect analysis:
- Use the single SSOT definition in this document's Defect vocabulary section.

Mandatory RCA workflow for bug/error/regression work (execute in order and record evidence):
- Step 0 - Define failure precisely: expected vs actual, inputs/environment/version/commit, and impact.
- Step 1 - Reproduce reliably: reproduce on demand; if intermittent, capture triggering conditions.
- Step 2 - Build MRE: reduce to minimal deterministic repro (fixture + command + expected failure signal).
- Step 3 - Observe facts: collect stack trace/logs/metrics/traces; add targeted assertions/instrumentation as needed.
- Step 4 - Localize first wrong state: identify where invalid state first appears (not only crash site).
- Step 5 - Form falsifiable hypothesis: "If X, then Y; therefore symptom Z."
- Step 6 - Run targeted disconfirming experiment: change one variable at a time and rule out alternatives.
- Step 7 - Declare root cause statement: specific, upstream, and directly actionable.
- Step 8 - Implement root-cause fix upstream: fix at authority/origin, not symptom site; if symptom patch is unavoidable, record infeasibility and residual unprevented error class.
- Step 9 - Lock with tests: add regression test (fails pre-fix/passes post-fix) plus nearby edge-case tests.
- Step 10 - Validate system-wide: run applicable suites/checks and verify runtime signals after rollout/staging.

RCA method stack for complex defects (default order):
- 5 Whys to drill to upstream authority fix point
- Fishbone/Ishikawa to enumerate plausible causes
- Pareto analysis to prioritize likely high-impact causes
- Implement root-cause fix and regression test
- FMEA/DFMEA to prevent recurrence in adjacent paths

Mandatory anti-bias artifacts for every fix:
- minimal reproducible example (MRE)
- regression fixture stored in repo
- disconfirming tests (edge/adversarial cases)
- invariant witness that fails pre-fix and passes post-fix
- root-cause uplift record: symptom location, upstream authority fix point, prevention change made, class of errors prevented, or explicit justification if patching locally
- SSOT consolidation evidence when divergence was a root cause

Confidence rule:
- confidence is evidence-weighted; "it worked once" is not evidence

