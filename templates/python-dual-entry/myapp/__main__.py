"""Entry dispatcher: route to GUI or CLI."""

from __future__ import annotations

import logging
import sys

from myapp.logging_config import setup_logging


logger = logging.getLogger(__name__)

_CLI_TRIGGER_FLAGS = {"--cli", "--help", "-h", "--version"}


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    setup_logging(verbose="--verbose" in argv)

    logger.debug("argv=%s", argv)

    if _CLI_TRIGGER_FLAGS.intersection(argv):
        from myapp.cli_app import main as cli_main

        return cli_main(argv)

    from myapp.gui_app import main as gui_main

    gui_main()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

