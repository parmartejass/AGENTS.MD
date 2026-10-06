from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from scripts.check_governance_core._test_support import (
    orchestration_contract_errors,
    orchestration_fixture,
    orchestration_payload,
    write_orchestration_payload,
)
from scripts.check_governance_core import resolve_documents


class OrchestrationDelegationContractTests(unittest.TestCase):
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
            ("", "version", 2),
            ("", "version", True),
            ("", "message_intake", None),
            ("message_intake", "unknown", True),
            ("message_intake", "trigger", "AGENT_REPORT"),
            ("message_intake", "dependent_work_barrier", False),
            ("message_intake", "dependent_work_barrier", 1),
            ("message_intake", "plan_field", "missing"),
            ("message_intake", "item_outcomes", ["invalid"]),
            ("message_intake", "item_outcomes", ["HOLD", "HOLD"]),
            ("message_intake", "mutation_outcome", "UNKNOWN"),
            ("message_intake", "failure_outcome", "OWNER_UPDATED"),
            ("message_intake", "no_mutation_outcomes", ["HOLD"]),
            ("message_intake", "phase_roles", {}),
            ("message_intake", "phase_roles", {"UNKNOWN": "PLANNING_AGENT"}),
            ("message_intake", "phase_roles", {"PLAN": "UNKNOWN"}),
            ("message_intake", "phase_roles", {"PLAN": "MAIN"}),
            ("message_intake", "phase_roles", {"PLAN": "PLANNING_AGENT"}),
            ("message_intake", "return_after", {}),
            ("message_intake", "return_after", {"HOLD": "PLAN"}),
            ("message_intake", "failure_terminal", "PLAN"),
            ("message_intake", "failure_terminal", "UNKNOWN"),
        )
        for section, key, replacement in cases:
            with self.subTest(section=section, key=key, replacement=replacement), tempfile.TemporaryDirectory() as temp:
                root = Path(temp)
                orchestration_fixture(root)
                value = orchestration_payload(root)
                (value[section] if section else value)[key] = replacement
                write_orchestration_payload(root, value)
                self.assertTrue(orchestration_contract_errors(root))

        for case in ("failure_terminal", "mutation_return", "no_mutation_return",
                     "correction_phase", "verification_phase"):
            with self.subTest(case=case), tempfile.TemporaryDirectory() as temp:
                root = Path(temp)
                orchestration_fixture(root)
                value = orchestration_payload(root)
                intake = value["message_intake"]
                if case == "failure_terminal":
                    intake["failure_terminal"] = "DONE"
                elif case == "mutation_return":
                    intake["return_after"][intake["mutation_outcome"]] = value["entry_state"]
                elif case == "no_mutation_return":
                    intake["return_after"][intake["no_mutation_outcomes"][0]] = "EXECUTE"
                else:
                    role = "EXECUTION_AGENT" if case == "correction_phase" else "REVIEW_AGENT"
                    normal = next(phase for phase, assigned in intake["phase_roles"].items() if assigned == role)
                    field = "state" if case == "correction_phase" else "final_verification_state"
                    special = value["critical_correction"][field]
                    intake["phase_roles"][special] = intake["phase_roles"].pop(normal)
                    intake["return_after"] = {
                        item: special if phase == normal else phase
                        for item, phase in intake["return_after"].items()
                    }
                write_orchestration_payload(root, value)
                result = resolve_documents({"repo_root": str(root), "governance_root": str(root)})
                self.assertEqual("FAILED", result["status"], result)
                self.assertEqual([], result["documents"])
                self.assertTrue(any("message_intake" in error for error in result["errors"]), result)
                self.assertFalse(any("internal governance" in error for error in result["errors"]), result)

    def test_explorer_and_task_relationships_fail_closed(self) -> None:
        for case in ("mutable", "delegating", "task_non_delegating", "not_fresh",
                     "duplicate_jurisdiction", "empty_jurisdiction", "missing_jurisdiction",
                     "descendant_in_state", "missing_plan", "missing_plan_field",
                     "missing_intake", "missing_intake_plan_field"):
            with self.subTest(case=case), tempfile.TemporaryDirectory() as temp:
                root = Path(temp)
                orchestration_fixture(root)
                value = orchestration_payload(root)
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
                elif case == "missing_intake":
                    del value["message_intake"]
                elif case == "missing_intake_plan_field":
                    value["plan"]["required_fields"].remove(value["message_intake"]["plan_field"])
                else:
                    del value["plan"]["format"]
                write_orchestration_payload(root, value)
                self.assertTrue(orchestration_contract_errors(root))


if __name__ == "__main__":
    unittest.main()
