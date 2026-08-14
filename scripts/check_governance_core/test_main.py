import io
import sys
import unittest
from unittest.mock import patch

from scripts.check_governance_core import check_governance_core_main as GOVERNANCE_CORE_MAIN


class GovernanceCoreCliContractTests(unittest.TestCase):
    def _assert_retired_option_rejected(self, option: str) -> None:
        stderr = io.StringIO()
        with patch.object(sys, "stderr", stderr):
            with self.assertRaises(SystemExit) as raised:
                GOVERNANCE_CORE_MAIN.main([option])

        self.assertEqual(2, raised.exception.code)
        self.assertIn(f"unrecognized arguments: {option}", stderr.getvalue())

    def test_retired_runtime_projection_option_is_rejected(self) -> None:
        self._assert_retired_option_rejected("--only-runtime-projection")

    def test_retired_success_marker_option_is_rejected(self) -> None:
        self._assert_retired_option_rejected("--success-marker")


if __name__ == "__main__":
    unittest.main()
