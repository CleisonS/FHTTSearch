from __future__ import annotations

import json
import shutil
from pathlib import Path

from app.constants import CONFIG_FILE
from app.utils.logging_config import configure_logging

DEFAULT_CONFIG = {
    "theme": "dark",
    "log_level": "INFO",
    "inspection_max_depth": 20,
    "inspection_max_controls": 10000,
    "inspection_timeout_seconds": 60,
    "live_inspector_interval_ms": 250,
    "default_backend": "uia",
    "output_directory": "output",
    "screenshots_directory": "output/screenshots",
    "only_visible_windows": True,
    "unm_title_filters": ["UNM", "UNM2000", "NE Manager", "FiberHome", "Main Topology", "ONU List", "FH_", "FH-"],
    "enable_overlay": False,
    "csv_delimiter": ";",
    "csv_encoding": "utf-8-sig",
    "always_on_top_live_inspector": False,
}


def load_config(path: Path = CONFIG_FILE) -> dict:
    if not path.exists():
        path.write_text(json.dumps(DEFAULT_CONFIG, indent=2, ensure_ascii=False), encoding="utf-8")
        return DEFAULT_CONFIG.copy()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        config = DEFAULT_CONFIG.copy()
        config.update({key: value for key, value in data.items() if key in DEFAULT_CONFIG})
        return config
    except Exception:
        backup = path.with_suffix(".corrupted.bak")
        shutil.copy2(path, backup)
        path.write_text(json.dumps(DEFAULT_CONFIG, indent=2, ensure_ascii=False), encoding="utf-8")
        return DEFAULT_CONFIG.copy()


def create_app():
    from PySide6.QtWidgets import QApplication

    from app.ui.theme import load_theme

    config = load_config()
    configure_logging(config.get("log_level", "INFO"))
    app = QApplication.instance() or QApplication([])
    app.setApplicationName("UNM Inspector")
    app.setStyleSheet(load_theme())
    return app, config
