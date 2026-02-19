---
doc_type: runbook
ssot_owner: AGENTS.md
update_trigger: PR control-plane flow, contract keys, or review/evidence policies change
---

# PR Control-Plane Loop

## Purpose
Provide a deterministic control-plane pattern for pull requests where:
- a coding agent proposes code,
- a risk-policy gate evaluates policy requirements,
- a code-review agent must be clean on the current head SHA,
- machine-verifiable evidence (tests, browser, review) is required,
- regressions are converted into harness-gap cases.

## Scope
- This runbook documents semantics and ordering.
- Copy implementation assets from `templates/pr-control-plane/` into the target repo.
- Keep provider integration pluggable: adapter contract is stable, provider module is swappable.

## Core ordering invariant
1. `risk-policy-gate` runs before expensive CI fanout.
2. CI fanout and browser evidence jobs run only after preflight pass.
3. Review-agent state is accepted only when tied to the current PR head SHA.
4. Merge remains blocked while actionable findings exist for the current head.

## Machine-readable contract
Use a single contract file as policy SSOT:
- `riskTierRules`
- `mergePolicy`
- `docsDriftRules`
- `reviewPolicy`
- `rerunPolicy`
- `remediationPolicy`
- `threadPolicy`
- `browserEvidencePolicy`
- `harnessGapPolicy`

Default template path:
- `templates/pr-control-plane/control-plane.contract.json`

## Current-head SHA discipline
- Review evidence is valid only for `pull_request.head.sha`.
- Stale "clean" runs for older SHAs are ignored.
- After each synchronize/push event, review rerun and policy gate must evaluate the new SHA.

## Canonical rerun writer
- Use exactly one workflow to request review reruns.
- Dedupe requests by marker and `sha:<headSha>` token.
- Do not allow multiple workflows to post rerun comments.

## Remediation loop
- Remediation is enabled by policy.
- Remediation never bypasses policy gates.
- Remediation must target the current PR branch/head and produce deterministic evidence for the next gate run.

## Bot-only stale thread cleanup
- Auto-resolve unresolved threads only when:
  - current-head rerun is clean, and
  - all thread comments are from approved bot identities.
- Never auto-resolve human-participated threads.

## Browser evidence policy
- For UI/user-flow changes, require evidence manifest checks in CI.
- Evidence must verify:
  - required flows exist,
  - entrypoint identity is correct,
  - authenticated identity matches expectation (when required),
  - artifacts are fresh and bound to current head SHA.

## Harness-gap loop
- For production regressions:
  1. create a harness-gap record,
  2. add deterministic case/fixture,
  3. track SLA metadata for closure.
- Keep issue/case metadata machine-readable.

## Verification
- Validate template behavior with fixture-backed tests under:
  - `templates/pr-control-plane/tests/contract/`
  - `templates/pr-control-plane/tests/policy/`
  - `templates/pr-control-plane/tests/evidence/`
- Repo-wide governance checks remain in `README.md` section "Checks".
