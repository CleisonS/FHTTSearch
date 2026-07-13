from __future__ import annotations
import logging
from typing import Callable, TypeVar
T=TypeVar("T")
def safe_get(func: Callable[[], T], default=None, label: str=""):
    try: return func()
    except Exception as exc:
        logging.getLogger(__name__).debug("safe_get failed %s: %s", label, exc)
        return default
