from __future__ import annotations
import json, shutil
from pathlib import Path
from PySide6.QtWidgets import QApplication, QMessageBox
from app.constants import CONFIG_FILE
from app.utils.logging_config import configure_logging
from app.ui.theme import load_theme
DEFAULT_CONFIG={"theme":"dark","log_level":"INFO","inspection_max_depth":20,"inspection_max_controls":10000,"inspection_timeout_seconds":60,"live_inspector_interval_ms":250,"default_backend":"uia","output_directory":"output","screenshots_directory":"output/screenshots","only_visible_windows":False,"unm_title_filters":["UNM","UNM2000","NE Manager","FiberHome","FH_","FH-"],"enable_overlay":False,"csv_delimiter":";","csv_encoding":"utf-8-sig","always_on_top_live_inspector":False}
def load_config(path:Path=CONFIG_FILE)->dict:
    if not path.exists(): path.write_text(json.dumps(DEFAULT_CONFIG,indent=2,ensure_ascii=False),encoding='utf-8'); return DEFAULT_CONFIG.copy()
    try:
        data=json.loads(path.read_text(encoding='utf-8')); cfg=DEFAULT_CONFIG.copy(); cfg.update({k:v for k,v in data.items() if k in DEFAULT_CONFIG}); return cfg
    except Exception:
        backup=path.with_suffix('.corrupted.bak'); shutil.copy2(path,backup); path.write_text(json.dumps(DEFAULT_CONFIG,indent=2,ensure_ascii=False),encoding='utf-8'); return DEFAULT_CONFIG.copy()
def create_app():
    cfg=load_config(); configure_logging(cfg.get('log_level','INFO')); app=QApplication.instance() or QApplication([]); app.setApplicationName('UNM Inspector'); app.setStyleSheet(load_theme()); return app,cfg
