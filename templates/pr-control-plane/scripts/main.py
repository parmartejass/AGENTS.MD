from __future__ import annotations

import argparse
import importlib
from pathlib import Path
from typing import Any

if __package__:
    from ._boundary import (  # type: ignore
        ContractError,
        InputError,
        load_contract,
        read_json,
        resolve_contract_relative_path,
        utc_now,
        write_json,
    )
else:
    from _boundary import (  # type: ignore
        ContractError,
        InputError,
        load_contract,
        read_json,
        resolve_contract_relative_path,
        utc_now,
        write_json,
    )


def _load_child_module(child_name: str):
    module_name = f"{__package__}.{child_name}.main" if __package__ else f"{child_name}.main"
    return importlib.import_module(module_name)


def _evaluate_review_state_fn():
    module = _load_child_module("check_review_state")
    return module.evaluate_review_state, module.select_latest_review_run


def _build_case_fn():
    return _load_child_module("harness_gap").build_case


def _evaluate_remediation_fn():
    return _load_child_module("remediation_loop").evaluate_remediation


def _evaluate_rerun_request_fn():
    return _load_child_module("request_rerun").evaluate_rerun_request


def _evaluate_thread_resolution_fn():
    return _load_child_module("resolve_bot_threads").evaluate_thread_resolution


def _evaluate_policy_fn():
    module = _load_child_module("risk_policy_gate")
    return module.evaluate_policy, module.compute_risk_tier


def _evaluate_browser_evidence_fn():
    return _load_child_module("validate_browser_evidence").evaluate_browser_evidence


def _read_json_list(path_or_json: str, field_name: str) -> list[Any]:
    value = read_json(path_or_json)
    if not isinstance(value, list):
        raise ValueError(f"{field_name} must resolve to a JSON list")
    return value


def _read_json_list_or_object_list(
    path_or_json: str,
    field_name: str,
    *,
    object_list_field: str,
) -> list[Any]:
    value = read_json(path_or_json)
    if isinstance(value, list):
        return value
    if isinstance(value, dict) and isinstance(value.get(object_list_field), list):
        return value[object_list_field]
    raise ValueError(
        f"{field_name} must resolve to a JSON list or an object with a '{object_list_field}' list"
    )


def _read_json_object(path_or_json: str, field_name: str) -> dict[str, Any]:
    value = read_json(path_or_json)
    if not isinstance(value, dict):
        raise ValueError(f"{field_name} must resolve to a JSON object")
    return value


def evaluate_browser_evidence(
    contract: dict[str, Any],
    head_sha: str,
    changed_files: list[str],
    manifest: dict[str, Any] | None,
    now=None,
) -> dict[str, Any]:
    _, compute_risk_tier = _evaluate_policy_fn()
    evaluate_browser_evidence_impl = _evaluate_browser_evidence_fn()
    risk_tier = compute_risk_tier(changed_files, contract["riskTierRules"])
    return evaluate_browser_evidence_impl(
        contract=contract,
        head_sha=head_sha,
        risk_tier=risk_tier,
        manifest=manifest,
        now=now or utc_now(),
    )


def _run_check_review_state(args: argparse.Namespace) -> int:
    contract = load_contract(args.contract)
    evaluate_review_state_impl, select_latest_review_run = _evaluate_review_state_fn()
    review_runs = _read_json_list_or_object_list(
        args.review_runs_json,
        "review-runs-json",
        object_list_field="check_runs",
    )
    findings = _read_json_list(args.findings_json, "findings-json")
    review_run = select_latest_review_run(
        review_runs=[entry for entry in review_runs if isinstance(entry, dict)],
        required_check_name=str(contract["reviewPolicy"].get("requiredReviewCheck")),
        head_sha=args.head_sha,
    )
    result = evaluate_review_state_impl(
        contract=contract,
        head_sha=args.head_sha,
        review_run=review_run,
        findings=[entry for entry in findings if isinstance(entry, dict)],
        timed_out=args.timed_out,
    )
    write_json(args.output_json, result)
    return 0 if result["result"] == "SUCCESS" else 1


def _run_harness_gap(args: argparse.Namespace) -> int:
    contract = load_contract(args.contract)
    build_case = _build_case_fn()
    incident = _read_json_object(args.incident_json, "incident-json")
    case = build_case(incident=incident, policy=contract["harnessGapPolicy"], now=utc_now())

    case_output_path = args.case_output
    if not case_output_path:
        cases_root = resolve_contract_relative_path(
            args.contract,
            str(contract["harnessGapPolicy"].get("casesPath", "harness/cases")),
            "harnessGapPolicy.casesPath",
        )
        case_output_path = str(cases_root / f"{case['id']}.json")

    write_json(case_output_path, case)
    result = {
        "result": "SUCCESS",
        "issueLabel": contract["harnessGapPolicy"].get("issueLabel"),
        "case": case,
        "caseOutputPath": case_output_path,
    }
    write_json(args.output_json, result)
    return 0


