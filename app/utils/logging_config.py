from __future__ import annotations
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from app.constants import LOG_DIR

def configure_logging(level: str="INFO") -> Path:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    log_file=LOG_DIR/"unm_inspector.log"
    root=logging.getLogger(); root.setLevel(getattr(logging, level.upper(), logging.INFO)); root.handlers.clear()
    fmt=logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(funcName)s | %(message)s")
    fh=RotatingFileHandler(log_file, maxBytes=5*1024*1024, backupCount=5, encoding="utf-8")
    fh.setFormatter(fmt); root.addHandler(fh)
    sh=logging.StreamHandler(); sh.setFormatter(fmt); root.addHandler(sh)
    return log_file
