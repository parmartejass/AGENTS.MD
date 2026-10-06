from __future__ import annotations

import io
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.check_governance_core import _git_capture
from scripts.check_governance_core._inventory import RepositoryInventory
from scripts.check_governance_core._test_support import write as _write


class BoundedGitCaptureTests(unittest.TestCase):
    def test_bounded_capture_does_not_block_closing_a_live_reader_pipe(self) -> None:
        class BlockingPipe:
            def read(self, _size: int) -> bytes:
                _git_capture.time.sleep(1)
                return b""

            def close(self) -> None:
                raise AssertionError("live reader pipe must not be closed synchronously")

        class Process:
            def __init__(self) -> None:
                self.stdout = BlockingPipe()
                self.stderr = io.BytesIO()
                self.returncode = None

            def poll(self) -> int | None:
                return self.returncode

            def kill(self) -> None:
                raise OSError("kill denied")

            def wait(self, *, timeout: float) -> int:
                raise subprocess.TimeoutExpired("git", timeout)

        with patch.object(_git_capture, "TIMEOUT_SECONDS", 0.01), patch.object(
            _git_capture, "CLEANUP_SECONDS", 0.01
        ), patch.object(_git_capture.subprocess, "Popen", return_value=Process()):
            started = _git_capture.time.monotonic()
            _stdout, _stderr, _returncode, error = _git_capture.bounded_capture(
                ["git"], label="tracked files"
            )
            elapsed = _git_capture.time.monotonic() - started

        self.assertLess(elapsed, 0.5)
        self.assertIn("kill denied", error or "")
        self.assertIn("left open because its reader is still active", error or "")

    def test_pipe_capture_never_reads_or_retains_beyond_its_cap(self) -> None:
        class TrackingPipe(io.BytesIO):
            def __init__(self, value: bytes) -> None:
                super().__init__(value)
                self.requests: list[int] = []

            def read(self, size: int = -1) -> bytes:
                self.requests.append(size)
                return super().read(size)

        pipe = TrackingPipe(b"0123456789")
        output = bytearray()
        failures: list[str] = []
        failed = _git_capture.threading.Event()
        with patch.object(_git_capture, "READ_CHUNK_BYTES", 3):
            _git_capture._read_bounded_pipe(
                pipe,
                limit=4,
                label="stdout",
                output=output,
                failure=failures,
                failed=failed,
            )

        self.assertEqual(b"0123", bytes(output))
        self.assertLessEqual(max(pipe.requests), 3)
        self.assertEqual(["Git inventory stdout exceeded 4 bytes"], failures)

    @unittest.skipIf(shutil.which("git") is None, "git is unavailable")
    def test_git_inventory_stops_at_the_output_byte_limit(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            subprocess.run(["git", "init"], cwd=root, check=True, capture_output=True, timeout=10)
            _write(root / "tracked.txt", "x\n")
            subprocess.run(["git", "add", "tracked.txt"], cwd=root, check=True, capture_output=True, timeout=10)
            with patch.object(_git_capture, "MAX_STDOUT_BYTES", 1):
                paths, error = RepositoryInventory(root).tracked_paths(root)
            self.assertEqual((), paths)
            self.assertIn("exceeded", error or "")

    def test_git_inventory_reports_process_start_failure(self) -> None:
        with patch.object(_git_capture.subprocess, "Popen", side_effect=OSError("process denied")):
            paths, error = RepositoryInventory._git_paths(
                Path("."), ["ls-files", "-z"], "tracked files"
            )

        self.assertEqual((), paths)
        self.assertIn("process denied", error or "")

    def test_bounded_capture_preserves_primary_and_cleanup_failures(self) -> None:
        class Process:
            def __init__(self) -> None:
                self.stdout = io.BytesIO(b"overflow")
                self.stderr = io.BytesIO()
                self.returncode = None

            def poll(self) -> None:
                return None

            def kill(self) -> None:
                raise OSError("kill denied")

            def wait(self, *, timeout: float) -> None:
                raise subprocess.TimeoutExpired("git", timeout)

        with patch.object(_git_capture, "MAX_STDOUT_BYTES", 1), patch.object(
            _git_capture.subprocess, "Popen", return_value=Process()
        ):
            _stdout, _stderr, _returncode, error = _git_capture.bounded_capture(
                ["git"], label="tracked files"
            )

        self.assertIn("stdout exceeded 1 bytes", error or "")
        self.assertIn("cleanup also failed", error or "")
        self.assertIn("kill denied", error or "")
        self.assertIn("reap failed", error or "")

    def test_bounded_capture_closes_pipes_after_partial_reader_start_failure(self) -> None:
        class Pipe(io.BytesIO):
            pass

        class Process:
            def __init__(self) -> None:
                self.stdout = Pipe()
                self.stderr = Pipe()
                self.returncode = None

            def poll(self) -> int | None:
                return self.returncode

            def kill(self) -> None:
                self.returncode = -9

            def wait(self, *, timeout: float) -> int:
                self.returncode = -9
                return self.returncode

        real_thread = _git_capture.threading.Thread
        starts = 0

        class PartialStartThread(real_thread):
            def start(self) -> None:
                nonlocal starts
                starts += 1
                if starts == 2:
                    raise RuntimeError("thread unavailable")
                super().start()

        process = Process()
        with patch.object(_git_capture.subprocess, "Popen", return_value=process), patch.object(
            _git_capture.threading, "Thread", PartialStartThread
        ):
            _stdout, _stderr, _returncode, error = _git_capture.bounded_capture(
                ["git"], label="tracked files"
            )

        self.assertIn("thread unavailable", error or "")
        self.assertTrue(process.stdout.closed)
        self.assertTrue(process.stderr.closed)

    @unittest.skipIf(shutil.which("git") is None, "git is unavailable")
    def test_git_inventory_real_subprocess_is_reaped_after_normal_completion(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            subprocess.run(["git", "init"], cwd=root, check=True, capture_output=True, timeout=10)
            _write(root / "tracked.txt", "x\n")
            subprocess.run(["git", "add", "tracked.txt"], cwd=root, check=True, capture_output=True, timeout=10)
            paths, error = RepositoryInventory._git_paths(
                root, ["ls-files", "-z"], "tracked files"
            )

        self.assertIsNone(error)
        self.assertEqual(("tracked.txt",), paths)


if __name__ == "__main__":
    unittest.main()
