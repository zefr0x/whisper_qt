"""A launcher for the application."""
from sys import argv

from .gui.main import ui_main


def main() -> int:
    """Entry point for the application."""
    return ui_main(argv)


if __name__ == "__main__":
    raise SystemExit(main())
