"""GUI bootstrap. PySide6 is optional; the CLI is always available."""
from __future__ import annotations

from ai_outpaint_studio.config.loader import load_config
from ai_outpaint_studio.utils.logging_setup import configure_logging


def main() -> int:
    cfg = load_config()
    configure_logging(cfg.app.log_level)
    try:
        from ai_outpaint_studio.gui.main_window import launch
    except ImportError:
        print("PySide6 not installed. Use the CLI: `outpaint --help`.")
        return 2
    return launch(cfg)


if __name__ == "__main__":
    raise SystemExit(main())