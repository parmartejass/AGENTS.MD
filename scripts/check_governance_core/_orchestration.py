from __future__ import annotations

import json
import re
from typing import Any

from scripts.check_governance_core._orchestration_delegation import validate_delegation_and_plan


_CONTRACT_FENCE = re.compile(r"^[ ]{0,3}(`{3,}|~{3,})([^`]*)$")
_IDENTIFIER = re.compile(r"^[A-Z][A-Z0-9_]*$")
_TOP_LEVEL_FIELDS = {
    "version",
    "roles",
    "read_only_roles",
    "mutable_roles",
    "non_delegating_roles",
    "fresh_roles",
    "states",
    "entry_state",
    "terminal_states",
    "state_roles",
    "transitions",
    "critical_correction",
    "delegation",
    "plan",
}
_TRANSITION_FIELDS = {"from", "to"}
_CORRECTION_FIELDS = {
    "state",
    "final_verification_state",
    "max_uses",
    "allowed_finding_classes",
}
_MAIN_ROLE = "MAIN"
_EXECUTE_STATE = "EXECUTE"


class _DuplicateJsonKey(ValueError):
    pass


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise _DuplicateJsonKey(key)
        result[key] = value
    return result


def _contract_blocks(text: str) -> list[str]:
    blocks: list[str] = []
    active_marker: str | None = None
    active_length = 0
    active_is_contract = False
    active_lines: list[str] = []
    for line in text.splitlines():
        fence = _CONTRACT_FENCE.match(line)
        if active_marker is None:
            if fence is None:
                continue
            marker = fence.group(1)
            active_marker = marker[0]
            active_length = len(marker)
            active_is_contract = fence.group(2).strip() == "orchestration-contract"
            active_lines = []
            continue
        if fence is not None:
            marker = fence.group(1)
            if marker[0] == active_marker and len(marker) >= active_length:
                if active_is_contract:
                    blocks.append("\n".join(active_lines))
                active_marker = None
                active_length = 0
                active_is_contract = False
                active_lines = []
                continue
        if active_is_contract:
            active_lines.append(line)
    return blocks


def _string_list(value: object, label: str, errors: list[str]) -> list[str]:
    if not isinstance(value, list) or any(not isinstance(item, str) or not item for item in value):
        errors.append(f"Orchestration.md contract {label} must be a list of non-empty strings")
        return []
    if len(value) != len(set(value)):
        errors.append(f"Orchestration.md contract {label} must not contain duplicates")
    return value


def _references(values: list[str], allowed: set[str], label: str, errors: list[str]) -> None:
    unknown = sorted(set(values) - allowed)
    if unknown:
        errors.append(f"Orchestration.md contract {label} references unknown values: {', '.join(unknown)}")


def validate_orchestration_contract(text: str) -> list[str]:
    blocks = _contract_blocks(text)
    if len(blocks) != 1:
        return [
            "Orchestration.md must contain exactly one closed orchestration-contract fenced block"
        ]
    try:
        data = json.loads(blocks[0], object_pairs_hook=_unique_object)
    except _DuplicateJsonKey as exc:
        return [f"Orchestration.md contract contains duplicate JSON key: {exc}"]
    except json.JSONDecodeError as exc:
        return [f"Orchestration.md contract contains malformed JSON: line {exc.lineno}: {exc.msg}"]
    if not isinstance(data, dict):
        return ["Orchestration.md contract root must be a JSON object"]
    return _validate_contract(data)


