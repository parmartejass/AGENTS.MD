from __future__ import annotations

import datetime as dt
from typing import Any


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
