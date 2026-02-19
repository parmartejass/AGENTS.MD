from __future__ import annotations

import argparse
import datetime as dt
from pathlib import Path
from typing import Any

from common import compute_risk_tier, load_contract, parse_iso8601, read_json, utc_now, write_json


def _validate_manifest(
    manifest: dict[str, Any],
    head_sha: str,
    required_flows: list[str],
    max_age_hours: float,
    now: dt.datetime,
) -> list[dict[str, Any]]:
    failures: list[dict[str, Any]] = []

    manifest_head = str(manifest.get("headSha", ""))
    if manifest_head != head_sha:
        failures.append(
            {
                "code": "EVIDENCE_HEAD_SHA_MISMATCH",
                "message": "Browser evidence headSha does not match current PR head.",
                "detail": {"expectedHeadSha": head_sha, "manifestHeadSha": manifest_head},
            }
        )

    generated_at_raw = manifest.get("generatedAt")
    if not isinstance(generated_at_raw, str):
        failures.append(
            {
                "code": "MISSING_GENERATED_AT",
                "message": "Browser evidence manifest is missing generatedAt timestamp.",
            }
        )
    else:
        try:
            generated_at = parse_iso8601(generated_at_raw)
            age_hours = (now - generated_at).total_seconds() / 3600.0
            if age_hours > max_age_hours:
                failures.append(
                    {
                        "code": "EVIDENCE_STALE",
                        "message": "Browser evidence artifact is stale.",
                        "detail": {"maxAgeHours": max_age_hours, "artifactAgeHours": age_hours},
                    }
                )
        except ValueError:
            failures.append(
                {
                    "code": "INVALID_GENERATED_AT",
                    "message": "generatedAt is not a valid ISO8601 timestamp.",
                }
            )

    flows = manifest.get("flows", [])
    if not isinstance(flows, list) or not flows:
        failures.append(
            {
                "code": "MISSING_FLOWS",
                "message": "Browser evidence manifest must contain at least one flow.",
            }
        )
        return failures

    flow_by_id = {str(flow.get("id")): flow for flow in flows if isinstance(flow, dict)}
    missing_required = [flow_id for flow_id in required_flows if flow_id not in flow_by_id]
    if missing_required:
        failures.append(
            {
                "code": "MISSING_REQUIRED_FLOW",
                "message": "Required flow IDs are missing from browser evidence.",
                "detail": {"missingFlowIds": missing_required},
            }
        )

    for flow in flow_by_id.values():
        flow_id = str(flow.get("id"))
        assertions = flow.get("assertions", [])
        if not isinstance(assertions, list) or not assertions:
            failures.append(
                {
                    "code": "FLOW_ASSERTIONS_MISSING",
                    "message": "Flow is missing assertions.",
                    "detail": {"flowId": flow_id},
                }
            )
            continue

        failed_assertions = [
            assertion for assertion in assertions if isinstance(assertion, dict) and not bool(assertion.get("passed"))
        ]
        if failed_assertions:
            failures.append(
                {
                    "code": "FLOW_ASSERTION_FAILED",
                    "message": "One or more flow assertions failed.",
                    "detail": {
                        "flowId": flow_id,
                        "failedAssertions": [assertion.get("name") for assertion in failed_assertions],
                    },
                }
            )

        if bool(flow.get("requiresIdentity")) and not str(flow.get("identity", "")).strip():
            failures.append(
                {
                    "code": "FLOW_IDENTITY_MISSING",
                    "message": "Authenticated flow requires identity but none was provided.",
                    "detail": {"flowId": flow_id},
                }
            )

    return failures


def evaluate_browser_evidence(
    contract: dict[str, Any],
    head_sha: str,
    changed_files: list[str],
    manifest: dict[str, Any] | None,
    now: dt.datetime | None = None,
) -> dict[str, Any]:
    now = now or utc_now()
    policy = contract["browserEvidencePolicy"]
    risk_tier = compute_risk_tier(changed_files, contract["riskTierRules"])
    required_tiers = set(policy.get("requiredForRiskTiers", []))
    required = bool(policy.get("blocking", False)) and (not required_tiers or risk_tier in required_tiers)

    if not required:
        return {
            "result": "SUCCESS",
            "reason": "EVIDENCE_NOT_REQUIRED_FOR_RISK_TIER",
            "riskTier": risk_tier,
            "required": False,
            "failures": [],
        }

    if manifest is None:
        return {
            "result": "FAILURE",
            "reason": "EVIDENCE_REQUIRED_BUT_MANIFEST_MISSING",
            "riskTier": risk_tier,
            "required": True,
            "failures": [
                {
                    "code": "MANIFEST_MISSING",
                    "message": "Browser evidence manifest is required but missing.",
                }
            ],
        }

    failures = _validate_manifest(
        manifest=manifest,
        head_sha=head_sha,
        required_flows=[str(flow_id) for flow_id in policy.get("requiredFlows", [])],
        max_age_hours=float(policy.get("maxArtifactAgeHours", 24)),
        now=now,
    )
    result = "FAILURE" if failures else "SUCCESS"
    return {
        "result": result,
        "reason": "EVIDENCE_VALIDATED",
        "riskTier": risk_tier,
        "required": True,
        "failures": failures,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate browser evidence manifest.")
    parser.add_argument("--contract", required=True, help="Path to control-plane contract JSON.")
    parser.add_argument("--head-sha", required=True, help="Current PR head SHA.")
    parser.add_argument(
        "--changed-files-json",
        required=True,
        help="JSON list/path for changed files used for risk-tier determination.",
    )
    parser.add_argument(
        "--manifest-json",
        required=False,
        help="Optional manifest JSON path/string override. If omitted, uses contract path.",
    )
    parser.add_argument(
        "--output-json",
        default="-",
        help="Output JSON path or '-' for stdout.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    contract = load_contract(args.contract)
    changed_files = read_json(args.changed_files_json)
    if not isinstance(changed_files, list):
        raise ValueError("changed-files-json must resolve to a JSON list")

    manifest: dict[str, Any] | None
    if args.manifest_json:
        parsed_manifest = read_json(args.manifest_json)
        if not isinstance(parsed_manifest, dict):
            raise ValueError("manifest-json must resolve to a JSON object")
        manifest = parsed_manifest
    else:
        manifest_path = Path(str(contract["browserEvidencePolicy"]["manifestPath"]))
        if manifest_path.exists():
            parsed_manifest = read_json(str(manifest_path))
            if not isinstance(parsed_manifest, dict):
                raise ValueError("manifest path must contain a JSON object")
            manifest = parsed_manifest
        else:
            manifest = None

    result = evaluate_browser_evidence(
        contract=contract,
        head_sha=args.head_sha,
        changed_files=[str(path) for path in changed_files],
        manifest=manifest,
    )
    write_json(args.output_json, result)
    return 0 if result["result"] == "SUCCESS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
