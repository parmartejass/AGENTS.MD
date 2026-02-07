---
doc_type: playbook
ssot_owner: AGENTS.md
update_trigger: RCA method expectations, defect vocabulary, or verification floors change
---

# Playbook - RCA Methods Template

Use when:
- A task is bug/error/regression diagnosis or fix.
- You need deterministic evidence for authority-first root-cause fixes.

Reference authority:
- `AGENTS.md` "Bias-Resistant Debugging (Hard Gate)"
- `AGENTS.md` "First-Principles Protocol (Hard Gate)"
- `AGENTS.md` "Verification Floors (Hard Gate)"

This template is a prompting scaffold. If any wording conflicts with policy, `AGENTS.md` wins.

## Shared Input Block (fill once)
- feature/workflow:
- symptom/manifestation:
- expected behavior:
- actual behavior:
- impact + blast radius:
- deterministic reproduction command:
- MRE fixture path(s):
- environment/version/commit:

## Method 1 - 5 Whys (upstream trace to authority)

### Steps
1. Start from the observed symptom only.
2. For each why, ask why the previous answer happened (no topic jumps).
3. Every answer must include concrete evidence (log, trace, test signal, metric).
4. Continue beyond five if authority is not reached.
5. Stop only when the answer lands on the authority boundary (contract/invariant/owner).

### Record
1. Why did [symptom] happen?
   - because:
   - evidence:
2. Why did [answer #1] happen?
   - because:
   - evidence:
3. Why did [answer #2] happen?
   - because:
   - evidence:
4. Why did [answer #3] happen?
   - because:
   - evidence:
5. Why did [answer #4] happen?
   - because:
   - evidence:

### Stop Condition and Output
- authority boundary reached? (Y/N)
- authority owner:
- broken contract/invariant:
- authority fix point:
- class of errors prevented by fixing at authority:

## Method 2 - Fishbone (cause space + elimination)

### Steps
1. Enumerate candidates under categories: people/process/technology/environment/data/policy.
2. Attach evidence for each candidate.
3. Reject candidates with disconfirming evidence.
4. Narrow to highest-confidence candidate causes.
5. Trace selected candidate to authority fix point.

### Record
- categories analyzed:
- candidate causes:
- evidence per candidate (R/D):
- rejected causes + disconfirming signal:
- selected candidate(s) for authority trace:

## Method 3 - Pareto (prioritization by impact)

### Steps
1. Measure cause frequencies/severity/cost on a defined window.
2. Rank causes by impact.
3. Select top contributors (for example, threshold-based top causes).
4. Run authority-first RCA on selected causes.

### Record
- measured causes:
- metric used (frequency/severity/cost):
- analysis window and data source:
- top causes selected + threshold:
- rationale for selected root-cause path:

## Method 4 - FMEA/DFMEA (recurrence prevention)

### Steps
1. List adjacent failure modes around the identified root cause.
2. Score severity/occurrence/detection and prioritize.
3. Add prevention controls at authority boundaries.
4. Re-evaluate residual risk after controls.

### Record
- adjacent failure modes:
- severity/occurrence/detection notes:
- prevention controls added:
- residual risk:

## Common Closure Block (required)
- root-cause statement (specific/upstream/actionable):
- symptom location (where issue manifested):
- authority fix point (where prevention belongs):
- fix placement (`authority-first` or `symptom patch + infeasibility`):
- deterministic evidence package:
  - MRE witness (fail before/pass after):
  - regression test:
  - disconfirming test:
  - failure-path check:
- change record artifact path (if enabled): `docs/project/change-records/<timestamp>-<slug>.json`
