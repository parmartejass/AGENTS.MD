from __future__ import annotations

import datetime as dt
from typing import Any


UTC = dt.timezone.utc


def _parse_iso8601(value: str) -> dt.datetime:
    normalized = value.replace("Z", "+00:00")
    parsed = dt.datetime.fromisoformat(normalized)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)


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
            generated_at = _parse_iso8601(generated_at_raw)
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
        return failures + [
            {
                "code": "MISSING_FLOWS",
                "message": "Browser evidence manifest must contain at least one flow.",
            }
        ]

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
    risk_tier: str,
    manifest: dict[str, Any] | None,
    now: dt.datetime,
) -> dict[str, Any]:
    policy = contract["browserEvidencePolicy"]
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
    return {
        "result": "FAILURE" if failures else "SUCCESS",
        "reason": "EVIDENCE_VALIDATED",
        "riskTier": risk_tier,
        "required": True,
        "failures": failures,
    }
