"""Command-line launcher: ``python -m scripts.check_governance_core`` from the governance root."""

import sys

from scripts.check_governance_core import main


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
