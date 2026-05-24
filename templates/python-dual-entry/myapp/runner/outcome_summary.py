"""Run outcome summary construction for structured event logs."""

from __future__ import annotations

from myapp.log_contract import ItemOutcome, Phase


def build_run_summary(*, item_outcome: ItemOutcome, final_phase: Phase) -> dict[str, dict[str, int]]:
    executed = 1 if item_outcome == ItemOutcome.EXECUTED else 0
    skipped = 1 if item_outcome == ItemOutcome.SKIPPED else 0
    failed = 1 if item_outcome == ItemOutcome.FAILED else 0

    return {
        "by_outcome": {
            "executed": executed,
            "skipped": skipped,
            "failed": failed,
        },
        "failed_by_phase": {
            "validation": 1 if final_phase == Phase.FAILED_VALIDATION else 0,
            "commit": 1 if final_phase == Phase.FAILED_COMMIT else 0,
            "cleanup": 1 if final_phase == Phase.FAILED_CLEANUP else 0,
        },
        "work_counts": {
            "planned": 1,
            "eligible": 0 if final_phase == Phase.FAILED_VALIDATION else 1,
            "executed": executed,
            "skipped": skipped,
            "failed": failed,
        },
    }
