from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QTreeWidget, QTreeWidgetItem


class ControlTree(QTreeWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setHeaderLabels(["Controle", "Tipo", "Classe", "Automation ID", "Handle", "Backend"])
        self.itemSelectionChanged.connect(self._selected_changed)
        self._callback = None

    def on_selected(self, callback) -> None:
        self._callback = callback

    def populate(self, controls) -> None:
        self.clear()
        self._add_controls(controls)
        self.expandToDepth(2)
        self.resizeColumnToContents(0)

    def populate_backend_roots(self, win32_controls, uia_controls) -> None:
        self.clear()
        self._add_backend_root("Win32", win32_controls)
        self._add_backend_root("UIA", uia_controls)
        self.expandToDepth(2)
        self.resizeColumnToContents(0)

    def _add_backend_root(self, label: str, controls) -> None:
        root = QTreeWidgetItem([label, "Backend", "", "", "", label.lower()])
        root.setData(0, Qt.ItemDataRole.UserRole, None)
        self.addTopLevelItem(root)
        self._add_controls(controls, root)

    def _add_controls(self, controls, root_item=None) -> None:
        items = {}
        for control in controls:
            item = QTreeWidgetItem([
                control.name or control.text or "(sem nome)",
                control.control_type,
                control.class_name,
                control.automation_id,
                str(control.handle),
                control.backend,
            ])
            item.setData(0, Qt.ItemDataRole.UserRole, control)
            items[control.index] = item
            if control.parent_index in items:
                items[control.parent_index].addChild(item)
            elif root_item is not None:
                root_item.addChild(item)
            else:
                self.addTopLevelItem(item)

    def _selected_changed(self) -> None:
        item = self.currentItem()
        if item is not None and self._callback:
            control = item.data(0, Qt.ItemDataRole.UserRole)
            if control is not None:
                self._callback(control)
