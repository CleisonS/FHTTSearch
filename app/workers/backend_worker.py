from __future__ import annotations

from PySide6.QtCore import QObject, Signal, Slot

from app.services.backend_detector import BackendDetector


class BackendWorker(QObject):
    started = Signal()
    progress = Signal(int, int, str)
    status = Signal(str)
    result = Signal(object)
    error = Signal(str)
    finished = Signal()
    cancelled = Signal()

    def __init__(self, window) -> None:
        super().__init__()
        self.window = window
        self._cancel = False

    def cancel(self) -> None:
        self._cancel = True

    @Slot()
    def run(self) -> None:
        self.started.emit()
        self.status.emit("Detectando backends...")
        try:
            if self._cancel:
                self.cancelled.emit()
                return
            win32, uia, classification = BackendDetector().detect(self.window.handle)
            self.result.emit((self.window, win32, uia, classification))
        except Exception as exc:
            self.error.emit(str(exc))
        finally:
            self.finished.emit()
