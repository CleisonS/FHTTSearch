from PySide6.QtCore import QObject, Signal, Slot
from app.services.window_service import WindowService
class ScanWorker(QObject):
    started=Signal(); progress=Signal(int,int,str); status=Signal(str); result=Signal(object); error=Signal(str); finished=Signal(); cancelled=Signal()
    def __init__(self): super().__init__(); self._cancel=False
    def cancel(self): self._cancel=True
    @Slot()
    def run(self):
        self.started.emit(); self.status.emit('Listando janelas...')
        try: self.result.emit(WindowService().list_windows())
        except Exception as exc: self.error.emit(str(exc))
        self.finished.emit()
