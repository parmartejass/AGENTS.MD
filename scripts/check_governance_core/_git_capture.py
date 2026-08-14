from __future__ import annotations

import subprocess
import threading
import time


MAX_STDOUT_BYTES = 16 * 1024 * 1024
MAX_STDERR_BYTES = 64 * 1024
READ_CHUNK_BYTES = 64 * 1024
TIMEOUT_SECONDS = 30.0
CLEANUP_SECONDS = 5.0


def _read_bounded_pipe(
    pipe,
    *,
    limit: int,
    label: str,
    output: bytearray,
    failure: list[str],
    failed: threading.Event,
) -> None:
    try:
        while not failed.is_set():
            remaining = limit + 1 - len(output)
            chunk = pipe.read(min(READ_CHUNK_BYTES, max(1, remaining)))
            if not chunk:
                return
            output.extend(chunk)
            if len(output) > limit:
                del output[limit:]
                failure.append(f"Git inventory {label} exceeded {limit} bytes")
                failed.set()
                return
    except (OSError, RuntimeError) as exc:
        failure.append(f"Unable to read Git inventory {label}: {exc}")
        failed.set()


def bounded_capture(
    command: list[str],
    *,
    label: str,
) -> tuple[bytes, bytes, int | None, str | None]:
    """Capture one Git command within fixed memory, time, and cleanup bounds."""

    process: subprocess.Popen[bytes] | None = None
    stdout = bytearray()
    stderr = bytearray()
    capture_failures: list[str] = []
    cleanup_failures: list[str] = []
    failed = threading.Event()
    readers: list[threading.Thread] = []
    started_readers: list[threading.Thread] = []
    primary: str | None = None
    try:
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        assert process.stdout is not None
        assert process.stderr is not None
        readers = [
            threading.Thread(
                target=_read_bounded_pipe,
                kwargs={
                    "pipe": process.stdout,
                    "limit": MAX_STDOUT_BYTES,
                    "label": "stdout",
                    "output": stdout,
                    "failure": capture_failures,
                    "failed": failed,
                },
                daemon=True,
            ),
            threading.Thread(
                target=_read_bounded_pipe,
                kwargs={
                    "pipe": process.stderr,
                    "limit": MAX_STDERR_BYTES,
                    "label": "stderr",
                    "output": stderr,
                    "failure": capture_failures,
                    "failed": failed,
                },
                daemon=True,
            ),
        ]
        for reader in readers:
            reader.start()
            started_readers.append(reader)
        deadline = time.monotonic() + TIMEOUT_SECONDS
        while process.poll() is None and not failed.is_set():
            if time.monotonic() >= deadline:
                primary = (
                    f"Unable to enumerate {label} with git ls-files: "
                    f"timed out after {TIMEOUT_SECONDS:g} seconds"
                )
                failed.set()
                break
            failed.wait(0.01)
        if capture_failures and primary is None:
            primary = capture_failures[0]
    except (FileNotFoundError, OSError, RuntimeError) as exc:
        primary = f"Unable to enumerate {label} with git ls-files: {exc}"
    finally:
        if process is not None:
            if process.poll() is None:
                try:
                    process.kill()
                except OSError as exc:
                    cleanup_failures.append(f"kill failed: {exc}")
            try:
                process.wait(timeout=CLEANUP_SECONDS)
            except (OSError, subprocess.TimeoutExpired) as exc:
                cleanup_failures.append(f"reap failed: {exc}")
            live_readers: set[threading.Thread] = set()
            for reader in started_readers:
                reader.join(timeout=CLEANUP_SECONDS)
                if reader.is_alive():
                    cleanup_failures.append(f"{reader.name} did not stop before pipe close")
                    live_readers.add(reader)
            for index, (pipe_name, pipe) in enumerate((("stdout", process.stdout), ("stderr", process.stderr))):
                if pipe is None:
                    continue
                reader = readers[index] if index < len(readers) else None
                if reader in live_readers:
                    cleanup_failures.append(f"{pipe_name} left open because its reader is still active")
                    continue
                try:
                    pipe.close()
                except (OSError, RuntimeError, ValueError) as exc:
                    cleanup_failures.append(f"{pipe_name} close failed: {exc}")
    if primary is None and capture_failures:
        primary = capture_failures[0]
    if cleanup_failures:
        cleanup_detail = "; ".join(cleanup_failures)
        primary = (
            f"{primary}; cleanup also failed: {cleanup_detail}"
            if primary
            else f"Unable to clean up git inventory for {label}: {cleanup_detail}"
        )
    return bytes(stdout), bytes(stderr), process.returncode if process is not None else None, primary
