"""Compatibility delegate for `python -m myapp`."""

from myapp.myapp_main import main


if __name__ == "__main__":
    raise SystemExit(main())
