from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional
@dataclass
class ControlInfo:
    index:int=0; parent_index:Optional[int]=None; depth:int=0; backend:str=""; name:str=""; text:str=""; control_type:str=""; friendly_class_name:str=""; class_name:str=""; automation_id:str=""; handle:int=0; process_id:int=0; rectangle:dict=field(default_factory=dict); enabled:Optional[bool]=None; visible:Optional[bool]=None; focused:Optional[bool]=None; keyboard_focusable:Optional[bool]=None; offscreen:Optional[bool]=None; children_count:int=0; patterns:list[str]=field(default_factory=list); errors:list[str]=field(default_factory=list); children:list['ControlInfo']=field(default_factory=list)
    @property
    def width(self): return max(0, int(self.rectangle.get('right',0))-int(self.rectangle.get('left',0)))
    @property
    def height(self): return max(0, int(self.rectangle.get('bottom',0))-int(self.rectangle.get('top',0)))
