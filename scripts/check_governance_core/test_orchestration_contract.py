from __future__ import annotations

import os
import re
import tempfile
import unittest
from pathlib import Path
from typing import Callable

from scripts.check_governance_core._documents import DocumentStore
from scripts.check_governance_core._governance_checks import resolve_governance_contract
from scripts.check_governance_core._inventory import RepositoryInventory
from scripts.check_governance_core._test_support import (
    REPOSITORY_ROOT,
    orchestration_contract_block,
    orchestration_contract_errors,
    orchestration_fixture,
    orchestration_payload,
    write,
    write_orchestration_payload,
)
from scripts.check_governance_core import resolve_documents


class OrchestrationContractTests(unittest.TestCase):
    def test_live_contract_is_structurally_valid(self) -> None:
        root = REPOSITORY_ROOT
        contract = resolve_governance_contract(root, DocumentStore(), RepositoryInventory(root))
        self.assertEqual((), contract.errors, contract)
        self.assertEqual(("AGENTS.md", "Orchestration.md"), contract.root_authorities)
        result = resolve_documents({"repo_root": str(root), "governance_root": str(root)})
        self.assertEqual("PASSED", result["status"], result)
        self.assertEqual(list(contract.root_authorities), result["documents"][:2])
        self.assertEqual([], result["errors"])
        with tempfile.TemporaryDirectory() as temp:
            fixture = Path(temp)
            orchestration_fixture(fixture)
            value = orchestration_payload(fixture)
            intake = value["message_intake"]
            renamed = {outcome: f"RENAMED_{outcome}" for outcome in intake["item_outcomes"]}
            intake["item_outcomes"] = list(renamed.values())
            for category in ("mutation_outcome", "failure_outcome"):
                intake[category] = renamed[intake[category]]
            intake["no_mutation_outcomes"] = [renamed[item] for item in intake["no_mutation_outcomes"]]
            intake["return_after"] = {renamed[item]: phase for item, phase in intake["return_after"].items()}
            value["plan"]["required_fields"].remove(intake["plan_field"])
            intake["plan_field"] += "_renamed"
            value["plan"]["required_fields"].append(intake["plan_field"])
            write_orchestration_payload(fixture, value)
            result = resolve_documents({"repo_root": str(fixture), "governance_root": str(fixture)})
            self.assertEqual("PASSED", result["status"], result)
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
                orchestration_fixture(root)
                mutate(root)
                self.assertTrue(orchestration_contract_errors(root))
                result = resolve_documents(
                    {"repo_root": str(root), "governance_root": str(root)}
                )
                self.assertEqual("FAILED", result["status"], result)
                self.assertEqual([], result["documents"])

    def test_orchestration_file_alias_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            orchestration_fixture(root)
            target = root / "Orchestration.md"
            source = root / "Orchestration.source.md"
            target.replace(source)
            try:
                os.link(source, target)
            except OSError as exc:
                self.skipTest(f"hard links unavailable: {exc}")
            self.assertTrue(any("alias" in error for error in orchestration_contract_errors(root)))
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
            match = orchestration_contract_block(root)
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
                orchestration_fixture(root)
                mutate(root)
                self.assertTrue(orchestration_contract_errors(root))
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
                orchestration_fixture(root)
                value = orchestration_payload(root)
                mutate(value)
                write_orchestration_payload(root, value)
                self.assertTrue(orchestration_contract_errors(root))

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
                orchestration_fixture(root)
                value = orchestration_payload(root)
                mutate(value)
                write_orchestration_payload(root, value)
                errors = orchestration_contract_errors(root)
                self.assertTrue(
                    any(expected in error for error in errors),
                    f"{expected!r} not found in {errors!r}",
                )


if __name__ == "__main__":
    unittest.main()
