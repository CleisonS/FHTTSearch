from PySide6.QtCore import QObject, Signal, Slot
from app.services.backend_detector import BackendDetector
from app.services.control_inspector import ControlInspector
from app.services.readiness_analyzer import ReadinessAnalyzer
from app.models.inspection_result import InspectionResult
class InspectionWorker(QObject):
    started=Signal(); progress=Signal(int,int,str); status=Signal(str); result=Signal(object); error=Signal(str); finished=Signal(); cancelled=Signal()
    def __init__(self, window, config): super().__init__(); self.window=window; self.config=config; self._cancel=False
    def cancel(self): self._cancel=True
    def _progress(self,count,depth,backend): self.progress.emit(count,depth,backend)
    @Slot()
    def run(self):
        self.started.emit(); res=InspectionResult(window=self.window)
        try:
            self.status.emit('Detectando backends...'); res.win32_result,res.uia_result,_=BackendDetector().detect(self.window.handle)
            insp=ControlInspector(self.config.get('inspection_max_depth',20), self.config.get('inspection_max_controls',10000), self.config.get('inspection_timeout_seconds',60))
            if res.win32_result.success and not self._cancel: self.status.emit('Inspecionando Win32...'); res.controls_win32=insp.inspect(self.window.handle,'win32',lambda:self._cancel,self._progress)
            if res.uia_result.success and not self._cancel: self.status.emit('Inspecionando UIA...'); res.controls_uia=insp.inspect(self.window.handle,'uia',lambda:self._cancel,self._progress)
            res.readiness=ReadinessAnalyzer().analyze(res.controls_win32+res.controls_uia); self.result.emit(res)
        except Exception as exc: res.errors.append(str(exc)); self.error.emit(str(exc)); self.result.emit(res)
        self.finished.emit()
