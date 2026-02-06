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

## Input block (required)
- symptom/manifestation:
- expected behavior:
- impact + blast radius:
- reproduction command:
- fixture path(s):

## Method 1 - Fishbone (cause space)
- categories analyzed (people/process/technology/environment/data/policy):
- candidate causes:
- evidence per candidate (R/D):
- causes rejected + disconfirming signal:

## Method 2 - Pareto (prioritization)
- measured causes:
- metric used (frequency/severity/cost):
- top causes selected + threshold:
- rationale for selected root-cause path:

## Method 3 - 5 Whys (upstream trace)
- why #1:
- why #2:
- why #3:
- why #4:
- why #5 (authority boundary reached):
- authority fix point:
- class of errors prevented by fixing at authority:

## Method 4 - FMEA/DFMEA (recurrence prevention)
- adjacent failure modes:
- severity/occurrence/detection notes:
- prevention controls added:
- residual risk:

## Required output
- root-cause statement (specific/upstream/actionable):
- fix placement (`authority-first` or `symptom patch + infeasibility`):
- deterministic evidence package:
  - MRE (fail before/pass after)
  - regression test
  - disconfirming test
  - failure-path check
- change record artifact path (if enabled): `docs/project/change-records/<timestamp>-<slug>.json`
