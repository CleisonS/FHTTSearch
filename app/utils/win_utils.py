from __future__ import annotations
import ctypes, os, platform
from typing import Tuple

def is_windows() -> bool: return os.name == "nt"
def is_user_admin() -> bool:
    if not is_windows(): return False
    try: return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception: return False

def get_dpi_scale() -> float:
    if not is_windows(): return 1.0
    try:
        user32=ctypes.windll.user32; user32.SetProcessDPIAware(); return user32.GetDpiForSystem()/96.0
    except Exception: return 1.0

def environment_summary() -> dict:
    return {"windows": platform.platform(), "python": platform.python_version(), "admin": is_user_admin(), "dpi_scale": get_dpi_scale(), "user": os.environ.get("USERNAME") or os.environ.get("USER",""), "hostname": platform.node()}
