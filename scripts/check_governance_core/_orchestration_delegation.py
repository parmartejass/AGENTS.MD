from __future__ import annotations

from typing import Any


def _strings(value: object, label: str, errors: list[str]) -> set[str]:
    if not isinstance(value, list) or not value or any(
        not isinstance(item, str) or not item.strip() for item in value
    ):
        errors.append(f"Orchestration.md contract {label} must be a non-empty string list")
        return set()
    if len(set(value)) != len(value):
        errors.append(f"Orchestration.md contract {label} must not contain duplicates")
    return set(value)


def validate_delegation_and_plan(
    data: dict[str, Any], roles: set[str], state_roles: dict[str, set[str]]
) -> list[str]:
    errors: list[str] = []
    delegation = data.get("delegation")
    if not isinstance(delegation, dict) or set(delegation) != {
        "task_roles", "explorer_jurisdictions", "explorers_per_task"
    }:
        errors.append("Orchestration.md contract delegation has invalid fields")
    else:
        _validate_delegation(delegation, data, roles, state_roles, errors)
    plan = data.get("plan")
    if not isinstance(plan, dict) or set(plan) != {"format", "persistence", "required_fields"}:
        errors.append("Orchestration.md contract plan has invalid fields")
    else:
        if plan["format"] != "yaml":
            errors.append("Orchestration.md contract plan.format must be yaml")
        if plan["persistence"] != "ephemeral_untracked":
            errors.append("Orchestration.md contract plan.persistence must be ephemeral_untracked")
        _strings(plan["required_fields"], "plan.required_fields", errors)
    return errors


def _validate_delegation(
    delegation: dict[str, Any],
    data: dict[str, Any],
    roles: set[str],
    state_roles: dict[str, set[str]],
    errors: list[str],
) -> None:
    tasks = _strings(delegation["task_roles"], "delegation.task_roles", errors)
    jurisdictions = delegation["explorer_jurisdictions"]
    if not isinstance(jurisdictions, dict) or not jurisdictions:
        errors.append("Orchestration.md contract explorer_jurisdictions must be a non-empty object")
        return
    explorers = set(jurisdictions)
    _strings(list(jurisdictions.values()), "explorer_jurisdictions values", errors)
    count = delegation["explorers_per_task"]
    if not isinstance(count, int) or isinstance(count, bool) or count < 1:
        errors.append("Orchestration.md contract explorers_per_task must be a positive integer")
    elif len(explorers) != count:
        errors.append("Orchestration.md contract explorer jurisdictions must match explorers_per_task")
    if not tasks <= roles or not explorers <= roles:
        errors.append("Orchestration.md contract delegation references unknown roles")
    if "MAIN" in tasks | explorers or tasks & explorers:
        errors.append("Orchestration.md contract task and explorer roles must be disjoint and exclude MAIN")
    non_delegating = data.get("non_delegating_roles")
    fresh = data.get("fresh_roles")
    read_only = data.get("read_only_roles")
    if not all(isinstance(value, list) and all(isinstance(item, str) for item in value)
               for value in (non_delegating, fresh, read_only)):
        return
    if set(non_delegating) != roles - tasks - {"MAIN"}:
        errors.append("Orchestration.md contract only task roles may delegate below MAIN")
    if not explorers <= set(read_only) & set(fresh) & set(non_delegating):
        errors.append("Orchestration.md contract explorers must be read-only, fresh, and non-delegating")
    if not tasks <= set(fresh):
        errors.append("Orchestration.md contract task roles must be fresh")
    for state, assigned in sorted(state_roles.items()):
        if assigned & explorers:
            errors.append(f"Orchestration.md contract state_roles.{state} must exclude explorer descendants")
