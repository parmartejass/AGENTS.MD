"""Centralized logging setup (SSOT)."""

from __future__ import annotations

import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

from myapp.constants import DEFAULT_ENCODING, LOG_DATE_FORMAT, LOG_FORMAT
from myapp.log_contract import EVENT_LOGGER_NAME


class JsonlEventHandler(logging.Handler):
    """Emit structured events as JSONL."""

    def __init__(self, *, default_event_log: Path | None) -> None:
        super().__init__(level=logging.INFO)
        self._default_event_log = Path(default_event_log) if default_event_log is not None else None
        self._write_failure_reported = False

    def resolve_path(self, run_id: str) -> Path:
        path = self._default_event_log or _default_event_log_path(run_id)
        return _remember_run_event_log_path(run_id, path)

    def emit(self, record: logging.LogRecord) -> None:
        payload = getattr(record, "event_payload", None)
        if not isinstance(payload, dict):
            return

        run_id = str(payload.get("run_id") or "unknown")
        raw_path = getattr(record, "event_log_path", None)

        try:
            target_path = Path(raw_path) if raw_path else self.resolve_path(run_id)
            target_path = _remember_run_event_log_path(run_id, target_path)
            target_path.parent.mkdir(parents=True, exist_ok=True)

            entry: dict[str, Any] = dict(payload)
            entry.setdefault("ts", datetime.now().astimezone().isoformat(timespec="milliseconds"))
            entry.setdefault(
                "source",
                {
                    "module": record.module,
                    "function": record.funcName,
                    "file": record.pathname,
                    "line": record.lineno,
                },
            )
            entry.setdefault("logger", record.name)

            with target_path.open("a", encoding=DEFAULT_ENCODING, newline="\n") as handle:
                handle.write(json.dumps(entry, sort_keys=True))
                handle.write("\n")
            self._write_failure_reported = False
        except OSError as exc:
            if not self._write_failure_reported:
                logging.getLogger(__name__).warning(
                    "Event log write failed at %s: %s",
                    target_path,
                    exc,
                )
                self._write_failure_reported = True


_EVENT_HANDLER: JsonlEventHandler | None = None
_RUN_EVENT_LOG_PATHS: dict[str, Path] = {}


def setup_logging(
    *,
    verbose: bool = False,
    log_file: Path | None = None,
    event_log: Path | None = None,
) -> None:
    level = logging.DEBUG if verbose else logging.INFO

    handlers: list[logging.Handler] = [logging.StreamHandler(sys.stdout)]
    if log_file is not None:
        handlers.append(logging.FileHandler(log_file, encoding=DEFAULT_ENCODING))

    logging.basicConfig(
        level=level,
        format=LOG_FORMAT,
        datefmt=LOG_DATE_FORMAT,
        handlers=handlers,
        force=True,
    )

    _install_event_handler(event_log=event_log)


def ensure_event_logger_configured(*, event_log: Path | None = None) -> None:
    if _EVENT_HANDLER is not None:
        return
    _install_event_handler(event_log=event_log)


def _install_event_handler(*, event_log: Path | None) -> None:
    global _EVENT_HANDLER
    _EVENT_HANDLER = JsonlEventHandler(default_event_log=event_log)

    event_logger = logging.getLogger(EVENT_LOGGER_NAME)
    event_logger.handlers.clear()
    event_logger.addHandler(_EVENT_HANDLER)
    event_logger.setLevel(logging.INFO)
    event_logger.propagate = False


def get_event_log_path(run_id: str) -> Path:
    cached = _RUN_EVENT_LOG_PATHS.get(run_id)
    if cached is not None:
        return cached

    if _EVENT_HANDLER is None:
        return _remember_run_event_log_path(run_id, _default_event_log_path(run_id))
    return _EVENT_HANDLER.resolve_path(run_id)


def _default_event_log_path(run_id: str) -> Path:
    date_part = datetime.now().astimezone().strftime("%Y%m%d")
    return Path("run-logs") / date_part / f"{run_id}.jsonl"


def _remember_run_event_log_path(run_id: str, path: Path) -> Path:
    normalized = Path(path)
    _RUN_EVENT_LOG_PATHS.setdefault(run_id, normalized)
    return _RUN_EVENT_LOG_PATHS[run_id]
