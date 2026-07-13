from __future__ import annotations
import time
from pywinauto import Application
from app.models.backend_result import BackendResult
class BackendDetector:
    def detect_backend(self, hwnd:int, backend:str)->BackendResult:
        st=time.time(); r=BackendResult(backend=backend)
        try:
            app=Application(backend=backend).connect(handle=hwnd, timeout=5); w=app.window(handle=hwnd)
            r.success=True; r.handle_valid=bool(hwnd); r.title_accessible=bool(w.window_text() is not None)
            children=w.descendants(); r.controls_count=len(children); r.named_controls_count=sum(1 for c in children if getattr(c.element_info,'name','')); r.meaningful_controls_count=sum(1 for c in children if getattr(c.element_info,'control_type','') in ('Edit','Tree','Table','DataGrid','List','Tab','Button'))
            r.score=min(100, r.controls_count + r.named_controls_count*2 + r.meaningful_controls_count*10)
        except Exception as exc: r.error=str(exc)
        r.duration_ms=int((time.time()-st)*1000); return r
    def detect(self, hwnd:int)->tuple[BackendResult,BackendResult,str]:
        w=self.detect_backend(hwnd,'win32'); u=self.detect_backend(hwnd,'uia')
        if not w.success and not u.success: c='NO_ACCESS'
        elif w.score>u.score*1.3: c='WIN32_RECOMMENDED'
        elif u.score>w.score*1.3: c='UIA_RECOMMENDED'
        elif w.success and u.success: c='HYBRID_RECOMMENDED'
        else: c='LIMITED_ACCESS'
        w.classification=u.classification=c; return w,u,c
