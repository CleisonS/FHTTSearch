from PySide6.QtWidgets import QTreeWidget,QTreeWidgetItem
from PySide6.QtCore import Qt
class ControlTree(QTreeWidget):
    def __init__(self): super().__init__(); self.setHeaderLabels(['Controle','Tipo','Classe','Automation ID','Handle','Backend']); self.itemSelectionChanged.connect(self._sel); self._callback=None
    def on_selected(self, cb): self._callback=cb
    def populate(self, controls):
        self.clear(); items={}
        for c in controls:
            it=QTreeWidgetItem([c.name or c.text or '(sem nome)',c.control_type,c.class_name,c.automation_id,str(c.handle),c.backend]); it.setData(0,Qt.ItemDataRole.UserRole,c)
            items[c.index]=it
            if c.parent_index in items: items[c.parent_index].addChild(it)
            else: self.addTopLevelItem(it)
        self.expandToDepth(2); self.resizeColumnToContents(0)
    def _sel(self):
        it=self.currentItem()
        if it and self._callback: self._callback(it.data(0,Qt.ItemDataRole.UserRole))