def _run_remediation_loop(args: argparse.Namespace) -> int:
    contract = load_contract(args.contract)
    evaluate_remediation = _evaluate_remediation_fn()
    findings = _read_json_list(args.findings_json, "findings-json")
    attempt_history = _read_json_list(args.attempt_history_json, "attempt-history-json")
    result = evaluate_remediation(
        contract=contract,
        head_sha=args.head_sha,
        findings=[entry for entry in findings if isinstance(entry, dict)],
        attempt_history=[entry for entry in attempt_history if isinstance(entry, dict)],
    )
    write_json(args.output_json, result)
    return 0


def _run_request_rerun(args: argparse.Namespace) -> int:
    contract = load_contract(args.contract)
    evaluate_rerun_request = _evaluate_rerun_request_fn()
    comments = _read_json_list(args.comments_json, "comments-json")
    result = evaluate_rerun_request(
        contract=contract,
        head_sha=args.head_sha,
        comments=[entry for entry in comments if isinstance(entry, dict)],
    )
    write_json(args.output_json, result)
    return 0


def _run_resolve_bot_threads(args: argparse.Namespace) -> int:
    contract = load_contract(args.contract)
    evaluate_thread_resolution = _evaluate_thread_resolution_fn()
    threads = _read_json_list(args.threads_json, "threads-json")
    result = evaluate_thread_resolution(
        contract=contract,
        threads=[entry for entry in threads if isinstance(entry, dict)],
        clean_rerun=args.clean_rerun,
    )
    write_json(args.output_json, result)
    return 0


def _run_risk_policy_gate(args: argparse.Namespace) -> int:
    contract = load_contract(args.contract)
    evaluate_policy, _ = _evaluate_policy_fn()
    changed_files = _read_json_list(args.changed_files_json, "changed-files-json")
    check_runs = read_json(args.check_runs_json) if args.check_runs_json else None
    if check_runs is not None and not args.head_sha:
        raise InputError("--head-sha is required when --check-runs-json is supplied.")
    result = evaluate_policy(
        contract=contract,
        changed_files=[str(path) for path in changed_files],
        check_runs=check_runs,
        head_sha=args.head_sha,
    )
    write_json(args.output_json, result)
    return 0 if result["result"] == "SUCCESS" else 1


def _run_validate_browser_evidence(args: argparse.Namespace) -> int:
    contract = load_contract(args.contract)
    changed_files = [str(path) for path in _read_json_list(args.changed_files_json, "changed-files-json")]

    manifest: dict[str, Any] | None
    if args.manifest_json:
        manifest = _read_json_object(args.manifest_json, "manifest-json")
    else:
        manifest_path = resolve_contract_relative_path(
            args.contract,
            str(contract["browserEvidencePolicy"]["manifestPath"]),
            "browserEvidencePolicy.manifestPath",
        )
        manifest = _read_json_object(str(manifest_path), "manifest-json") if manifest_path.exists() else None

    result = evaluate_browser_evidence(
        contract=contract,
        head_sha=args.head_sha,
        changed_files=changed_files,
        manifest=manifest,
        now=utc_now(),
    )
    write_json(args.output_json, result)
    return 0 if result["result"] == "SUCCESS" else 1


def load_contract_file(path: str) -> dict[str, Any]:
    return load_contract(path)


def evaluate_review_state(*args, **kwargs):
    evaluate_review_state_impl, _ = _evaluate_review_state_fn()
    return evaluate_review_state_impl(*args, **kwargs)


