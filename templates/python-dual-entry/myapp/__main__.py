"""Compatibility delegate for `python -m myapp`."""

from myapp.main import main


if __name__ == "__main__":
    raise SystemExit(main())
