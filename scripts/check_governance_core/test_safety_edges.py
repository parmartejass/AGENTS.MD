from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from scripts.check_governance_core._inventory import RepositoryInventory
from scripts.check_governance_core._python_safety import check_python_safety


def _write(path: Path, value: str) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        handle.write(value)


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
                fail_on_warnings=False,
            )

        self.assertEqual([], errors)
        self.assertEqual([], warnings)


if __name__ == "__main__":
    unittest.main()
