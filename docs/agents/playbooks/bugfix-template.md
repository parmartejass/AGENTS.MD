---
doc_type: playbook
ssot_owner: AGENTS.md
update_trigger: change safety or verification expectations change
---

# Playbook - Bugfix

Use when:
- Task matches profile `bugfix` in `agents-manifest.yaml`.
- Task is a bug/error/regression diagnosis or fix.

Reference authority:
- `AGENTS.md` "First-Principles Protocol (Hard Gate)"
- `AGENTS.md` "Bias-Resistant Debugging (Hard Gate)"
- `AGENTS.md` "Verification Floors (Hard Gate)"
- `docs/agents/playbooks/rca-methods-template.md`

This template is a prompting scaffold. If any wording conflicts with policy, `AGENTS.md` wins.

## Symptom
- observed behavior:
- expected behavior:

## Defect vocabulary
- symptom/manifestation:
- root cause:
- workaround(s) attempted:
- blast radius (impacted modules/workflows/users):

## Repro inputs
- files/folders:
- minimal steps:

## Model + invariants (first principles)
- system boundary (what's in/out of scope):
- inputs -> transformation -> outputs:
- invariants to preserve (resource safety, determinism, SSOT rules):

## SSOT impact analysis
- duplicated logic present? (where):
- missing SSOT rule/constant? (what):

## Authority trace (fix at root, not symptom)
- symptom location (where error manifested):
- authority fix point (where fix should be applied):
- class of errors prevented by fixing at authority:
- authority owner unknown or conflicting? (Y/N):
- if authority owner is unknown/conflicting: STOP and resolve ownership before implementing the fix.
- if patching at symptom, justify:

## RCA evidence
- deterministic repro command + failure signal:
- MRE fixture path + command:
- falsifiable hypothesis:
- disconfirming experiment (edge/adversarial):
- root-cause statement (specific/upstream/actionable):
- RCA method(s) used (5 Whys/Fishbone/Pareto/FMEA, if applicable):
- evidence (R/D) + where recorded:

## Fix plan
- SSOT owner to change:
- call sites to rewire:
- verification to run:

## Verification + risk scan
- verification commands (from README.md "Checks"):
- MRE witness (fail before / pass after):
- regression test:
- disconfirming test:
- failure-path check:
- change record artifact (when enabled): `docs/project/change-records/<timestamp>-<slug>.json`
- if behavior changed: shift-left prevention updates (tests/design/contracts/observability):
- modularity decision (if new logic introduced; reference `AGENTS.md` Non-Negotiable 11):
- security/resource/perf scan (notes):
