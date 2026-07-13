from PySide6.QtCore import QObject, Signal, Slot
class ExportWorker(QObject):
    started=Signal(); progress=Signal(int,int,str); status=Signal(str); result=Signal(object); error=Signal(str); finished=Signal(); cancelled=Signal()
    def __init__(self, func, *args): super().__init__(); self.func=func; self.args=args
    @Slot()
    def run(self):
        self.started.emit();
        try: self.result.emit(self.func(*self.args))
        except Exception as exc: self.error.emit(str(exc))
        self.finished.emit()