def _validate_contract(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    missing = sorted(_TOP_LEVEL_FIELDS - set(data))
    unknown = sorted(set(data) - _TOP_LEVEL_FIELDS)
    if missing:
        errors.append(f"Orchestration.md contract is missing fields: {', '.join(missing)}")
    if unknown:
        errors.append(f"Orchestration.md contract has unsupported fields: {', '.join(unknown)}")
    version = data.get("version")
    if not isinstance(version, int) or isinstance(version, bool) or version < 1:
        errors.append("Orchestration.md contract version must be a positive integer")

    roles_value = data.get("roles")
    if not isinstance(roles_value, dict) or not roles_value:
        errors.append("Orchestration.md contract roles must be a non-empty object")
        roles: set[str] = set()
    else:
        roles = set(roles_value)
        if any(not _IDENTIFIER.fullmatch(role) for role in roles):
            errors.append("Orchestration.md contract role identifiers must use uppercase snake case")
        if any(not isinstance(description, str) or not description.strip() for description in roles_value.values()):
            errors.append("Orchestration.md contract role descriptions must be non-empty strings")

    read_only = _string_list(data.get("read_only_roles"), "read_only_roles", errors)
    mutable = _string_list(data.get("mutable_roles"), "mutable_roles", errors)
    non_delegating = _string_list(data.get("non_delegating_roles"), "non_delegating_roles", errors)
    fresh = _string_list(data.get("fresh_roles"), "fresh_roles", errors)
    for label, values in (
        ("read_only_roles", read_only),
        ("mutable_roles", mutable),
        ("non_delegating_roles", non_delegating),
        ("fresh_roles", fresh),
    ):
        _references(values, roles, label, errors)
    if set(read_only) & set(mutable):
        errors.append("Orchestration.md contract read-only and mutable role sets must be disjoint")
    if set(read_only) | set(mutable) != roles:
        errors.append("Orchestration.md contract read-only and mutable roles must partition all roles")

    states = _string_list(data.get("states"), "states", errors)
    state_set = set(states)
    if any(not _IDENTIFIER.fullmatch(state) for state in states):
        errors.append("Orchestration.md contract state identifiers must use uppercase snake case")
    entry = data.get("entry_state")
    if not isinstance(entry, str) or entry not in state_set:
        errors.append("Orchestration.md contract entry_state must reference a declared state")
    terminals = _string_list(data.get("terminal_states"), "terminal_states", errors)
    _references(terminals, state_set, "terminal_states", errors)
    if not terminals:
        errors.append("Orchestration.md contract must declare at least one terminal state")

    state_role_sets: dict[str, set[str]] = {}
    state_roles = data.get("state_roles")
    if not isinstance(state_roles, dict):
        errors.append("Orchestration.md contract state_roles must be an object")
    else:
        if set(state_roles) != state_set:
            errors.append("Orchestration.md contract state_roles keys must exactly cover declared states")
        for state, values in state_roles.items():
            assigned = _string_list(values, f"state_roles.{state}", errors)
            _references(assigned, roles, f"state_roles.{state}", errors)
            if not assigned:
                errors.append(f"Orchestration.md contract state_roles.{state} must not be empty")
            if isinstance(state, str) and state in state_set and assigned and set(assigned) <= roles:
                state_role_sets[state] = set(assigned)

    graph = _transition_graph(data.get("transitions"), state_set, errors)
    terminal_set = set(terminals)
    for terminal in terminal_set:
        if graph.get(terminal):
            errors.append(f"Orchestration.md contract terminal state {terminal} must have no outgoing transitions")
    for state in state_set - terminal_set:
        if state in graph and not graph[state]:
            errors.append(f"Orchestration.md contract non-terminal state {state} must have an outgoing transition")
    if isinstance(entry, str) and entry in state_set and set(graph) == state_set:
        reached = _reachable(graph, entry)
        if reached != state_set:
            errors.append(
                "Orchestration.md contract contains unreachable states: "
                + ", ".join(sorted(state_set - reached))
            )
        if _has_cycle(graph, entry):
            errors.append("Orchestration.md contract transition graph must be acyclic")

    _validate_correction(data.get("critical_correction"), state_set, terminal_set, graph, errors)
    _validate_state_role_boundaries(
        state_role_sets,
        set(mutable) & roles,
        data.get("critical_correction"),
        state_set,
        errors,
    )
    errors.extend(validate_delegation_and_plan(data, roles, state_role_sets))
    return errors


def _validate_state_role_boundaries(
    state_roles: dict[str, set[str]],
    mutable_roles: set[str],
    correction: object,
    states: set[str],
    errors: list[str],
) -> None:
    if not state_roles:
        return
    for state in sorted(states):
        assigned = state_roles.get(state)
        if assigned is not None and _MAIN_ROLE not in assigned:
            errors.append(f"Orchestration.md contract state_roles.{state} must include MAIN")

    if not mutable_roles:
        errors.append("Orchestration.md contract mutable_roles must declare at least one mutation owner")
        return
    if _EXECUTE_STATE not in states:
        errors.append("Orchestration.md contract states must include EXECUTE")
        return

    mutation_states = {_EXECUTE_STATE}
    if isinstance(correction, dict):
        correction_state = correction.get("state")
        if isinstance(correction_state, str) and correction_state in states:
            mutation_states.add(correction_state)

    for state, assigned in sorted(state_roles.items()):
        if state in mutation_states:
            missing = sorted(mutable_roles - assigned)
            extra = sorted(assigned - mutable_roles - {_MAIN_ROLE})
            if missing:
                errors.append(
                    f"Orchestration.md contract state_roles.{state} "
                    f"must include mutable role(s): {', '.join(missing)}"
                )
            if extra:
                errors.append(
                    f"Orchestration.md contract state_roles.{state} may include only "
                    f"MAIN and mutable role(s); unexpected role(s): {', '.join(extra)}"
                )
            continue

        mutable_assigned = sorted(assigned & mutable_roles)
        if mutable_assigned:
            errors.append(
                f"Orchestration.md contract state_roles.{state} "
                f"must not include mutable role(s): {', '.join(mutable_assigned)}"
            )


def _transition_graph(value: object, states: set[str], errors: list[str]) -> dict[str, list[str]]:
    if not isinstance(value, list):
        errors.append("Orchestration.md contract transitions must be a list")
        return {}
    graph: dict[str, list[str]] = {}
    for index, transition in enumerate(value):
        if not isinstance(transition, dict) or set(transition) != _TRANSITION_FIELDS:
            errors.append(f"Orchestration.md contract transitions[{index}] must contain only from and to")
            continue
        source = transition.get("from")
        if not isinstance(source, str) or source not in states:
            errors.append(f"Orchestration.md contract transitions[{index}].from references an unknown state")
            continue
        if source in graph:
            errors.append(f"Orchestration.md contract transitions contains duplicate source state: {source}")
            continue
        targets = _string_list(transition.get("to"), f"transitions[{index}].to", errors)
        _references(targets, states, f"transitions[{index}].to", errors)
        graph[source] = targets
    if set(graph) != states:
        errors.append("Orchestration.md contract transitions must exactly cover declared states")
    return graph


def _reachable(graph: dict[str, list[str]], start: str) -> set[str]:
    reached: set[str] = set()
    pending = [start]
    while pending:
        current = pending.pop()
        if current in reached:
            continue
        reached.add(current)
        pending.extend(reversed(graph.get(current, [])))
    return reached


def _has_cycle(graph: dict[str, list[str]], start: str) -> bool:
    visited: set[str] = set()
    active: set[str] = set()

    def visit(state: str) -> bool:
        if state in active:
            return True
        if state in visited:
            return False
        active.add(state)
        if any(visit(target) for target in graph.get(state, [])):
            return True
        active.remove(state)
        visited.add(state)
        return False

    return visit(start)


def _validate_correction(
    value: object,
    states: set[str],
    terminals: set[str],
    graph: dict[str, list[str]],
    errors: list[str],
) -> None:
    if not isinstance(value, dict) or set(value) != _CORRECTION_FIELDS:
        errors.append("Orchestration.md contract critical_correction has invalid fields")
        return
    correction = value.get("state")
    verification = value.get("final_verification_state")
    if not isinstance(correction, str) or correction not in states or correction in terminals:
        errors.append("Orchestration.md contract critical correction state must reference a non-terminal state")
        return
    if not isinstance(verification, str) or verification not in states or verification in terminals:
        errors.append("Orchestration.md contract final verification state must reference a non-terminal state")
        return
    if correction == verification:
        errors.append("Orchestration.md contract correction and final verification states must differ")
    if value.get("max_uses") != 1:
        errors.append("Orchestration.md contract critical correction max_uses must be exactly one")
    classes = _string_list(value.get("allowed_finding_classes"), "allowed_finding_classes", errors)
    if not classes or any(not _IDENTIFIER.fullmatch(item) for item in classes):
        errors.append("Orchestration.md contract allowed finding classes must use uppercase snake case")
    correction_targets = set(graph.get(correction, []))
    if verification not in correction_targets or correction_targets - terminals - {verification}:
        errors.append("Orchestration.md contract correction may transition only to final verification or terminal states")
    if set(graph.get(verification, [])) - terminals or not graph.get(verification):
        errors.append("Orchestration.md contract final verification must transition directly to terminal states")
    correction_sources = {source for source, targets in graph.items() if correction in targets}
    verification_sources = {source for source, targets in graph.items() if verification in targets}
    if len(correction_sources) != 1:
        errors.append("Orchestration.md contract correction state must have exactly one incoming transition")
    if verification_sources != {correction}:
        errors.append("Orchestration.md contract final verification must be reachable only from correction")
