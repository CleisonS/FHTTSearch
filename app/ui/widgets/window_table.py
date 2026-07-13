from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QAbstractItemView, QHeaderView, QTableWidget, QTableWidgetItem

from app.models.window_info import WindowInfo


class WindowTable(QTableWidget):
    window_double_clicked = Signal(object)

    headers = [
        "Título",
        "PID",
        "Processo",
        "Handle",
        "Classe",
        "Visível",
        "Minimizada",
        "Maximizada",
        "Win32",
        "UIA",
    ]

    def __init__(self) -> None:
        super().__init__(0, len(self.headers))
        self._windows_by_handle: dict[int, WindowInfo] = {}
        self.setHorizontalHeaderLabels(self.headers)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.setSortingEnabled(True)
        self.itemDoubleClicked.connect(self._emit_double_clicked)
        header = self.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)

    def set_windows(self, windows: list[WindowInfo], preserve_handle: int | None = None) -> None:
        selected = preserve_handle or (self.selected_window().handle if self.selected_window() else None)
        self.setSortingEnabled(False)
        self._windows_by_handle = {w.handle: w for w in windows}
        self.setRowCount(len(windows))
        for row, window in enumerate(windows):
            values = [
                window.title or "(sem título)",
                str(window.pid),
                window.process_name,
                f"{window.handle} / 0x{window.handle:08X}",
                window.class_name,
                self._yes_no(window.visible),
                self._yes_no(window.minimized),
                self._yes_no(window.maximized),
                self._backend_text(window.win32_available),
                self._backend_text(window.uia_available),
            ]
            for column, value in enumerate(values):
                item = QTableWidgetItem(value)
                item.setData(Qt.ItemDataRole.UserRole, window.handle)
                item.setToolTip(window.executable_path or "Caminho do executável indisponível")
                if column in {1, 3}:
                    item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                self.setItem(row, column, item)
        self.setSortingEnabled(True)
        if selected:
            self.select_handle(selected)

    def selected_window(self) -> WindowInfo | None:
        rows = self.selectionModel().selectedRows() if self.selectionModel() else []
        if not rows:
            return None
        item = self.item(rows[0].row(), 0)
        if item is None:
            return None
        return self._windows_by_handle.get(int(item.data(Qt.ItemDataRole.UserRole)))

    def select_handle(self, handle: int) -> bool:
        for row in range(self.rowCount()):
            item = self.item(row, 0)
            if item and int(item.data(Qt.ItemDataRole.UserRole)) == handle:
                self.selectRow(row)
                return True
        return False

    def _emit_double_clicked(self) -> None:
        window = self.selected_window()
        if window is not None:
            self.window_double_clicked.emit(window)

    @staticmethod
    def _yes_no(value: bool) -> str:
        return "Sim" if value else "Não"

    @staticmethod
    def _backend_text(value: bool | None) -> str:
        if value is True:
            return "OK"
        if value is False:
            return "Falhou"
        return "Não testado"
