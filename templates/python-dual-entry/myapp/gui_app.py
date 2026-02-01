"""Tkinter GUI entry point (thin): select scenario -> run job on worker -> update UI via queue."""

from __future__ import annotations

import logging
import queue
import threading
import tkinter as tk
from dataclasses import dataclass
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from typing import Protocol, TypeVar

from myapp.constants import DEFAULT_GUI_POLL_MS
from myapp.errors import ConfigError
from myapp.runner import run_job
from myapp.scenarios import load_scenario


logger = logging.getLogger(__name__)


_T = TypeVar("_T")


class SupportsGetNowait(Protocol[_T]):
    """Protocol for queue-like objects that support non-blocking get."""

    def get_nowait(self) -> _T: ...


class SupportsIsAlive(Protocol):
    """Protocol for thread-like objects that support is_alive check."""

    def is_alive(self) -> bool: ...


@dataclass(frozen=True)
class UiResult:
    scenario_id: str
    success: bool
    message: str


def _poll_queue_once(
    result_queue: SupportsGetNowait[UiResult],
    worker: SupportsIsAlive | None,
) -> tuple[UiResult | None, bool]:
    """Return (ui_result, should_reschedule) for a single poll tick."""
    try:
        return result_queue.get_nowait(), False
    except queue.Empty:
        if worker and worker.is_alive():
            return None, True

    # Worker finished; drain once more to avoid missing a late enqueue.
    try:
        return result_queue.get_nowait(), False
    except queue.Empty:
        return None, False


class Application(tk.Tk):
    def __init__(self) -> None:
        super().__init__()

        self.title("MyApp - Dual-Entry Automation Template")
        self.geometry("700x220")
        self.minsize(650, 220)

        self._queue: queue.Queue[UiResult] = queue.Queue()
        self._worker: threading.Thread | None = None
        self._cancel_event = threading.Event()

        self._scenario_path = tk.StringVar()
        self._status = tk.StringVar(value="Ready")

        self._build_ui()
        logger.info("GUI ready")

    def _build_ui(self) -> None:
        frame = ttk.Frame(self, padding=12)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="Scenario JSON:").grid(row=0, column=0, sticky="w")

        entry = ttk.Entry(frame, textvariable=self._scenario_path, width=70)
        entry.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(4, 8))

        browse = ttk.Button(frame, text="Browse...", command=self._on_browse)
        browse.grid(row=1, column=2, sticky="e", padx=(8, 0))

        self._run_btn = ttk.Button(frame, text="Run", command=self._on_run)
        self._run_btn.grid(row=2, column=0, sticky="w")

        self._cancel_btn = ttk.Button(frame, text="Cancel", command=self._on_cancel, state="disabled")
        self._cancel_btn.grid(row=2, column=1, sticky="w", padx=(8, 0))

        self._progress = ttk.Progressbar(frame, mode="indeterminate")
        self._progress.grid(row=3, column=0, columnspan=3, sticky="ew", pady=(12, 4))

        ttk.Label(frame, textvariable=self._status).grid(row=4, column=0, columnspan=3, sticky="w")

        frame.columnconfigure(0, weight=1)

    def _on_browse(self) -> None:
        path = filedialog.askopenfilename(
            title="Select Scenario JSON",
            filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")],
        )
        if path:
            self._scenario_path.set(path)

    def _on_run(self) -> None:
        if self._worker and self._worker.is_alive():
            messagebox.showwarning("Busy", "A job is already running.")
            return

        scenario_path_raw = self._scenario_path.get().strip()
        if not scenario_path_raw:
            messagebox.showerror("Error", "Select a scenario JSON file.")
            return

        scenario_path = Path(scenario_path_raw)
        try:
            scenario = load_scenario(scenario_path)
        except ConfigError as exc:
            messagebox.showerror("Invalid scenario", str(exc))
            return

        self._status.set(f"Running: {scenario.scenario_id}")
        self._run_btn.configure(state="disabled")
        self._cancel_btn.configure(state="normal")
        self._cancel_event.clear()
        self._progress.start()

        self._worker = threading.Thread(target=self._worker_run, args=(scenario.scenario_id, scenario.job), daemon=True)
        self._worker.start()
        self.after(DEFAULT_GUI_POLL_MS, self._poll_queue)

    def _worker_run(self, scenario_id: str, job_config) -> None:
        result = run_job(job_config, cancel_event=self._cancel_event)

        if result.success:
            message = f"SUCCESS: lines_processed={result.lines_processed}\nOutput: {result.output_path}"
            self._queue.put(UiResult(scenario_id=scenario_id, success=True, message=message))
        else:
            errors = "\n".join(result.errors) if result.errors else "Unknown error"
            message = f"FAILED ({result.status.value})\n{errors}"
            self._queue.put(UiResult(scenario_id=scenario_id, success=False, message=message))

    def _poll_queue(self) -> None:
        ui_result, should_reschedule = _poll_queue_once(self._queue, self._worker)
        if ui_result is None:
            if should_reschedule:
                self.after(DEFAULT_GUI_POLL_MS, self._poll_queue)
            return

        self._progress.stop()
        self._run_btn.configure(state="normal")
        self._cancel_btn.configure(state="disabled")

        self._status.set("Ready")

        if ui_result.success:
            messagebox.showinfo("Complete", ui_result.message)
        else:
            messagebox.showerror("Failed", ui_result.message)

    def _on_cancel(self) -> None:
        self._cancel_event.set()
        self._status.set("Cancelling...")


def main() -> None:
    app = Application()
    app.mainloop()


if __name__ == "__main__":
    main()
