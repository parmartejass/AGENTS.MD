from __future__ import annotations

import argparse
from typing import Any

from common import (
    check_run_is_success,
    compute_risk_tier,
    load_contract,
    matches_any,
    normalize_check_runs,
    read_json,
    run_sort_key,
    write_json,
)


def evaluate_policy(
    contract: dict[str, Any],
    changed_files: list[str],
    check_runs: list[dict[str, Any]] | None = None,
    head_sha: str | None = None,
) -> dict[str, Any]:
    failures: list[dict[str, Any]] = []

    risk_rules = contract["riskTierRules"]
    risk_tier = compute_risk_tier(changed_files, risk_rules)
    required_checks = contract["mergePolicy"].get(risk_tier, {}).get("requiredChecks", [])

    docs_drift = contract["docsDriftRules"]
    control_plane_paths = docs_drift.get("controlPlanePaths", [])
    required_docs = docs_drift.get("requiredDocs", [])

    control_plane_changed = [path for path in changed_files if matches_any(path, control_plane_paths)]
    if control_plane_changed:
        missing_docs = [doc for doc in required_docs if doc not in changed_files]
        if missing_docs:
            failures.append(
                {
                    "code": "DOCS_DRIFT_REQUIRED_DOCS_MISSING",
                    "message": "Control-plane changes require corresponding docs updates.",
                    "detail": {
                        "controlPlaneChanged": control_plane_changed,
                        "missingDocs": missing_docs,
                    },
                }
            )

    checks_validated = False
    if check_runs is not None:
        checks_validated = True
        normalized_runs = normalize_check_runs(check_runs)
        for required_name in required_checks:
            matches = [run for run in normalized_runs if run.get("name") == required_name]
            if head_sha:
                matches = [run for run in matches if run.get("head_sha") == head_sha]

            if not matches:
                failures.append(
                    {
                        "code": "MISSING_REQUIRED_CHECK",
                        "message": f"Required check '{required_name}' was not found for the current head.",
                        "detail": {"requiredCheck": required_name, "headSha": head_sha},
                    }
                )
                continue

            latest = sorted(matches, key=run_sort_key, reverse=True)[0]
            if not check_run_is_success(latest):
                failures.append(
                    {
                        "code": "REQUIRED_CHECK_NOT_SUCCESS",
                        "message": f"Required check '{required_name}' is not successful.",
                        "detail": {
                            "requiredCheck": required_name,
                            "status": latest.get("status"),
                            "conclusion": latest.get("conclusion"),
                            "headSha": latest.get("head_sha"),
                        },
                    }
                )

    result = "FAILURE" if failures else "SUCCESS"
    return {
        "result": result,
        "riskTier": risk_tier,
        "requiredChecks": required_checks,
        "checksValidated": checks_validated,
        "failures": failures,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evaluate PR risk-policy gate contract.")
    parser.add_argument("--contract", required=True, help="Path to control-plane contract JSON.")
    parser.add_argument(
        "--changed-files-json",
        required=True,
        help="JSON array of changed files or path to JSON file containing that array.",
    )
    parser.add_argument(
        "--check-runs-json",
        required=False,
        help="Optional JSON list of check runs (or object with check_runs) for required-check validation.",
    )
    parser.add_argument("--head-sha", required=False, help="Current PR head SHA.")
    parser.add_argument(
        "--output-json",
        default="-",
        help="Output JSON path. Use '-' to print to stdout.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    contract = load_contract(args.contract)
    changed_files = read_json(args.changed_files_json)
    if not isinstance(changed_files, list):
        raise ValueError("changed-files-json must resolve to a JSON list")

    check_runs = read_json(args.check_runs_json) if args.check_runs_json else None
    result = evaluate_policy(
        contract=contract,
        changed_files=[str(path) for path in changed_files],
        check_runs=check_runs,
        head_sha=args.head_sha,
    )
    write_json(args.output_json, result)
    return 0 if result["result"] == "SUCCESS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
