from __future__ import annotations

import datetime as dt
import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Any


UTC = dt.timezone.utc


class InputError(ValueError):
    """Raised when user-supplied inputs violate the parent contract."""


class ContractError(ValueError):
    """Raised when the control-plane contract is malformed."""


def parse_iso8601(value: str) -> dt.datetime:
    normalized = value.replace("Z", "+00:00")
    parsed = dt.datetime.fromisoformat(normalized)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)


def utc_now() -> dt.datetime:
    return dt.datetime.now(tz=UTC)


def read_json(path_or_json: str) -> Any:
    try:
        return json.loads(path_or_json)
    except json.JSONDecodeError:
        candidate = Path(path_or_json)
        if not candidate.exists():
            raise
        return json.loads(candidate.read_text(encoding="utf-8"))


def write_json(path: str, payload: dict[str, Any]) -> None:
    if path == "-":
        sys.stdout.write(json.dumps(payload, indent=2, sort_keys=True) + "\n")
        sys.stdout.flush()
        return

    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    _atomic_write_text(target, json.dumps(payload, indent=2, sort_keys=True))


def _atomic_write_text(target: Path, content: str) -> None:
    temp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=str(target.parent),
            delete=False,
            prefix=f".{target.name}.",
            suffix=".tmp",
        ) as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
            temp_path = Path(handle.name)
        temp_path.replace(target)
    finally:
        if temp_path is not None and temp_path.exists():
            temp_path.unlink(missing_ok=True)


def _require_mapping(parent: dict[str, Any], key: str) -> dict[str, Any]:
    value = parent.get(key)
    if not isinstance(value, dict):
        raise ContractError(f"Contract key '{key}' must be a JSON object.")
    return value


def _require_string_list(parent: dict[str, Any], key: str) -> list[str]:
    value = parent.get(key)
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise ContractError(f"Contract key '{key}' must be a JSON array of strings.")
    return value


def resolve_contract_relative_path(contract_path: str, raw_path: str, field_name: str) -> Path:
    contract_root = Path(contract_path).resolve().parent
    candidate = Path(raw_path)
    if candidate.is_absolute():
        raise ContractError(f"Contract field '{field_name}' must be a relative path.")

    resolved = (contract_root / candidate).resolve()
    try:
        resolved.relative_to(contract_root)
    except ValueError as exc:
        raise ContractError(
            f"Contract field '{field_name}' must stay within the contract root."
        ) from exc
    return resolved


def load_contract(path: str) -> dict[str, Any]:
    contract = read_json(path)
    if not isinstance(contract, dict):
        raise ContractError("Contract must resolve to a JSON object.")

    required_keys = (
        "riskTierRules",
        "mergePolicy",
        "docsDriftRules",
        "reviewPolicy",
        "rerunPolicy",
        "remediationPolicy",
        "threadPolicy",
        "browserEvidencePolicy",
        "harnessGapPolicy",
    )
    missing = [key for key in required_keys if key not in contract]
    if missing:
        raise ContractError(f"Contract missing required keys: {', '.join(missing)}")

    risk_tier_rules = _require_mapping(contract, "riskTierRules")
    if not risk_tier_rules:
        raise ContractError("Contract key 'riskTierRules' must not be empty.")
    if not all(isinstance(key, str) for key in risk_tier_rules):
        raise ContractError("Contract key 'riskTierRules' must use string tier names.")
    for tier, patterns in risk_tier_rules.items():
        if not isinstance(patterns, list) or not all(isinstance(item, str) for item in patterns):
            raise ContractError(f"riskTierRules['{tier}'] must be a JSON array of strings.")

    merge_policy = _require_mapping(contract, "mergePolicy")
    for tier_name, tier_policy in merge_policy.items():
        if not isinstance(tier_policy, dict):
            raise ContractError(f"mergePolicy['{tier_name}'] must be a JSON object.")
        _require_string_list(tier_policy, "requiredChecks")

    docs_drift_rules = _require_mapping(contract, "docsDriftRules")
    _require_string_list(docs_drift_rules, "controlPlanePaths")
    _require_string_list(docs_drift_rules, "requiredDocs")

    review_policy = _require_mapping(contract, "reviewPolicy")
    if not isinstance(review_policy.get("requiredReviewCheck"), str):
        raise ContractError("reviewPolicy.requiredReviewCheck must be a string.")
    _require_string_list(review_policy, "actionableTokens")
    _require_string_list(review_policy, "weakConfidenceTokens")

    rerun_policy = _require_mapping(contract, "rerunPolicy")
    for key in ("canonicalWorkflow", "commentMarker", "triggerText"):
        if not isinstance(rerun_policy.get(key), str):
            raise ContractError(f"rerunPolicy.{key} must be a string.")

    remediation_policy = _require_mapping(contract, "remediationPolicy")
    if not isinstance(remediation_policy.get("branchPrefix"), str):
        raise ContractError("remediationPolicy.branchPrefix must be a string.")

    thread_policy = _require_mapping(contract, "threadPolicy")
    _require_string_list(thread_policy, "botAuthorAllowlist")

    browser_policy = _require_mapping(contract, "browserEvidencePolicy")
    if not isinstance(browser_policy.get("manifestPath"), str):
        raise ContractError("browserEvidencePolicy.manifestPath must be a string.")
    _require_string_list(browser_policy, "requiredForRiskTiers")
    _require_string_list(browser_policy, "requiredFlows")

    harness_policy = _require_mapping(contract, "harnessGapPolicy")
    for key in ("issueLabel", "casesPath"):
        if not isinstance(harness_policy.get(key), str):
            raise ContractError(f"harnessGapPolicy.{key} must be a string.")
    return contract
