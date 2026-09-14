from __future__ import annotations

import json
import os
import re
import tempfile
import unittest
from pathlib import Path
from typing import Callable

from scripts.check_governance_core._documents import DocumentStore
from scripts.check_governance_core._governance_checks import resolve_governance_contract
from scripts.check_governance_core._inventory import RepositoryInventory
from scripts.check_governance_core._test_support import install_root_authorities, write
from scripts.check_governance_core.check_governance_core_main import resolve_documents


_BLOCK = re.compile(
    r"(?ms)^```orchestration-contract\s*$\n(?P<body>.*?)^```\s*$"
)


def _fixture(root: Path) -> None:
    install_root_authorities(root)
    write(root / "docs/agents/agents_index.md", "# Agents\n")


def _payload(root: Path) -> dict[str, object]:
    text = (root / "Orchestration.md").read_text(encoding="utf-8")
    match = _BLOCK.search(text)
    assert match is not None
    value = json.loads(match.group("body"))
    assert isinstance(value, dict)
    return value


def _write_payload(root: Path, value: dict[str, object]) -> None:
    path = root / "Orchestration.md"
    text = path.read_text(encoding="utf-8")
    rendered = "```orchestration-contract\n" + json.dumps(value, indent=2) + "\n```"
    write(path, _BLOCK.sub(rendered, text, count=1))


def _contract_errors(root: Path) -> tuple[str, ...]:
    return resolve_governance_contract(
        root,
        DocumentStore(),
        RepositoryInventory(root),
    ).errors


