from __future__ import annotations
import time
from typing import Callable
from pywinauto import Application
from app.models.control_info import ControlInfo
from app.utils.safe_calls import safe_get
class ControlInspector:
    def __init__(self, max_depth=20, max_controls=10000, timeout_seconds=60): self.max_depth=max_depth; self.max_controls=max_controls; self.timeout_seconds=timeout_seconds
    def inspect(self, hwnd:int, backend:str, cancel:Callable[[],bool]|None=None, progress:Callable[[int,int,str],None]|None=None)->list[ControlInfo]:
        start=time.time(); cancel=cancel or (lambda: False); controls=[]; seen=set()
        app=Application(backend=backend).connect(handle=hwnd, timeout=5); root=app.window(handle=hwnd)
        def rect_dict(wrapper):
            r=safe_get(lambda: wrapper.rectangle(), None); return {} if r is None else {'left':r.left,'top':r.top,'right':r.right,'bottom':r.bottom}
        def walk(wrapper, depth, parent):
            if cancel() or len(controls)>=self.max_controls or depth>self.max_depth or time.time()-start>self.timeout_seconds: return
            key=(safe_get(lambda: wrapper.handle, 0), id(wrapper.element_info));
            if key in seen: return
            seen.add(key); idx=len(controls)
            info=ControlInfo(index=idx,parent_index=parent,depth=depth,backend=backend,name=safe_get(lambda: wrapper.element_info.name,'') or '',text=safe_get(lambda: wrapper.window_text(),'') or '',control_type=safe_get(lambda: wrapper.element_info.control_type,'') or '',friendly_class_name=safe_get(lambda: wrapper.friendly_class_name(),'') or '',class_name=safe_get(lambda: wrapper.element_info.class_name,'') or '',automation_id=safe_get(lambda: wrapper.element_info.automation_id,'') or '',handle=int(safe_get(lambda: wrapper.handle,0) or 0),process_id=int(safe_get(lambda: wrapper.element_info.process_id,0) or 0),rectangle=rect_dict(wrapper),enabled=safe_get(lambda: wrapper.is_enabled(),None),visible=safe_get(lambda: wrapper.is_visible(),None),focused=safe_get(lambda: wrapper.has_keyboard_focus(),None),keyboard_focusable=safe_get(lambda: wrapper.element_info.keyboard_focusable,None),offscreen=safe_get(lambda: wrapper.element_info.is_offscreen,None),patterns=safe_get(lambda: list(getattr(wrapper.element_info,'_supported_patterns',[]) or []),[]))
            children=safe_get(lambda: wrapper.children(), []) or []; info.children_count=len(children); controls.append(info)
            if progress: progress(len(controls), depth, backend)
            for ch in children: walk(ch, depth+1, idx)
        walk(root,0,None)
        by={c.index:c for c in controls}
        for c in controls:
            if c.parent_index in by: by[c.parent_index].children.append(c)
        return controls
