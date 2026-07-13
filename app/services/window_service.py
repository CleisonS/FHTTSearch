from __future__ import annotations
from app.models.window_info import WindowInfo
from app.constants import DEFAULT_UNM_FILTERS
from app.utils.safe_calls import safe_get
from app.services.process_service import ProcessService

def matches_window_filter(w: WindowInfo, text: str="", only_unm: bool=False, only_visible: bool=False) -> bool:
    hay=f"{w.title} {w.process_name} {w.class_name}".lower()
    if only_visible and not w.visible: return False
    if only_unm and not any(f.lower() in hay for f in DEFAULT_UNM_FILTERS): return False
    return not text or text.lower() in hay
class WindowService:
    def list_windows(self)->list[WindowInfo]:
        if __import__('os').name != 'nt': return []
        import win32gui, win32process
        ps=ProcessService(); out=[]
        def cb(hwnd,_):
            title=safe_get(lambda: win32gui.GetWindowText(hwnd), "") or ""
            _,pid=win32process.GetWindowThreadProcessId(hwnd); pdata=ps.get_process_data(pid)
            rect=safe_get(lambda: win32gui.GetWindowRect(hwnd), (0,0,0,0))
            out.append(WindowInfo(title=title, handle=int(hwnd), pid=pid, process_name=pdata.get('name',''), executable_path=pdata.get('exe',''), class_name=safe_get(lambda: win32gui.GetClassName(hwnd),''), rectangle={'left':rect[0],'top':rect[1],'right':rect[2],'bottom':rect[3]}, visible=bool(safe_get(lambda: win32gui.IsWindowVisible(hwnd), False)), minimized=bool(safe_get(lambda: win32gui.IsIconic(hwnd), False)), maximized=bool(safe_get(lambda: win32gui.IsZoomed(hwnd), False))))
            return True
        win32gui.EnumWindows(cb, None); return out
