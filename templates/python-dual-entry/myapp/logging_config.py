"""Centralized logging setup (SSOT)."""

from __future__ import annotations

import logging
import sys
from pathlib import Path

from myapp.constants import DEFAULT_ENCODING, LOG_DATE_FORMAT, LOG_FORMAT


def setup_logging(*, verbose: bool = False, log_file: Path | None = None) -> None:
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

