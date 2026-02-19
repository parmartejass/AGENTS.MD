# PR Control-Plane Template (GitHub Actions + Mock Review Adapter)

This template provides a deterministic PR control-plane pattern:
- policy gate first,
- CI fanout second,
- current-head review state required,
- browser evidence validation,
- remediation loop and bot-thread cleanup,
- harness-gap intake for incidents.

It is provider-agnostic at the contract boundary. A deterministic mock adapter is included.

## What Is Included
- `control-plane.contract.json`: machine-readable policy contract.
- `schemas/control-plane-contract.schema.json`: contract schema.
- `workflows/*.yml`: copyable workflow templates.
- `scripts/*.py`: deterministic policy/evidence/check logic.
- `adapters/review_adapter_contract.md`: provider-agnostic adapter contract.
- `adapters/mock/adapter.py`: mock adapter reference.
- `tests/`: fixture-backed contract/policy/evidence tests.

## Install In A Target Repo
1. Copy this folder into your target repo, for example:
   - `automation/pr-control-plane/`
2. Copy `workflows/*.yml` into `.github/workflows/`.
3. Update each workflow `CONTROL_PLANE_ROOT` env if your folder path differs.
4. Update `control-plane.contract.json` with your repo paths/check names.
5. Wire your review provider by implementing the contract in `adapters/review_adapter_contract.md`.

## Contract Semantics
The contract is the SSOT for:
- risk tiers and required checks,
- docs drift policy for control-plane changes,
- review state requirements,
- canonical rerun comment writer + dedupe marker,
- remediation policy and attempt bounds,
- bot-only thread auto-resolve policy,
- browser evidence requirements,
- harness-gap SLA metadata.

## Deterministic Local Validation
From template root:

```bash
python3 -m unittest -v \
  tests.contract.test_review_adapter_contract \
  tests.policy.test_risk_policy_gate \
  tests.policy.test_review_state \
  tests.evidence.test_browser_evidence
```

If `python3` is unavailable, use `python`.

## Required Check Names
The default high-tier required checks in `control-plane.contract.json` are:
- `risk-policy-gate`
- `harness-smoke`
- `Browser Evidence`
- `CI Pipeline`

Ensure workflow/job names match these check names.

## Provider Swap
To replace the mock adapter:
1. Keep normalized output shape and invariants from `adapters/review_adapter_contract.md`.
2. Preserve current-head SHA strictness and actionable finding semantics.
3. Keep rerun dedupe and thread-cleanup semantics unchanged.