def evaluate_policy(*args, **kwargs):
    evaluate_policy_impl, _ = _evaluate_policy_fn()
    return evaluate_policy_impl(*args, **kwargs)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Parent contract for PR control-plane script features.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    review_parser = subparsers.add_parser("check-review-state", help="Validate review-agent state.")
    review_parser.add_argument("--contract", required=True, help="Path to control-plane contract JSON.")
    review_parser.add_argument("--head-sha", required=True, help="Current PR head SHA.")
    review_parser.add_argument("--review-runs-json", required=True, help="JSON list/object of check runs.")
    review_parser.add_argument("--findings-json", default="[]", help="JSON list/path for normalized findings.")
    review_parser.add_argument("--timed-out", action="store_true", help="Force timeout failure mode.")
    review_parser.add_argument("--output-json", default="-", help="Output JSON path or '-' for stdout.")
    review_parser.set_defaults(handler=_run_check_review_state)

    harness_parser = subparsers.add_parser("harness-gap", help="Create deterministic harness-gap case records.")
    harness_parser.add_argument("--contract", required=True, help="Path to control-plane contract JSON.")
    harness_parser.add_argument("--incident-json", required=True, help="Incident JSON path/string.")
    harness_parser.add_argument("--case-output", required=False, help="Optional case output path.")
    harness_parser.add_argument("--output-json", default="-", help="Output JSON path or '-' for stdout.")
    harness_parser.set_defaults(handler=_run_harness_gap)

    remediation_parser = subparsers.add_parser("remediation-loop", help="Evaluate remediation action.")
    remediation_parser.add_argument("--contract", required=True, help="Path to control-plane contract JSON.")
    remediation_parser.add_argument("--head-sha", required=True, help="Current PR head SHA.")
    remediation_parser.add_argument("--findings-json", required=True, help="JSON list/path for normalized findings.")
    remediation_parser.add_argument(
        "--attempt-history-json",
        default="[]",
        help="JSON list/path of prior remediation attempts.",
    )
    remediation_parser.add_argument("--output-json", default="-", help="Output JSON path or '-' for stdout.")
    remediation_parser.set_defaults(handler=_run_remediation_loop)

    rerun_parser = subparsers.add_parser("request-rerun", help="Canonical rerun-comment dedupe evaluator.")
    rerun_parser.add_argument("--contract", required=True, help="Path to control-plane contract JSON.")
    rerun_parser.add_argument("--head-sha", required=True, help="Current PR head SHA.")
    rerun_parser.add_argument("--comments-json", required=True, help="JSON list/path of issue comments.")
    rerun_parser.add_argument("--output-json", default="-", help="Output JSON path or '-' for stdout.")
    rerun_parser.set_defaults(handler=_run_request_rerun)

    threads_parser = subparsers.add_parser("resolve-bot-threads", help="Resolve bot-only review threads.")
    threads_parser.add_argument("--contract", required=True, help="Path to control-plane contract JSON.")
    threads_parser.add_argument("--threads-json", required=True, help="JSON list/path of review threads.")
    threads_parser.add_argument("--clean-rerun", action="store_true", help="Indicates rerun is clean.")
    threads_parser.add_argument("--output-json", default="-", help="Output JSON path or '-' for stdout.")
    threads_parser.set_defaults(handler=_run_resolve_bot_threads)

    policy_parser = subparsers.add_parser("risk-policy-gate", help="Evaluate PR risk-policy gate contract.")
    policy_parser.add_argument("--contract", required=True, help="Path to control-plane contract JSON.")
    policy_parser.add_argument("--changed-files-json", required=True, help="JSON array/path of changed files.")
    policy_parser.add_argument("--check-runs-json", required=False, help="Optional JSON list/object of check runs.")
    policy_parser.add_argument("--head-sha", required=False, help="Current PR head SHA.")
    policy_parser.add_argument("--output-json", default="-", help="Output JSON path or '-' for stdout.")
    policy_parser.set_defaults(handler=_run_risk_policy_gate)

    evidence_parser = subparsers.add_parser("validate-browser-evidence", help="Validate browser evidence manifest.")
    evidence_parser.add_argument("--contract", required=True, help="Path to control-plane contract JSON.")
    evidence_parser.add_argument("--head-sha", required=True, help="Current PR head SHA.")
    evidence_parser.add_argument("--changed-files-json", required=True, help="JSON list/path for changed files.")
    evidence_parser.add_argument("--manifest-json", required=False, help="Optional manifest JSON path/string.")
    evidence_parser.add_argument("--output-json", default="-", help="Output JSON path or '-' for stdout.")
    evidence_parser.set_defaults(handler=_run_validate_browser_evidence)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    try:
        args = parser.parse_args(argv)
        return args.handler(args)
    except SystemExit as exc:
        if int(exc.code or 0) == 0:
            return 0
        write_json(
            "-",
            {
                "result": "FAILURE",
                "reason": "INVALID_ARGS",
                "details": {"exitCode": int(exc.code or 1)},
            },
        )
        return int(exc.code or 1)
    except (ContractError, InputError, FileNotFoundError, ValueError) as exc:
        write_json(
            "-",
            {
                "result": "FAILURE",
                "reason": exc.__class__.__name__.upper(),
                "details": {"message": str(exc)},
            },
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
