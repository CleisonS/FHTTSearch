from __future__ import annotations

from PySide6.QtCore import QObject, Signal, Slot

from app.services.window_service import WindowService


class ScanWorker(QObject):
    started = Signal()
    progress = Signal(int, int, str)
    status = Signal(str)
    result = Signal(object)
    error = Signal(str)
    finished = Signal()
    cancelled = Signal()

    def __init__(self) -> None:
        super().__init__()
        self._cancel = False

    def cancel(self) -> None:
        self._cancel = True

    @Slot()
    def run(self) -> None:
        self.started.emit()
        self.status.emit("Listando janelas do Windows...")
        try:
            if self._cancel:
                self.cancelled.emit()
                return
            self.result.emit(WindowService().list_windows())
        except Exception as exc:
            self.error.emit(str(exc))
        finally:
            self.finished.emit()
