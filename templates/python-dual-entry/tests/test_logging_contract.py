from __future__ import annotations

import json
import logging
import tempfile
import threading
import time
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest import mock

import myapp.logging_config as logging_config
from myapp.config import JobConfig
from myapp.log_contract import validate_event_payload
from myapp.log_redaction import sanitize_for_logging
from myapp.logging_config import setup_logging
from myapp.runner import run_job
from myapp.scenarios import load_scenario


TESTS_DIR = Path(__file__).resolve().parent
SCENARIOS_DIR = TESTS_DIR / "scenarios"
FIXTURES_DIR = TESTS_DIR / "fixtures"
EXPECTED_SEQUENCES = json.loads((FIXTURES_DIR / "logging_expected_sequences.json").read_text(encoding="utf-8"))


def _read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _events_for_run(path: Path, run_id: str) -> list[dict]:
    return [event for event in _read_jsonl(path) if event.get("run_id") == run_id]


class LoggingContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.event_log = Path(self._tmp.name) / "events.jsonl"
        setup_logging(event_log=self.event_log)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_happy_path_emits_full_lifecycle(self) -> None:
        scenario = load_scenario(SCENARIOS_DIR / "scenario_001_happy_path.json")
        if scenario.job.output_path.exists():
            scenario.job.output_path.unlink()

        result = run_job(scenario.job, mode="test")
        self.assertTrue(result.success)
        self.assertTrue(result.run_id)

        events = _events_for_run(self.event_log, result.run_id)
        self.assertGreaterEqual(len(events), 4)
        self.assertEqual(events[0]["event"], "run_start")
        self.assertEqual(events[-1]["event"], "run_end")

        phase_events = [event["phase"] for event in events if event["event"] == "phase_transition"]
        self.assertEqual(phase_events, EXPECTED_SEQUENCES["happy_path_phases"])

        run_end = [event for event in events if event["event"] == "run_end"][0]
        self.assertEqual(run_end["result"], "SUCCESS")

        terminal_item = [event for event in events if event["event"] == "item_terminal"][0]
        self.assertEqual(terminal_item["outcome"], "EXECUTED")
        self.assertEqual(terminal_item["reason_code"], "COMPLETED")

        for event in events:
            source = event.get("source", {})
            self.assertIn("file", source)
            self.assertIn("line", source)
            self.assertIn("function", source)

    def test_validation_failure_emits_failed_validation(self) -> None:
        scenario = load_scenario(SCENARIOS_DIR / "scenario_002_missing_input.json")
        result = run_job(scenario.job, mode="test")
        self.assertFalse(result.success)

        events = _events_for_run(self.event_log, result.run_id)
        phase_events = [event["phase"] for event in events if event["event"] == "phase_transition"]
        self.assertEqual(phase_events, EXPECTED_SEQUENCES["validation_failure_phases"])

        failure_event = [event for event in events if event["event"] == "failure_event"][0]
        self.assertEqual(failure_event["reason_code"], "VALIDATION_FAILED")

        run_end = [event for event in events if event["event"] == "run_end"][0]
        self.assertEqual(run_end["result"], "FAILURE")

    def test_runtime_exception_emits_failure_with_source(self) -> None:
        scenario = load_scenario(SCENARIOS_DIR / "scenario_001_happy_path.json")

        class _BrokenWorkflow:
            def run(self, *_args, **_kwargs):  # noqa: ANN001
                raise RuntimeError("boom")

        with mock.patch("myapp.runner.get_workflow", return_value=_BrokenWorkflow()):
            result = run_job(scenario.job, mode="test")

        self.assertFalse(result.success)
        events = _events_for_run(self.event_log, result.run_id)
        failure_event = [event for event in events if event["event"] == "failure_event"][0]
        self.assertEqual(failure_event["reason_code"], "UNEXPECTED_EXCEPTION")
        self.assertEqual(failure_event["phase"], "FAILED_COMMIT")
        self.assertEqual(failure_event["error"]["type"], "RuntimeError")
        self.assertIn("where", failure_event["error"])

    def test_cancelled_run_emits_partial_success_and_skipped_item(self) -> None:
        scenario = load_scenario(SCENARIOS_DIR / "scenario_001_happy_path.json")
        cancel_event = threading.Event()
        cancel_event.set()

        result = run_job(scenario.job, cancel_event=cancel_event, mode="test")
        self.assertFalse(result.success)
        self.assertEqual(result.status.value, "CANCELLED")

        events = _events_for_run(self.event_log, result.run_id)
        run_end = [event for event in events if event["event"] == "run_end"][0]
        self.assertEqual(run_end["result"], "PARTIAL_SUCCESS")

        terminal_item = [event for event in events if event["event"] == "item_terminal"][0]
        self.assertEqual(terminal_item["outcome"], "SKIPPED")
        self.assertEqual(terminal_item["reason_code"], "CANCELLED")

        phase_events = [event["phase"] for event in events if event["event"] == "phase_transition"]
        self.assertEqual(phase_events, EXPECTED_SEQUENCES["cancelled_phases"])

    def test_logging_sink_failure_is_non_fatal(self) -> None:
        scenario = load_scenario(SCENARIOS_DIR / "scenario_001_happy_path.json")
        if scenario.job.output_path.exists():
            scenario.job.output_path.unlink()

        with tempfile.TemporaryDirectory() as tmp_dir:
            bad_parent = Path(tmp_dir) / "not_a_dir"
            with bad_parent.open("w", encoding="utf-8") as handle:
                handle.write("occupied")
            setup_logging(event_log=bad_parent / "events.jsonl")

            with self.assertLogs("myapp.logging_config", level="WARNING") as captured:
                result = run_job(scenario.job, mode="test")
            self.assertTrue(result.success)
            self.assertEqual(result.status.value, "EXECUTED")
            self.assertTrue(
                any("Event log write failed" in entry for entry in captured.output),
                f"Expected an event sink warning, got: {captured.output}",
            )

    def test_debug_job_config_log_redacts_sensitive_values(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_root = Path(tmp_dir)
            input_path = tmp_root / "in.txt"
            output_path = tmp_root / "out.txt"
            with input_path.open("w", encoding="utf-8", newline="\n") as handle:
                handle.write("line\n")

            config = JobConfig(
                workflow_id="text_transform_v1",
                input_path=input_path,
                output_path=output_path,
                workflow={
                    "api_key": "super-secret-value",
                    "steps": [],
                },
            )

            with self.assertLogs("myapp.runner", level="DEBUG") as captured:
                result = run_job(config, mode="test")

            self.assertTrue(result.success)
            combined = "\n".join(captured.output)
            self.assertIn("Full job config", combined)
            self.assertIn("[REDACTED]", combined)
            self.assertNotIn("super-secret-value", combined)

    def test_sleep_step_cancel_is_interruptible(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_root = Path(tmp_dir)
            input_path = tmp_root / "in.txt"
            output_path = tmp_root / "out.txt"
            with input_path.open("w", encoding="utf-8", newline="\n") as handle:
                handle.write("line\n")

            config = JobConfig(
                workflow_id="text_transform_v1",
                input_path=input_path,
                output_path=output_path,
                workflow={
                    "steps": [
                        {"op": "sleep_ms", "ms": 1000},
                        {"op": "uppercase"},
                    ]
                },
            )

            cancel_event = threading.Event()
            timer = threading.Timer(0.05, cancel_event.set)
            timer.start()
            start = time.perf_counter()
            try:
                result = run_job(config, cancel_event=cancel_event, mode="test")
            finally:
                timer.cancel()
            elapsed = time.perf_counter() - start

            self.assertFalse(result.success)
            self.assertEqual(result.status.value, "CANCELLED")
            self.assertLess(elapsed, 0.8, f"Cancellation took too long: {elapsed:.3f}s")

    def test_run_job_bootstraps_event_logger_without_setup(self) -> None:
        scenario = load_scenario(SCENARIOS_DIR / "scenario_001_happy_path.json")
        if scenario.job.output_path.exists():
            scenario.job.output_path.unlink()

        event_logger = logging.getLogger("myapp.events")
        original_handler = logging_config._EVENT_HANDLER
        original_handlers = list(event_logger.handlers)
        original_level = event_logger.level
        original_propagate = event_logger.propagate

        try:
            logging_config._EVENT_HANDLER = None
            event_logger.handlers.clear()
            event_logger.propagate = False

            result = run_job(scenario.job, mode="test")
            event_path = logging_config.get_event_log_path(result.run_id)
            self.assertTrue(event_path.exists(), f"Expected event log path to exist: {event_path}")
        finally:
            logging_config._EVENT_HANDLER = original_handler
            event_logger.handlers.clear()
            for handler in original_handlers:
                event_logger.addHandler(handler)
            event_logger.setLevel(original_level)
            event_logger.propagate = original_propagate

            if "event_path" in locals() and event_path.exists():
                event_path.unlink()
                parent = event_path.parent
                if parent.exists() and not any(parent.iterdir()):
                    parent.rmdir()
                    grand_parent = parent.parent
                    if grand_parent.exists() and not any(grand_parent.iterdir()):
                        grand_parent.rmdir()

    def test_event_log_path_lookup_is_stable_for_run_id(self) -> None:
        run_id = "stable-run-id"
        original_datetime = logging_config.datetime
        original_handler = logging_config._EVENT_HANDLER
        logging_config._RUN_EVENT_LOG_PATHS.pop(run_id, None)

        class _DayOneDateTime:
            @classmethod
            def now(cls) -> datetime:
                return datetime(2026, 2, 9, 12, 0, 0, tzinfo=timezone.utc)

        class _DayTwoDateTime:
            @classmethod
            def now(cls) -> datetime:
                return datetime(2026, 2, 10, 12, 0, 0, tzinfo=timezone.utc)

        try:
            logging_config._EVENT_HANDLER = None
            logging_config.datetime = _DayOneDateTime
            first = logging_config.get_event_log_path(run_id)
            logging_config.datetime = _DayTwoDateTime
            second = logging_config.get_event_log_path(run_id)
        finally:
            logging_config.datetime = original_datetime
            logging_config._EVENT_HANDLER = original_handler
            logging_config._RUN_EVENT_LOG_PATHS.pop(run_id, None)

        self.assertEqual(first, second)
        self.assertEqual(str(first), "run-logs/20260209/stable-run-id.jsonl")

    def test_redaction_masks_nested_secret_keys(self) -> None:
        payload = {
            "token": "abc123",
            "nested": {
                "api_key": "should-hide",
                "credentials": {"password": "p@ss"},
            },
        }
        sanitized = sanitize_for_logging(payload)
        self.assertEqual(sanitized["token"], "[REDACTED]")
        self.assertEqual(sanitized["nested"]["api_key"], "[REDACTED]")
        self.assertEqual(sanitized["nested"]["credentials"], "[REDACTED]")

    def test_validator_rejects_missing_required_fields(self) -> None:
        with self.assertRaises(ValueError):
            validate_event_payload({"event": "run_start", "run_id": "abc"})

    def test_validator_rejects_run_start_missing_outputs(self) -> None:
        with self.assertRaises(ValueError):
            validate_event_payload(
                {
                    "ts": "2026-02-09T12:00:00+00:00",
                    "event": "run_start",
                    "run_id": "abc",
                    "app": "myapp",
                    "version": "0.1.0",
                    "mode": "test",
                    "inputs": {},
                    "config": {},
                }
            )

    def test_validator_rejects_unknown_reason_code(self) -> None:
        with self.assertRaises(ValueError):
            validate_event_payload(
                {
                    "ts": "2026-02-09T12:00:00+00:00",
                    "event": "failure_event",
                    "run_id": "abc",
                    "phase": "FAILED_COMMIT",
                    "reason_code": "NOT_A_REAL_CODE",
                    "reason_detail": "bad",
                    "error": {},
                }
            )


if __name__ == "__main__":
    unittest.main()
