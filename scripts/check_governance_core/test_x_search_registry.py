from __future__ import annotations

import os
import sys
import unittest
from pathlib import Path
from types import ModuleType
from unittest.mock import Mock, patch


SOURCE = Path(__file__).resolve().parents[2] / "X-Bookmarks Import/skills/x-research/scripts/x_search.py"


class UsageError(ValueError):
    pass


def isolated_cli():
    runtime = ModuleType("x_runtime")
    runtime.UsageError = UsageError
    for name in (
        "configure_logging", "load_env", "parse_int_arg", "parse_retry_delay_seconds",
        "summarize_payload", "write_json_stdout", "write_stdout_line",
    ):
        setattr(runtime, name, Mock())
    runtime.request_json = Mock(side_effect=AssertionError("network must remain isolated"))
    namespace = {"__file__": str(SOURCE), "__name__": "isolated_x_search"}
    original_path = sys.path[:]
    try:
        with patch.dict(sys.modules, {"x_runtime": runtime}), patch.dict(os.environ, {"X_BEARER_TOKEN": "test-token"}, clear=True):
            exec(compile(SOURCE.read_bytes(), str(SOURCE), "exec"), namespace)
    finally:
        sys.path[:] = original_path
    namespace["search"] = Mock(return_value=([{"id": "synthetic"}], {}, {}, {}))
    namespace["enrich"] = Mock(return_value=[{"id": "synthetic", "_score": 0}])
    return namespace, runtime


class XSearchRegistryTests(unittest.TestCase):
    def test_default_and_each_registered_mode_dispatch_through_the_cli(self) -> None:
        cli, runtime = isolated_cli()
        self.assertEqual(["full", "compact", "json"], list(cli["EMITTERS"]))
        for mode in cli["EMITTERS"]:
            self.assertIs(cli[f"emit_{mode}"], cli["EMITTERS"][mode])
        for flag, expected in (([], "full"), (["--emit=full"], "full"), (["--emit=compact"], "compact"), (["--emit=json"], "json")):
            with self.subTest(flag=flag):
                handlers = {mode: Mock() for mode in cli["EMITTERS"]}
                with patch.dict(cli["EMITTERS"], handlers), patch.object(sys, "argv", [str(SOURCE), "topic", *flag]):
                    cli["main"]()
                handlers[expected].assert_called_once_with([{"id": "synthetic", "_score": 0}], "topic", 7)
                self.assertTrue(all(not handler.called for mode, handler in handlers.items() if mode != expected))
        runtime.request_json.assert_not_called()

    def test_help_and_invalid_modes_preserve_exact_cli_strings(self) -> None:
        cli, runtime = isolated_cli()
        usage = 'Usage: python3 x_search.py "topic" [--days=7] [--limit=100] [--no-retweets] [--lang=en] [--emit=full|compact|json]'
        with patch.object(sys, "argv", [str(SOURCE), "--help"]):
            cli["main"]()
        runtime.write_stdout_line.assert_called_once_with(usage)
        for args, message in ((["topic", "--emit=other"], "--emit must be one of: full, compact, json."), (["--emit=full"], usage)):
            with self.subTest(args=args), patch.object(sys, "argv", [str(SOURCE), *args]):
                with self.assertRaises(UsageError) as caught:
                    cli["main"]()
                self.assertEqual(message, str(caught.exception))
        cli["search"].assert_not_called()
        runtime.request_json.assert_not_called()

    def test_registered_extension_reaches_parser_help_error_and_dispatch(self) -> None:
        cli, runtime = isolated_cli()
        extension = Mock()
        cli["EMITTERS"]["synthetic"] = extension
        with patch.object(sys, "argv", [str(SOURCE), "topic", "--emit=synthetic"]):
            cli["main"]()
        extension.assert_called_once_with([{"id": "synthetic", "_score": 0}], "topic", 7)
        cli["write_usage"]()
        self.assertIn("[--emit=full|compact|json|synthetic]", runtime.write_stdout_line.call_args.args[0])
        with patch.object(sys, "argv", [str(SOURCE), "topic", "--emit=other"]):
            with self.assertRaises(UsageError) as caught:
                cli["parse_args"]()
        self.assertEqual("--emit must be one of: full, compact, json, synthetic.", str(caught.exception))
        runtime.request_json.assert_not_called()


if __name__ == "__main__":
    unittest.main()
