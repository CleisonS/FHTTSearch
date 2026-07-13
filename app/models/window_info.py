from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional
@dataclass
class WindowInfo:
    title: str=""; handle: int=0; pid: int=0; process_name: str=""; executable_path: str=""; class_name: str=""; rectangle: dict=field(default_factory=dict); visible: bool=False; minimized: bool=False; maximized: bool=False; session_name: str=""; architecture: str=""; integrity_level: str=""; win32_available: Optional[bool]=None; uia_available: Optional[bool]=None
