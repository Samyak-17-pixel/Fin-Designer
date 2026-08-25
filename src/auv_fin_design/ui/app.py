"""Launch the desktop GUI: python -m auv_fin_design.ui.app"""

from __future__ import annotations

import sys


def main() -> None:
    try:
        from auv_fin_design.ui.gui.main_window import run_app
    except ImportError as exc:
        print(
            "PySide6 is required for the GUI.\n"
            "Install with:  pip install -e \".[gui]\"\n"
            f"Details: {exc}",
            file=sys.stderr,
        )
        sys.exit(1)
    sys.exit(run_app())


if __name__ == "__main__":
    main()
