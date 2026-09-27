from __future__ import annotations

import re
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
    data: dict[str, Any], roles: set[str], state_roles: dict[str, set[str]],
    terminals: set[str], identifier: re.Pattern[str],
) -> list[str]:
    errors: list[str] = []
    tasks: set[str] = set()
    fields: set[str] = set()
    delegation = data.get("delegation")
    if not isinstance(delegation, dict) or set(delegation) != {
        "task_roles", "explorer_jurisdictions", "explorers_per_task"
    }:
        errors.append("Orchestration.md contract delegation has invalid fields")
    else:
        tasks = _validate_delegation(delegation, data, roles, state_roles, errors)
    plan = data.get("plan")
    if not isinstance(plan, dict) or set(plan) != {"format", "persistence", "required_fields"}:
        errors.append("Orchestration.md contract plan has invalid fields")
    else:
        if plan["format"] != "yaml":
            errors.append("Orchestration.md contract plan.format must be yaml")
        if plan["persistence"] != "ephemeral_untracked":
            errors.append("Orchestration.md contract plan.persistence must be ephemeral_untracked")
        fields = _strings(plan["required_fields"], "plan.required_fields", errors)
    excluded_states = set(terminals)
    correction = data.get("critical_correction")
    if isinstance(correction, dict):
        excluded_states.update(
            state for field in ("state", "final_verification_state")
            if isinstance(state := correction.get(field), str)
        )
    normal_state_roles = {state: assigned for state, assigned in state_roles.items() if state not in excluded_states}
    _validate_message_intake(data.get("message_intake"), fields, tasks, normal_state_roles, terminals, identifier, errors)
    return errors


def _validate_delegation(
    delegation: dict[str, Any],
    data: dict[str, Any],
    roles: set[str],
    state_roles: dict[str, set[str]],
    errors: list[str],
) -> set[str]:
    tasks = _strings(delegation["task_roles"], "delegation.task_roles", errors)
    jurisdictions = delegation["explorer_jurisdictions"]
    if not isinstance(jurisdictions, dict) or not jurisdictions:
        errors.append("Orchestration.md contract explorer_jurisdictions must be a non-empty object")
        return tasks
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
        return tasks
    if set(non_delegating) != roles - tasks - {"MAIN"}:
        errors.append("Orchestration.md contract only task roles may delegate below MAIN")
    if not explorers <= set(read_only) & set(fresh) & set(non_delegating):
        errors.append("Orchestration.md contract explorers must be read-only, fresh, and non-delegating")
    if not tasks <= set(fresh):
        errors.append("Orchestration.md contract task roles must be fresh")
    for state, assigned in sorted(state_roles.items()):
        if assigned & explorers:
            errors.append(f"Orchestration.md contract state_roles.{state} must exclude explorer descendants")
    return tasks


def _validate_message_intake(
    value: object,
    plan_fields: set[str],
    tasks: set[str],
    state_roles: dict[str, set[str]],
    terminals: set[str],
    identifier: re.Pattern[str],
    errors: list[str],
) -> None:
    prefix = "Orchestration.md contract message_intake"
    fields = {"trigger", "plan_field", "item_outcomes", "mutation_outcome",
              "no_mutation_outcomes", "failure_outcome", "phase_roles", "dependent_work_barrier",
              "return_after", "failure_terminal"}
    if not isinstance(value, dict) or set(value) != fields:
        errors.append(f"{prefix} has invalid fields")
        return
    if value["trigger"] != "USER_MESSAGE":
        errors.append(f"{prefix}.trigger must be USER_MESSAGE")
    if value["dependent_work_barrier"] is not True:
        errors.append(f"{prefix}.dependent_work_barrier must be true")
    plan_field = value["plan_field"]
    if not isinstance(plan_field, str) or not plan_field or plan_field not in plan_fields:
        errors.append(f"{prefix}.plan_field must reference a required plan field")
    outcomes = _strings(value["item_outcomes"], "message_intake.item_outcomes", errors)
    no_mutation = _strings(value["no_mutation_outcomes"], "message_intake.no_mutation_outcomes", errors)
    if any(not identifier.fullmatch(outcome) for outcome in outcomes):
        errors.append(f"{prefix}.item_outcomes must use uppercase snake case")
    mutation = value["mutation_outcome"]
    failure = value["failure_outcome"]
    if not isinstance(mutation, str) or not isinstance(failure, str):
        errors.append(f"{prefix} mutation and failure outcomes must be strings")
    elif (mutation == failure or {mutation, failure} & no_mutation
          or {mutation, failure} | no_mutation != outcomes):
        errors.append(f"{prefix} outcome categories must partition item_outcomes")
    phases = value["phase_roles"]
    if not isinstance(phases, dict) or not phases:
        errors.append(f"{prefix}.phase_roles must be a non-empty object")
        return
    assigned = _strings(list(phases.values()), "message_intake.phase_roles values", errors)
    if assigned != tasks:
        errors.append(f"{prefix}.phase_roles must cover every task role exactly once")
    for phase, role in phases.items():
        if phase not in state_roles or not isinstance(role, str) or role not in state_roles[phase]:
            errors.append(f"{prefix}.phase_roles must reference declared normal state-role assignments")
    returns = value["return_after"]
    if (not isinstance(returns, dict) or not isinstance(mutation, str) or not isinstance(failure, str)
            or set(returns) != outcomes - {failure} or mutation not in returns or not no_mutation <= set(returns)
            or any(not isinstance(phase, str) or phase not in phases for phase in returns.values())):
        errors.append(f"{prefix}.return_after must link every successful outcome to an intake phase")
    else:
        if phases[returns[mutation]] != "REVIEW_AGENT":
            errors.append(f"{prefix}.return_after mutation outcome must return after the normal review phase")
        if any(phases[returns[outcome]] != "PLAN_REVIEW_AGENT" for outcome in no_mutation):
            errors.append(f"{prefix}.return_after no-mutation outcomes must return after the normal plan-review phase")
    terminal = value["failure_terminal"]
    if terminal != "STOP" or terminal not in terminals:
        errors.append(f"{prefix}.failure_terminal must reference the declared STOP terminal")
