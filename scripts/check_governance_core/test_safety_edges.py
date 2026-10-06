from __future__ import annotations

import ast
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.check_governance_core._test_support import REPOSITORY_ROOT, write as _write
from scripts.check_governance_core._documents import DocumentStore
from scripts.check_governance_core._inventory import RepositoryInventory
from scripts.check_governance_core._python_safety import check_python_safety
from scripts.check_governance_core import run_checks


class PythonSafetyEdgeTests(unittest.TestCase):
    def test_silent_broad_handler_control_flow_is_an_error(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            _write(
                root / "silent.py",
                "def continue_case():\n"
                "    for _item in (1,):\n"
                "        try:\n"
                "            raise RuntimeError()\n"
                "        except Exception:\n"
                "            continue\n"
                "def break_case():\n"
                "    for _item in (1,):\n"
                "        try:\n"
                "            raise RuntimeError()\n"
                "        except BaseException:\n"
                "            break\n"
                "def ellipsis_case():\n"
                "    try:\n"
                "        raise RuntimeError()\n"
                "    except Exception:\n"
                "        ...\n",
            )
            errors, warnings = check_python_safety(
                root,
                RepositoryInventory(root),
                DocumentStore(),
                fail_on_warnings=False,
            )

        self.assertEqual([], warnings)
        self.assertEqual(3, sum("SILENT_EXCEPT" in error for error in errors), errors)

    def test_empty_collection_sentinels_are_warnings(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            _write(
                root / "sentinels.py",
                "def list_case():\n"
                "    try:\n"
                "        raise RuntimeError()\n"
                "    except Exception:\n"
                "        return []\n"
                "def dict_case():\n"
                "    try:\n"
                "        raise RuntimeError()\n"
                "    except BaseException:\n"
                "        return {}\n"
                "def set_case():\n"
                "    try:\n"
                "        raise RuntimeError()\n"
                "    except Exception:\n"
                "        return set()\n",
            )
            errors, warnings = check_python_safety(
                root,
                RepositoryInventory(root),
                DocumentStore(),
                fail_on_warnings=False,
            )

        self.assertEqual([], errors)
        self.assertEqual(3, sum("EXCEPT_RETURN_LITERAL" in warning for warning in warnings), warnings)

    def test_logged_and_raised_broad_handler_is_allowed(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            _write(
                root / "explicit.py",
                "import logging\n"
                "logger = logging.getLogger(__name__)\n"
                "def explicit():\n"
                "    try:\n"
                "        raise RuntimeError()\n"
                "    except Exception:\n"
                "        logger.exception('failed')\n"
                "        raise\n",
            )
            errors, warnings = check_python_safety(
                root,
                RepositoryInventory(root),
                DocumentStore(),
                fail_on_warnings=False,
            )

        self.assertEqual([], errors)
        self.assertEqual([], warnings)



class SharedPythonParseTests(unittest.TestCase):
    def test_import_index_matches_a_full_walk(self) -> None:
        nested = (
            "import a\ndef f():\n    import b\n    try:\n        import c\n    except E:\n        import d\n"
            "    else:\n        import e\n    finally:\n        from . import g\n    match x:\n        case 1:\n"
            "            import h\n    class K:\n        import i\n    with w:\n        import j\nimport k\n"
        )
        files, inventory_error = RepositoryInventory(REPOSITORY_ROOT).python_files(REPOSITORY_ROOT)
        self.assertIsNone(inventory_error)
        sources = {"nested": nested, **{
            path.relative_to(REPOSITORY_ROOT).as_posix(): path.read_text(encoding="utf-8") for path in files
        }}
        store = DocumentStore()
        for name, text in sources.items():
            with self.subTest(source=name):
                module, error = store.python_module(REPOSITORY_ROOT / name, text)
                self.assertIsNone(error)
                expected = [node for node in ast.walk(module.tree) if isinstance(node, (ast.Import, ast.ImportFrom))]
                self.assertEqual(expected, list(module.imports))

    def test_full_run_parses_each_python_source_once(self) -> None:
        parsed: list[str] = []
        original = ast.parse

        def counted(source, filename="<unknown>", *args, **kwargs):
            parsed.append(filename)
            return original(source, filename, *args, **kwargs)

        with patch.object(ast, "parse", counted):
            result = run_checks({})
        # Both parse consumers must run; their pass/fail status belongs to other tests (deletion-safe).
        ran = {record["id"] for record in result.get("checks", [])}
        self.assertLessEqual({"folder_architecture", "python_safety"}, ran, result)
        self.assertTrue(parsed)
        self.assertEqual(len(parsed), len(set(parsed)), sorted(parsed))


if __name__ == "__main__":
    unittest.main()
