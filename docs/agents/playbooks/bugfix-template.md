---
doc_type: playbook
ssot_owner: AGENTS.md
update_trigger: change safety or verification expectations change
---

# Playbook — Bugfix

Use when:
- Task matches profile `bugfix` in `agents-manifest.yaml`.

## Symptom
- observed behavior:
- expected behavior:

## Repro inputs
- files/folders:
- minimal steps:

## Model + invariants (first principles)
- system boundary (what's in/out of scope):
- inputs -> transformation -> outputs:
- invariants to preserve (resource safety, determinism, SSOT rules):

## SSOT impact analysis
- duplicated logic present? (where)
- missing SSOT rule/constant? (what)

## Authority trace (fix at root, not symptom)
- Symptom location (where error manifested):
- Authority fix point (where fix should be applied):
- Class of errors prevented by fixing at authority:
- If patching at symptom, justify:

## Fix plan
- SSOT owner to change:
- call sites to rewire:
- verification to run:
