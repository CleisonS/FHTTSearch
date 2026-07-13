import pytest
pytest.importorskip('PySide6')
from app.ui.main_window import MainWindow

def test_ui_smoke(qtbot):
    w=MainWindow({'live_inspector_interval_ms':250,'inspection_max_depth':1,'inspection_max_controls':5,'inspection_timeout_seconds':1})
    qtbot.addWidget(w)
    assert w.windowTitle()=='UNM Inspector'