class OrchestrationContractTests(unittest.TestCase):
    def test_live_contract_is_structurally_valid(self) -> None:
        root = Path(__file__).resolve().parents[2]
        contract = resolve_governance_contract(root, DocumentStore(), RepositoryInventory(root))
        self.assertEqual((), contract.errors, contract)
        self.assertEqual(("AGENTS.md", "Orchestration.md"), contract.root_authorities)
        result = resolve_documents({"repo_root": str(root), "governance_root": str(root)})
        self.assertEqual("PASSED", result["status"], result)
        self.assertEqual(list(contract.root_authorities), result["documents"][:2])
        self.assertEqual([], result["errors"])

    def test_missing_wrong_case_and_duplicate_authority_routes_fail(self) -> None:
        def missing(root: Path) -> None:
            (root / "Orchestration.md").unlink()

        def wrong_case(root: Path) -> None:
            (root / "Orchestration.md").rename(root / "orchestration.md")

        def duplicate(root: Path) -> None:
            agents = root / "AGENTS.md"
            write(
                agents,
                agents.read_text(encoding="utf-8")
                + "\n<!-- orchestration-authority: Orchestration.md -->\n",
            )

        def wrong_route(root: Path) -> None:
            agents = root / "AGENTS.md"
            write(
                agents,
                agents.read_text(encoding="utf-8").replace(
                    "orchestration-authority: Orchestration.md",
                    "orchestration-authority: orchestration.md",
                ),
            )

        for name, mutate in (
            ("missing", missing),
            ("wrong_case", wrong_case),
            ("duplicate", duplicate),
            ("wrong_route", wrong_route),
        ):
            with self.subTest(name=name), tempfile.TemporaryDirectory() as temp:
                root = Path(temp)
                _fixture(root)
                mutate(root)
                self.assertTrue(_contract_errors(root))
                result = resolve_documents(
                    {"repo_root": str(root), "governance_root": str(root)}
                )
                self.assertEqual("FAILED", result["status"], result)
                self.assertEqual([], result["documents"])

    def test_orchestration_file_alias_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            _fixture(root)
            target = root / "Orchestration.md"
            source = root / "Orchestration.source.md"
            target.replace(source)
            try:
                os.link(source, target)
            except OSError as exc:
                self.skipTest(f"hard links unavailable: {exc}")
            self.assertTrue(any("alias" in error for error in _contract_errors(root)))
            result = resolve_documents(
                {"repo_root": str(root), "governance_root": str(root)}
            )
            self.assertEqual("FAILED", result["status"], result)
            self.assertEqual([], result["documents"])

    def test_malformed_duplicate_and_duplicate_key_contracts_fail(self) -> None:
        def malformed(root: Path) -> None:
            path = root / "Orchestration.md"
            original = path.read_text(encoding="utf-8")
            changed, count = re.subn(r'"version":\s*\d+,', '"version": ,', original, count=1)
            self.assertEqual(1, count)
            self.assertNotEqual(original, changed)
            write(path, changed)

        def duplicate_block(root: Path) -> None:
            path = root / "Orchestration.md"
            match = _BLOCK.search(path.read_text(encoding="utf-8"))
            assert match is not None
            write(path, path.read_text(encoding="utf-8") + "\n" + match.group(0) + "\n")

        def duplicate_key(root: Path) -> None:
            path = root / "Orchestration.md"
            original = path.read_text(encoding="utf-8")
            changed, count = re.subn(
                r'"version":\s*\d+,', lambda match: match.group(0) * 2,
                original, count=1,
            )
            self.assertEqual(1, count)
            self.assertNotEqual(original, changed)
            write(path, changed)

        for name, mutate in (
            ("malformed", malformed),
            ("duplicate_block", duplicate_block),
            ("duplicate_key", duplicate_key),
        ):
            with self.subTest(name=name), tempfile.TemporaryDirectory() as temp:
                root = Path(temp)
                _fixture(root)
                mutate(root)
                self.assertTrue(_contract_errors(root))
                result = resolve_documents(
                    {"repo_root": str(root), "governance_root": str(root)}
                )
                self.assertEqual("FAILED", result["status"], result)
                self.assertEqual([], result["documents"])

    def test_invalid_role_state_graph_and_correction_contracts_fail(self) -> None:
        Mutation = Callable[[dict[str, object]], None]

        def invalid_role(value: dict[str, object]) -> None:
            state_roles = value["state_roles"]
            assert isinstance(state_roles, dict)
            first = next(iter(state_roles))
            state_roles[first] = ["UNKNOWN_ROLE"]

        def invalid_state(value: dict[str, object]) -> None:
            transitions = value["transitions"]
            assert isinstance(transitions, list) and isinstance(transitions[0], dict)
            transitions[0]["to"] = ["UNKNOWN_STATE"]

        def duplicate_state(value: dict[str, object]) -> None:
            states = value["states"]
            assert isinstance(states, list)
            states.append(states[0])

        def terminal_outgoing(value: dict[str, object]) -> None:
            transitions = value["transitions"]
            terminals = value["terminal_states"]
            entry = value["entry_state"]
            assert isinstance(transitions, list) and isinstance(terminals, list)
            for transition in transitions:
                if isinstance(transition, dict) and transition.get("from") == terminals[0]:
                    transition["to"] = [entry]

        def invalid_partition(value: dict[str, object]) -> None:
            mutable = value["mutable_roles"]
            read_only = value["read_only_roles"]
            assert isinstance(mutable, list) and isinstance(read_only, list)
            read_only.append(mutable[0])

        def second_correction(value: dict[str, object]) -> None:
            correction = value["critical_correction"]
            assert isinstance(correction, dict)
            correction["max_uses"] = 2

        def parallel_verification_route(value: dict[str, object]) -> None:
            transitions = value["transitions"]
            correction = value["critical_correction"]
            assert isinstance(transitions, list) and isinstance(correction, dict)
            verification = correction["final_verification_state"]
            first = transitions[0]
            assert isinstance(first, dict) and isinstance(first["to"], list)
            first["to"].append(verification)

        def cyclic_flow(value: dict[str, object]) -> None:
            transitions = value["transitions"]
            correction = value["critical_correction"]
            entry = value["entry_state"]
            assert isinstance(transitions, list) and isinstance(correction, dict)
            verification = correction["final_verification_state"]
            for transition in transitions:
                if isinstance(transition, dict) and transition.get("from") == verification:
                    transition["to"] = [entry]

        mutations: tuple[tuple[str, Mutation], ...] = (
            ("invalid_role", invalid_role),
            ("invalid_state", invalid_state),
            ("duplicate_state", duplicate_state),
            ("terminal_outgoing", terminal_outgoing),
            ("invalid_partition", invalid_partition),
            ("second_correction", second_correction),
            ("parallel_verification_route", parallel_verification_route),
            ("cyclic_flow", cyclic_flow),
        )
        for name, mutate in mutations:
            with self.subTest(name=name), tempfile.TemporaryDirectory() as temp:
                root = Path(temp)
                _fixture(root)
                value = _payload(root)
                mutate(value)
                _write_payload(root, value)
                self.assertTrue(_contract_errors(root))

    def test_role_boundary_semantic_drifts_fail(self) -> None:
        Mutation = Callable[[dict[str, object]], None]

        def roles_for(value: dict[str, object], state: str) -> list[str]:
            state_roles = value["state_roles"]
            assert isinstance(state_roles, dict)
            roles = state_roles[state]
            assert isinstance(roles, list)
            return roles

        def execution_in_final_review(value: dict[str, object]) -> None:
            roles_for(value, "FINAL_REVIEW").append("EXECUTION_AGENT")

        def execution_removed_from_execute(value: dict[str, object]) -> None:
            roles_for(value, "EXECUTE").remove("EXECUTION_AGENT")

        def main_removed_from_plan(value: dict[str, object]) -> None:
            roles_for(value, "PLAN").remove("MAIN")

        def governance_in_execute(value: dict[str, object]) -> None:
            roles_for(value, "EXECUTE").append("GOVERNANCE_AGENT")

        def execution_removed_from_correction(value: dict[str, object]) -> None:
            roles_for(value, "CRITICAL_CORRECTION").remove("EXECUTION_AGENT")

        cases: tuple[tuple[str, Mutation, str], ...] = (
            (
                "execution_in_final_review",
                execution_in_final_review,
                "state_roles.FINAL_REVIEW must not include mutable role(s): EXECUTION_AGENT",
            ),
            (
                "execution_removed_from_execute",
                execution_removed_from_execute,
                "state_roles.EXECUTE must include mutable role(s): EXECUTION_AGENT",
            ),
            (
                "main_removed_from_plan",
                main_removed_from_plan,
                "state_roles.PLAN must include MAIN",
            ),
            (
                "governance_in_execute",
                governance_in_execute,
                "state_roles.EXECUTE may include only MAIN and mutable role(s); "
                "unexpected role(s): GOVERNANCE_AGENT",
            ),
            (
                "execution_removed_from_correction",
                execution_removed_from_correction,
                "state_roles.CRITICAL_CORRECTION must include mutable role(s): EXECUTION_AGENT",
            ),
        )
        for name, mutate, expected in cases:
            with self.subTest(name=name), tempfile.TemporaryDirectory() as temp:
                root = Path(temp)
                _fixture(root)
                value = _payload(root)
                mutate(value)
                _write_payload(root, value)
                errors = _contract_errors(root)
                self.assertTrue(
                    any(expected in error for error in errors),
                    f"{expected!r} not found in {errors!r}",
                )

    def test_delegation_and_yaml_plan_fail_closed(self) -> None:
        cases = (
            ("delegation", "task_roles", ["UNKNOWN"]),
            ("delegation", "task_roles", ["MAIN"]),
            ("delegation", "task_roles", ["GOVERNANCE_AGENT"]),
            ("delegation", "task_roles", ["PLANNING_AGENT", "PLANNING_AGENT"]),
            ("delegation", "explorer_jurisdictions", {"UNKNOWN": "unknown"}),
            ("delegation", "explorer_jurisdictions", {}),
            ("delegation", "explorer_jurisdictions", {"GOVERNANCE_AGENT": "governance"}),
            ("delegation", "explorers_per_task", 0),
            ("delegation", "explorers_per_task", True),
            ("delegation", "explorers_per_task", "3"),
            ("delegation", "unknown", True),
            ("plan", "format", "markdown"),
            ("plan", "persistence", "tracked"),
            ("plan", "required_fields", []),
            ("plan", "required_fields", ["goal", "goal"]),
            ("plan", "required_fields", [""]),
            ("plan", "unknown", True),
        )
        for section, key, replacement in cases:
            with self.subTest(section=section, key=key, replacement=replacement), tempfile.TemporaryDirectory() as temp:
                root = Path(temp)
                _fixture(root)
                value = _payload(root)
                value[section][key] = replacement
                _write_payload(root, value)
                self.assertTrue(_contract_errors(root))

    def test_explorer_and_task_relationships_fail_closed(self) -> None:
        for case in ("mutable", "delegating", "task_non_delegating", "not_fresh",
                     "duplicate_jurisdiction", "empty_jurisdiction", "missing_jurisdiction",
                     "descendant_in_state", "missing_plan", "missing_plan_field"):
            with self.subTest(case=case), tempfile.TemporaryDirectory() as temp:
                root = Path(temp)
                _fixture(root)
                value = _payload(root)
                explorers = value["delegation"]["explorer_jurisdictions"]
                child = next(iter(explorers))
                if case == "mutable":
                    value["read_only_roles"].remove(child)
                    value["mutable_roles"].append(child)
                elif case == "delegating":
                    value["non_delegating_roles"].remove(child)
                elif case == "task_non_delegating":
                    value["non_delegating_roles"].append(value["delegation"]["task_roles"][0])
                elif case == "not_fresh":
                    value["fresh_roles"].remove(child)
                elif case == "duplicate_jurisdiction":
                    explorers[child] = list(explorers.values())[1]
                elif case == "empty_jurisdiction":
                    explorers[child] = ""
                elif case == "missing_jurisdiction":
                    del explorers[child]
                elif case == "descendant_in_state":
                    value["state_roles"]["PLAN"].append(child)
                elif case == "missing_plan":
                    del value["plan"]
                else:
                    del value["plan"]["format"]
                _write_payload(root, value)
                self.assertTrue(_contract_errors(root))

if __name__ == "__main__":
    unittest.main()
