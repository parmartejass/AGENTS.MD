from __future__ import annotations

import argparse
import datetime as dt
from pathlib import Path
from typing import Any

from common import load_contract, read_json, utc_now, write_json


def build_case(
    incident: dict[str, Any],
    policy: dict[str, Any],
    now: dt.datetime,
) -> dict[str, Any]:
    incident_id = str(incident.get("id") or f"harness-gap-{now.strftime('%Y%m%d-%H%M%S')}")
    sla_days = int(policy.get("slaDays", 7))
    due_at = now + dt.timedelta(days=sla_days)

    return {
        "id": incident_id,
        "createdAt": now.isoformat(),
        "slaDueAt": due_at.isoformat(),
        "status": "open",
        "summary": incident.get("summary"),
        "workflow": incident.get("workflow"),
        "regressionSha": incident.get("regressionSha"),
        "fixturePath": incident.get("fixturePath"),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create deterministic harness-gap case records.")
    parser.add_argument("--contract", required=True, help="Path to control-plane contract JSON.")
    parser.add_argument("--incident-json", required=True, help="Incident JSON path/string.")
    parser.add_argument("--case-output", required=False, help="Optional case output path.")
    parser.add_argument("--output-json", default="-", help="Output JSON path or '-' for stdout.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    contract = load_contract(args.contract)
    policy = contract["harnessGapPolicy"]
    incident = read_json(args.incident_json)
    if not isinstance(incident, dict):
        raise ValueError("incident-json must resolve to a JSON object")

    now = utc_now()
    case = build_case(incident=incident, policy=policy, now=now)

    case_output_path: str | None = args.case_output
    if not case_output_path:
        cases_root = Path(str(policy.get("casesPath", "harness/cases")))
        case_output_path = str(cases_root / f"{case['id']}.json")

    case_path = Path(case_output_path)
    write_json(str(case_path), case)

    result = {
        "result": "SUCCESS",
        "issueLabel": policy.get("issueLabel"),
        "case": case,
        "caseOutputPath": str(case_path),
    }
    write_json(args.output_json, result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
