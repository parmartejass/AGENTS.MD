from __future__ import annotations

import os
import re
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.check_governance_core.check_governance_core_main import resolve_documents, run_checks
from scripts.check_governance_core._test_support import install_foundations, live_principles_section, write


FIXTURE_ROOT = Path(__file__).resolve().parent / "fixtures"


def governance_fixture(root: Path, manifest: str) -> None:
    install_foundations(root)
    write(root / "docs/agents/agents_index.md", "# Agents Index\n")
    write(root / "agents-manifest.yaml", manifest)


def valid_manifest(authority: str = "docs/agents/other.md") -> str:
    return (FIXTURE_ROOT / "manifest_valid.yaml").read_text(encoding="utf-8").replace(
        "__AUTHORITY__", authority
    )


class PublicApiContractTests(unittest.TestCase):
    def test_principles_structure_reports_failures_through_governance_only(self) -> None:
        source = live_principles_section()
        block = re.search(
            r"(?ms)^<!-- fundamental-principles:start -->\n.*?^<!-- fundamental-principles:end -->$",
            source,
        )
        assert block is not None
        entries = re.findall(r"(?m)^### FP-[0-9]{2}$", block.group(0))
        declaration = re.search(r"`### FP-([0-9]{2})` through `### FP-([0-9]{2})`", source)
        assert declaration is not None
        cases = {
            "valid": source,
            "valid_blank_lines": source.replace("\n\n", "\n\n\n"),
            "missing_block": source.replace(block.group(0), ""),
            "duplicate_block": source + "\n" + block.group(0),
            "duplicate_start": source + "\n<!-- fundamental-principles:start -->\n",
            "duplicate_end": source + "\n<!-- fundamental-principles:end -->\n",
            "reversed_markers": re.sub(r"(?m)^<!-- fundamental-principles:(start|end) -->$",
                lambda match: "<!-- fundamental-principles:" + ("end" if match.group(1) == "start" else "start") + " -->", source),
            "duplicate_id": source.replace(entries[1] + "\n", entries[0] + "\n"),
            "non_must": source.replace("\nMUST ", "\nSHOULD ", 1),
            "missing_tail": source[:source.rindex(entries[-1])] + "<!-- fundamental-principles:end -->\n",
            "second_paragraph": source.replace("\nMUST ", "\nAdditional paragraph.\n\nMUST ", 1),
            "fenced_block": source.replace(block.group(0), "```md\n" + block.group(0) + "\n```"),
            "fenced_paragraph": source.replace("\nMUST ", "\n```md\nMUST ", 1),
            "missing_declaration": source.replace(declaration.group(0), ""),
            "duplicate_declaration": source.replace(declaration.group(0), declaration.group(0) * 2),
            "reversed_declaration": source.replace(declaration.group(0),
                f"`### FP-{declaration.group(2)}` through `### FP-{declaration.group(1)}`"),
            "wrong_heading": source.replace(entries[0] + "\n", entries[0] + " title\n"),
            "indented_heading": source.replace("\n" + entries[0] + "\n", "\n " + entries[0] + "\n"),
        }
        for name, value in cases.items():
            with self.subTest(name=name), tempfile.TemporaryDirectory() as temp:
                root = Path(temp)
                governance_fixture(root, valid_manifest())
                agents = root / "AGENTS.md"
                write(agents, agents.read_text(encoding="utf-8").replace(source, value))
                request = {"repo_root": str(root), "governance_root": str(root)}
                result = run_checks(request)
                record = next(item for item in result["checks"] if item["id"] == "governance")
                valid = name.startswith("valid")
                self.assertEqual("PASSED" if valid else "FAILED", record["status"], record)
                self.assertFalse(any("unexpectedly" in error for error in record["errors"]), record)
                self.assertEqual(result["planned"], [item["id"] for item in result["checks"]])
                self.assertEqual(sorted(result["planned"]), sorted(result["executed"] + result["failed"]))
                if not valid:
                    self.assertTrue(any("Fundamental Principles" in error for error in record["errors"]), record)
                    self.assertIn("governance", result["failed"])
                resolved = resolve_documents(request)
                self.assertEqual("PASSED", resolved["status"], resolved)
                self.assertEqual(["AGENTS.md", "Orchestration.md"], resolved["documents"])

    def test_principles_expected_range_is_owned_by_agents_and_text_is_not_policy_copied(self) -> None:
        source = live_principles_section()
        entries = re.findall(r"(?m)^### FP-[0-9]{2}$", source)
        declaration = re.search(r"`### FP-[0-9]{2}` through `### FP-[0-9]{2}`", source)
        assert declaration is not None
        changed = source[:source.rindex(entries[-1])] + "<!-- fundamental-principles:end -->\n"
        changed = changed.replace(declaration.group(0), f"`{entries[0]}` through `{entries[-2]}`")
        changed = re.sub(r"(?m)^MUST .+$", "MUST retain this synthetic structural witness.", changed)
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            governance_fixture(root, valid_manifest())
            agents = root / "AGENTS.md"
            write(agents, agents.read_text(encoding="utf-8").replace(source, changed))
            result = run_checks({"repo_root": str(root), "governance_root": str(root)})
            record = next(item for item in result["checks"] if item["id"] == "governance")
            self.assertEqual("PASSED", record["status"], record)

    def test_decision_critical_governance_file_aliases_are_rejected(self) -> None:
        for filename in ("AGENTS.md", "agents-manifest.yaml"):
            with self.subTest(filename=filename), tempfile.TemporaryDirectory() as temp:
                root = Path(temp)
                governance_fixture(root, valid_manifest())
                write(root / "docs/agents/other.md", "owner\n")
                target = root / filename
                source = root / f"{filename}.source"
                target.replace(source)
                os.link(source, target)

                result = run_checks({"repo_root": str(root), "governance_root": str(root)})

                self.assertEqual("FAILED", result["status"], result)
                self.assertTrue(
                    any("must not be an alias" in error for error in result["errors"]),
                    result,
                )




    def test_rejects_unknown_public_request_key(self) -> None:
        result = run_checks({"unexpected": True})
        self.assertEqual("FAILED_VALIDATION", result["status"])
        self.assertIn("unsupported request key", result["errors"][0])

    def test_rejects_invalid_public_request_value_types(self) -> None:
        for request in ({"mode": []}, {"fail_on_safety_warnings": "false"}, {"repo_root": 42}):
            with self.subTest(request=request):
                result = run_checks(request)
                self.assertEqual("FAILED_VALIDATION", result["status"], result)

    def test_handler_exception_preserves_work_universe(self) -> None:
        root = Path(__file__).resolve().parents[2]
        with patch("scripts.check_governance_core._engine.validate_manifest", side_effect=RuntimeError("boom")):
            result = run_checks({"repo_root": str(root), "governance_root": str(root)})
        self.assertEqual("FAILED", result["status"])
        self.assertEqual(
            sorted(result["planned"]),
            sorted([*result["executed"], *result["skipped"], *result["failed"]]),
        )
        self.assertIn("manifest", result["failed"])

    def test_invalid_yaml_is_explicit_failure_not_traceback(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            governance_fixture(
                root,
                (FIXTURE_ROOT / "manifest_invalid_trailing.yaml").read_text(encoding="utf-8"),
            )
            write(root / "docs/agents/other.md", "owner\n")
            result = run_checks({"repo_root": str(root), "governance_root": str(root)})
            self.assertEqual("FAILED", result["status"])
            self.assertTrue(any("invalid double-quoted scalar" in error for error in result["errors"]), result)

    def test_invalid_yaml_colon_space_scalar_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            governance_fixture(root, valid_manifest().replace(
                "update_trigger: routes change",
                "update_trigger: routes: change",
            ))
            write(root / "docs/agents/other.md", "owner\n")
            result = run_checks({"repo_root": str(root), "governance_root": str(root)})
            manifest = next(record for record in result["checks"] if record["id"] == "manifest")
            self.assertEqual("FAILED", manifest["status"], manifest)

    def test_invalid_yaml_colon_tab_scalar_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            governance_fixture(root, valid_manifest().replace("- 'sample'", "- sample:\tevil"))
            write(root / "docs/agents/other.md", "owner\n")
            result = run_checks({"repo_root": str(root), "governance_root": str(root)})
            manifest = next(record for record in result["checks"] if record["id"] == "manifest")
            self.assertEqual("FAILED", manifest["status"], manifest)

    def test_invalid_yaml_mapping_marker_and_single_quote_are_rejected(self) -> None:
        for value in ("sample:", "'a' b 'c'"):
            with self.subTest(value=value), tempfile.TemporaryDirectory() as temp:
                root = Path(temp)
                governance_fixture(root, valid_manifest().replace("'sample'", value))
                write(root / "docs/agents/other.md", "owner\n")
                result = run_checks({"repo_root": str(root), "governance_root": str(root)})
                manifest = next(record for record in result["checks"] if record["id"] == "manifest")
                self.assertEqual("FAILED", manifest["status"], manifest)

    def test_single_quoted_scalars_are_parsed_once_and_accepted(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            governance_fixture(root, valid_manifest())
            write(root / "docs/agents/other.md", "owner\n")
            result = run_checks({"repo_root": str(root), "governance_root": str(root)})
            manifest = next(record for record in result["checks"] if record["id"] == "manifest")
            self.assertEqual("PASSED", manifest["status"], manifest)

    def test_root_authority_aliases_are_rejected_before_filesystem_lookup(self) -> None:
        aliases = (
            "AGENTS.md",
            "Orchestration.md",
            "AGENTS.MD",
            "ORCHESTRATION.MD",
            "Orchestration.md ",
            "Orchestration.md:stream",
        )
        for alias in aliases:
            with self.subTest(alias=alias), tempfile.TemporaryDirectory() as temp:
                root = Path(temp)
                governance_fixture(root, valid_manifest(alias))
                result = run_checks({"repo_root": str(root), "governance_root": str(root)})
                manifest = next(record for record in result["checks"] if record["id"] == "manifest")
                self.assertEqual("FAILED", manifest["status"], manifest)

    def test_non_root_authority_case_alias_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            governance_fixture(root, valid_manifest("DOCS/AGENTS/OTHER.MD"))
            write(root / "docs/agents/other.md", "owner\n")
            result = run_checks({"repo_root": str(root), "governance_root": str(root)})
            manifest = next(record for record in result["checks"] if record["id"] == "manifest")
            self.assertEqual("FAILED", manifest["status"], manifest)

    def test_hard_link_alias_of_root_authority_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            governance_fixture(root, valid_manifest("docs/agents/alias.md"))
            os.link(root / "Orchestration.md", root / "docs/agents/alias.md")
            result = run_checks({"repo_root": str(root), "governance_root": str(root)})
            manifest = next(record for record in result["checks"] if record["id"] == "manifest")
            self.assertEqual("FAILED", manifest["status"], manifest)

    def test_invalid_utf8_returns_explicit_issue(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            governance_fixture(root, valid_manifest())
            write(root / "agents-manifest.yaml", b"\xff\xfe")
            result = run_checks({"repo_root": str(root), "governance_root": str(root)})
            self.assertEqual("FAILED", result["status"])
            self.assertTrue(any("Invalid UTF-8" in error for error in result["errors"]), result)

    def test_document_resolution_rejects_invalid_root_types(self) -> None:
        for request in ({"repo_root": []}, {"governance_root": False}, {"repo_root": ""}):
            with self.subTest(request=request):
                result = resolve_documents(request)
                self.assertEqual("FAILED_VALIDATION", result["status"], result)

    def test_manifest_requires_string_metadata(self) -> None:
        for mutation in (
            ("description: >-\n  frozen success fixture", "description: {}"),
            ("update_trigger: routes change", "update_trigger: []"),
            ("- 'find the owner'", "- ''"),
        ):
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as temp:
                root = Path(temp)
                governance_fixture(root, valid_manifest().replace(*mutation))
                write(root / "docs/agents/other.md", "owner\n")
                result = run_checks({"repo_root": str(root), "governance_root": str(root)})
                manifest = next(record for record in result["checks"] if record["id"] == "manifest")
                self.assertEqual("FAILED", manifest["status"], manifest)




if __name__ == "__main__":
    unittest.main()
