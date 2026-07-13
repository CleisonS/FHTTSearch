import pytest

try:
    from app.ui.main_window import MainWindow
except ImportError as exc:
    pytest.skip(f"PySide6/Qt indisponível neste ambiente: {exc}", allow_module_level=True)


def test_ui_smoke(qtbot):
    w = MainWindow({"live_inspector_interval_ms": 250, "inspection_max_depth": 1, "inspection_max_controls": 5, "inspection_timeout_seconds": 1})
    qtbot.addWidget(w)
    assert w.windowTitle() == "UNM Inspector"
