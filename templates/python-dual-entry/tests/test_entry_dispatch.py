from __future__ import annotations

import unittest
from unittest import mock

from myapp.main import main


class EntryDispatchTests(unittest.TestCase):
    @mock.patch("myapp.main.setup_logging")
    @mock.patch("myapp.main.start_gui")
    def test_no_args_defaults_to_gui(self, start_gui: mock.Mock, setup_logging: mock.Mock) -> None:
        result = main([])

        self.assertEqual(result, 0)
        setup_logging.assert_called_once_with()
        start_gui.assert_called_once()

    @mock.patch("myapp.main._run_cli", return_value=7)
    def test_help_routes_to_cli(self, run_cli: mock.Mock) -> None:
        result = main(["--help"])

        self.assertEqual(result, 7)
        run_cli.assert_called_once_with(["--help"])

    @mock.patch("myapp.main._run_cli", return_value=8)
    def test_version_routes_to_cli(self, run_cli: mock.Mock) -> None:
        result = main(["--version"])

        self.assertEqual(result, 8)
        run_cli.assert_called_once_with(["--version"])

    @mock.patch("myapp.main._run_cli", return_value=9)
    def test_scenario_verify_routes_to_cli(self, run_cli: mock.Mock) -> None:
        argv = ["--scenario", "tests/scenarios/scenario_001_happy_path.json", "--verify"]
        result = main(argv)

        self.assertEqual(result, 9)
        run_cli.assert_called_once_with(argv)

    @mock.patch("myapp.main._run_cli", return_value=10)
    def test_unknown_flag_routes_to_cli(self, run_cli: mock.Mock) -> None:
        result = main(["--unknown"])

        self.assertEqual(result, 10)
        run_cli.assert_called_once_with(["--unknown"])

    @mock.patch("myapp.main._run_cli", return_value=11)
    def test_equals_style_scenario_flag_routes_to_cli(self, run_cli: mock.Mock) -> None:
        argv = ["--scenario=tests/scenarios/scenario_001_happy_path.json"]
        result = main(argv)

        self.assertEqual(result, 11)
        run_cli.assert_called_once_with(argv)

    @mock.patch("myapp.main.setup_logging")
    @mock.patch("myapp.main.start_gui")
    def test_positional_arg_keeps_gui_default(self, start_gui: mock.Mock, setup_logging: mock.Mock) -> None:
        result = main(["notes.txt"])

        self.assertEqual(result, 0)
        setup_logging.assert_called_once_with()
        start_gui.assert_called_once()

    @mock.patch("myapp.main.setup_logging")
    @mock.patch("myapp.main.start_gui", side_effect=RuntimeError("boom"))
    def test_gui_startup_failure_returns_nonzero(self, _start_gui: mock.Mock, setup_logging: mock.Mock) -> None:
        result = main([])

        self.assertEqual(result, 1)
        setup_logging.assert_called_once_with()


if __name__ == "__main__":
    unittest.main()
