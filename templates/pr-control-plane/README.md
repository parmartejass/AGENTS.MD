# PR Control-Plane Template (GitHub Actions + Mock Review Adapter)

This template provides a deterministic PR control-plane pattern:
- policy gate first,
- CI fanout second,
- current-head review state required,
- browser evidence validation,
- remediation loop and bot-thread cleanup,
- harness-gap intake for incidents.

It is provider-agnostic at the contract boundary. A deterministic mock adapter is included.

If wording here conflicts with `AGENTS.md`, `AGENTS.md` wins.
This README is supporting guidance; the machine-readable contract and schema remain the policy SSOT.

## What Is Included
- `control-plane.contract.json`: machine-readable policy contract.
- `schemas/control-plane-contract.schema.json`: contract schema.
- `workflows/*.yml`: copyable workflow templates.
- `scripts/main.py`: parent contract and CLI boundary for deterministic policy/evidence/check logic.
- `scripts/<feature>/main.py`: child feature contracts called only by `scripts/main.py`.
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
The default high-tier required checks are the values under `mergePolicy.high.requiredChecks` in `control-plane.contract.json`.
Ensure workflow/job names match that contract-owned list.

## Provider Swap
To replace the mock adapter:
1. Keep normalized output shape and invariants from `adapters/review_adapter_contract.md`.
2. Preserve current-head SHA strictness and actionable finding semantics.
3. Keep rerun dedupe and thread-cleanup semantics unchanged.

## Script Architecture
- `scripts/main.py` is the only public connector for the script subtree.
- Each child feature lives in its own folder, such as `scripts/risk_policy_gate/main.py` or `scripts/check_review_state/main.py`.
- All file and JSON I/O stays in `scripts/main.py`; child feature contracts take plain data in and return plain data out.
