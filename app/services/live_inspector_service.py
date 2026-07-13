from __future__ import annotations
from app.models.control_info import ControlInfo
class LiveInspectorService:
    def inspect_at_cursor(self, backend='uia')->ControlInfo:
        if __import__('os').name!='nt': return ControlInfo(backend=backend, errors=['Live Inspector requer Windows.'])
        import win32gui, win32api
        from pywinauto import Desktop
        x,y=win32api.GetCursorPos(); hwnd=win32gui.WindowFromPoint((x,y))
        info=ControlInfo(backend=backend, handle=int(hwnd), rectangle={'left':x,'top':y,'right':x,'bottom':y})
        try:
            e=Desktop(backend=backend).from_point(x,y); info.name=e.element_info.name or ''; info.text=e.window_text() or ''; info.control_type=e.element_info.control_type or ''; info.class_name=e.element_info.class_name or ''; info.automation_id=getattr(e.element_info,'automation_id','') or ''; r=e.rectangle(); info.rectangle={'left':r.left,'top':r.top,'right':r.right,'bottom':r.bottom}; info.process_id=e.element_info.process_id; info.enabled=e.is_enabled(); info.visible=e.is_visible(); info.children_count=len(e.children())
        except Exception as exc: info.errors.append(str(exc))
        return info
