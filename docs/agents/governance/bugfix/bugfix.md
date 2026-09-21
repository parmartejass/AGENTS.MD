---
doc_type: policy
ssot_owner: docs/agents/governance/bugfix/bugfix.md
update_trigger: defect terminology, diagnosis sequence, RCA methods, or anti-bias evidence obligations change
---

# Bugfix

Jurisdiction: defect vocabulary, bias-resistant diagnosis workflow, RCA methods, the bugfix verification floor, and the bugfix scaffold.

## Defect vocabulary

- symptom/manifestation: where the defect is observed.
- root cause: earliest defect or condition making the symptom inevitable.
- workaround: avoids the symptom without removing the cause.
- patch: code change, root-cause or symptom-level.
- regression: new failure introduced by the fix.
- blast radius: scope of impacted modules, workflows, and users.
- Required: use these terms without redefinition in reports and reviews.

## Biases guarded (hard gate)

- Premature closure: Prohibited to close before a disconfirming experiment runs.
- Confirmation bias: Required to seek evidence that breaks the hypothesis.
- Anchoring: Prohibited to fix on the first plausible cause.
- Novelty and recency bias: Prohibited to blame the newest change without evidence.

## Mandatory RCA workflow

- Step 0 - Define failure: expected vs actual, inputs, environment, version, commit, impact.
- Step 1 - Reproduce reliably; capture triggering conditions when intermittent.
- Step 2 - Build MRE: minimal deterministic fixture, command, and expected failure signal.
- Step 3 - Observe facts: stack trace, logs, metrics, traces, targeted instrumentation.
- Step 4 - Localize first wrong state, not only the crash site.
- Step 5 - Form a falsifiable hypothesis: if X then Y, therefore symptom Z.
- Step 6 - Run a disconfirming experiment; change one variable at a time.
- Step 7 - Declare a root-cause statement: specific, upstream, actionable.
- Step 8 - Fix at the authority; a symptom-level patch follows the root-cause uplift gate.
- Step 9 - Lock with a regression test collected by the guard command, failing pre-fix and passing post-fix, plus edge cases.
- Step 10 - Validate system-wide: applicable suites plus runtime signals after rollout.
- Required order: execute Step 0 through Step 10 and record evidence at each step.
- Default method order for complex defects: 5 Whys, Fishbone, Pareto, root-cause fix, FMEA.

## Mandatory anti-bias artifacts

- Root-cause uplift record: symptom location, authority fix point, prevention change, error class prevented.
- SSOT consolidation evidence when divergence was a root cause.
- Explicit justification when patching locally instead of upstream.

## Confidence rule

- Confidence is evidence-weighted.
- Prohibited: treating a single passing run as evidence.

## Verification floor for bugfix

- Deterministic MRE witness.
- Regression test.
- At least one disconfirming edge or adversarial test.
- At least one failure-path check.
- Guard check confirming nothing outside the fix broke.

## RCA methods

### 5 Whys (upstream trace to authority)

- Start from the observed symptom only.
- Ask why the previous answer happened; Prohibited: topic jumps.
- Each answer MUST carry concrete evidence - log, trace, test signal, metric.
- Record why/because/evidence rows until an authority boundary is reached or an evidence gap is recorded; five is neither required nor sufficient, and the chain MUST branch when an answer has more than one sufficient cause.
- Record: authority boundary reached (Y/N), authority owner, broken contract or invariant, authority fix point, class of errors prevented.
- Record the unresolved evidence gap when no authority boundary is reached.

### Fishbone (cause space and elimination)

- Enumerate candidates under people, process, technology, environment, data, policy, measurement.
- Attach evidence to each candidate.
- Reject candidates carrying disconfirming evidence.
- Narrow to highest-confidence candidates and trace each to its authority fix point.
- Record: categories analyzed, candidates, evidence per candidate, rejected causes with signal, selected candidates.

### Pareto (prioritization by impact)

- Measure cause frequency, severity, or cost over a defined window.
- Rank causes by impact and select top contributors against a stated threshold.
- Run authority-first RCA on the selected causes.
- Record: measured causes, metric used, window and data source, selected causes and threshold, rationale.

### FMEA (recurrence prevention)

- List adjacent failure modes around the identified root cause.
- Rate severity, occurrence, and detection and prioritize by the Action Priority table; ranking by a multiplied risk priority number is Prohibited.
- Add prevention controls at authority boundaries.
- Re-evaluate residual risk after controls.
- Record: adjacent failure modes, scoring notes, controls added, residual risk.

## Bugfix scaffold

- Required for every bug, error, or regression task; fill once per task; it records evidence and defines no plan or approval process.

```
- feature_workflow: affected feature or workflow
- symptom_observed: observed behavior
- symptom_expected: expected behavior
- symptom_actual: actual behavior
- root_cause: earliest defect making the symptom inevitable
- workarounds_attempted: what was tried
- environment: environment, version, commit
- repro_inputs: files/folders and minimal steps
- repro_command: deterministic reproduction command + failure signal
- mre_fixture: MRE fixture path(s) + command
- system_boundary: what is in and out of scope
- flow_model: inputs -> transformation -> outputs
- invariants: resource safety, determinism, SSOT rules to preserve
- ssot_duplicated_logic: where duplicated logic exists
- ssot_missing_rule: missing SSOT rule or constant
- authority_symptom_location: where the error manifested
- authority_fix_point: earliest defective owner
- authority_errors_prevented: class of errors prevented at that owner
- authority_unknown_or_conflicting: Y/N; stop and report the authority gap before fixing
- authority_symptom_patch_justification: required when not fixing upstream
- hypothesis: falsifiable statement
- disconfirming_experiment: edge/adversarial experiment run
- root_cause_statement: specific, upstream, actionable
- rca_methods_used: 5 Whys / Fishbone / Pareto / FMEA
- evidence_record: R and D evidence plus where recorded
- fix_placement: authority-first, or symptom patch plus infeasibility
- fix_ssot_owner: owner to change
- fix_call_sites: call sites to rewire
- mre_witness: fail before / pass after
- regression_test: test locking the fix
- disconfirming_test: test designed to break the fix
- failure_path_check: deterministic failure-case run
- guard_command: full or smoke suite
- guard_result: pass/fail
- owner_doc_promotion: target and witness for durable authority-changing outcomes
- shift_left_prevention: required when behavior changed; tests, design, contracts, observability updates
- modularity_decision: per the coding jurisdiction
- security_resource_perf_scan: notes
```
