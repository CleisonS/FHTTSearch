from __future__ import annotations
import re, shutil
from datetime import datetime
from pathlib import Path

def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True); return path

def sanitize_filename(value: str, max_len: int=80) -> str:
    cleaned=re.sub(r"[^A-Za-z0-9_. -]+", "_", value or "sem_titulo").strip().replace(" ", "_")
    cleaned=re.sub(r"_+", "_", cleaned).strip("._") or "sem_titulo"
    return cleaned[:max_len]

def timestamp() -> str: return datetime.now().strftime("%Y%m%d_%H%M%S")

def copy_if_exists(src: Path, dst: Path) -> bool:
    if src.exists(): ensure_dir(dst.parent); shutil.copy2(src,dst); return True
    return False
