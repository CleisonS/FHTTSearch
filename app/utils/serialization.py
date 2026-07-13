from __future__ import annotations
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any

def to_plain(obj: Any) -> Any:
    if is_dataclass(obj): return {k: to_plain(v) for k,v in asdict(obj).items()}
    if isinstance(obj, dict): return {str(k): to_plain(v) for k,v in obj.items()}
    if isinstance(obj, (list, tuple, set)): return [to_plain(v) for v in obj]
    if isinstance(obj, Path): return str(obj)
    if isinstance(obj, (str, int, float, bool)) or obj is None: return obj
    if hasattr(obj, "left") and hasattr(obj, "top"):
        return {"left": getattr(obj,"left",0), "top": getattr(obj,"top",0), "right": getattr(obj,"right",0), "bottom": getattr(obj,"bottom",0)}
    return str(obj)
