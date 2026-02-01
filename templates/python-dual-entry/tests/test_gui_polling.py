from __future__ import annotations

import json
import queue
import random
import unittest
from collections.abc import Sequence
from pathlib import Path
from typing import Generic, TypeVar

from myapp.gui_app import UiResult, _poll_queue_once


FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"
RACE_FIXTURE = FIXTURES_DIR / "gui_poll_race_sequence.json"
_EMPTY: object = object()

_T = TypeVar("_T")


class SequenceQueue(Generic[_T]):
    """Test double for queue.Queue that returns items from a predefined sequence."""

    def __init__(self, sequence: Sequence[_T | object]) -> None:
        self._sequence: list[_T | object] = list(sequence)

    def get_nowait(self) -> _T:
        if not self._sequence:
            raise queue.Empty
        token = self._sequence.pop(0)
        if token is _EMPTY:
            raise queue.Empty
        return token  # type: ignore[return-value]


class StubWorker:
    """Test double for threading.Thread that reports a fixed alive state."""

    def __init__(self, alive: bool) -> None:
        self._alive = alive

    def is_alive(self) -> bool:
        return self._alive


class GuiPollQueueTests(unittest.TestCase):
    def test_returns_result_when_queue_has_item(self):
        result = UiResult(scenario_id="happy", success=True, message="done")
        q = SequenceQueue([result])
        worker = StubWorker(alive=True)

        ui_result, should_reschedule = _poll_queue_once(q, worker)

        self.assertEqual(ui_result, result)
        self.assertFalse(should_reschedule)

    def test_reschedules_when_no_result_and_worker_alive(self):
        q = SequenceQueue([])
        worker = StubWorker(alive=True)

        ui_result, should_reschedule = _poll_queue_once(q, worker)

        self.assertIsNone(ui_result)
        self.assertTrue(should_reschedule)

    def test_catches_late_enqueue_after_worker_exit(self):
        fixture_data = json.loads(RACE_FIXTURE.read_text(encoding="utf-8"))
        result = UiResult(scenario_id="race", success=True, message="done")
        sequence = [result if token == "RESULT" else _EMPTY for token in fixture_data["sequence"]]
        q = SequenceQueue(sequence)
        worker = StubWorker(alive=False)

        ui_result, should_reschedule = _poll_queue_once(q, worker)

        self.assertEqual(ui_result, result)
        self.assertFalse(should_reschedule)

    def test_no_reschedule_when_worker_dead_and_queue_empty(self):
        q = SequenceQueue([])
        worker = StubWorker(alive=False)

        ui_result, should_reschedule = _poll_queue_once(q, worker)

        self.assertIsNone(ui_result)
        self.assertFalse(should_reschedule)

    def test_randomized_poll_matrix(self):
        rng = random.Random(7)
        result = UiResult(scenario_id="matrix", success=True, message="ok")

        for _ in range(25):
            worker_alive = rng.choice([True, False])
            tokens = [rng.choice(["EMPTY", "RESULT"]) for _ in range(2)]
            sequence = [result if token == "RESULT" else _EMPTY for token in tokens]

            ui_result, should_reschedule = _poll_queue_once(SequenceQueue(sequence), StubWorker(worker_alive))

            if tokens[0] == "RESULT":
                expected_result = result
                expected_reschedule = False
            elif worker_alive:
                expected_result = None
                expected_reschedule = True
            else:
                expected_result = result if tokens[1] == "RESULT" else None
                expected_reschedule = False

            self.assertEqual(ui_result, expected_result)
            self.assertEqual(should_reschedule, expected_reschedule)
