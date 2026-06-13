---
doc_type: playbook
ssot_owner: AGENTS.md
update_trigger: change contract fields or verification checklist requirements change
---

# Change Contract Template (Required for behavior changes and bugfixes)

Use as a temporary implementation/review scaffold; `AGENTS.md` and owner docs define required semantics, while Git remains the mechanical change-history source.

```md
# Change Contract

## A) Problem Statement (Observed vs Expected)
- Observed:
- Expected:
- Scope: (rows/files/modules/users impacted)
- Blast radius: (what else could be impacted by the fix/change)

## B) Invariants (Semantic Truth: S)
List invariants affected by this change. Use categories.

### Data invariants
- INV-D1:
- INV-D2:

### Ordering invariants
- INV-O1:

### Atomicity invariants (2PC / all-or-nothing)
- INV-A1:

### Idempotency invariants
- INV-I1:

### Lifecycle invariants (Excel/COM/resources)
- INV-L1:

### Observability invariants (outcome/log completeness)
- INV-OBS1:

## C) Witnesses (Runtime Evidence: R / Recorded Truth: D)
For each invariant above, define a measurable witness.

| Invariant ID | Witness signal (what is measured) | Where recorded (log field/report col) | Pass criteria |
|---|---|---|---|
| INV-L1 | Excel PID baseline before/after | log.excel_pid_before/after | after == before |
| INV-A1 | No writes before validation complete | log.phase sequence | no write events before VALIDATED |

## D) Authority Impact + Fix Placement (SSOT: D)
Identify which authorities are touched and confirm no new competing authority exists.

- Config authority impacted? (Y/N) If Y: where is canonical key defined?
- Parser authority impacted? (Y/N)
- Writer authority impacted? (Y/N)
- Excel lifecycle authority impacted? (Y/N)
- Logger/schema authority impacted? (Y/N)
- Reporting/run-outcome authority impacted? (Y/N)

No-duplication proof (list any removed duplicated logic/files):
- Removed:
- Replaced by:

### Authority-first fix analysis (if debugging)
- Symptom location (where error manifested):
- Authority fix point (where fix was applied):
- Class of errors prevented by fixing at authority:
- If patching at symptom, justify:
- RCA method(s) used (Fishbone/Pareto/5 Whys/FMEA etc.):

## E) Minimal Repro + Regression Fixture
- Minimal repro description:
- Fixture location (path):
- Before fix (expected failure signal):
- After fix (expected pass signal):

## F) Disconfirming Tests (Anti-Premature-Closure)
List tests designed to break your hypothesis.

- Test 1 (edge/adversarial):
- Test 2 (randomized/property):
- Test 3 (real-file replay):

## G) Rollout and Safety
- Feature flag / mode switch? (Y/N) If Y: name:
- Rollback plan:
- Data safety: (atomic writes? backups? temp + rename?)

## H) Verification Checklist (Expected Outcomes)
- [ ] All invariants have witnesses
- [ ] 2PC enforced (no writes before VALIDATED)
- [ ] Every row/file ends with terminal outcome + reason
- [ ] Cleanup baseline restored (Excel/process/temp files)
- [ ] Fixture added + tests pass
- [ ] Bugfixes include deterministic MRE + regression + disconfirming test evidence
- [ ] Failure-path check executed where required by Verification Floors (bugfix and behavior-change work)
- [ ] Root-cause fix is upstream/authority-first, or infeasibility is documented
```
