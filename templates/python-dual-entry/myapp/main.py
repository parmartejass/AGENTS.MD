"""Top-level entry wrapper: default to GUI, auto-route CLI flags."""

from __future__ import annotations

import logging
import sys

from myapp.cli_app import has_cli_intent
from myapp.logging_config import setup_logging


logger = logging.getLogger(__name__)


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)

    if has_cli_intent(argv):
        from myapp.cli_app import main as cli_main

        return cli_main(argv)

    setup_logging()
    logger.debug("argv=%s", argv)

    try:
        from myapp.gui_app import main as gui_main

        gui_main()
        return 0
    except Exception:
        logger.exception("GUI startup failed")
        return 1
