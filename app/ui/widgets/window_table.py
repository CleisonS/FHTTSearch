from PySide6.QtWidgets import QTableWidget,QTableWidgetItem
class WindowTable(QTableWidget):
    headers=['Título','PID','Processo','Handle','Classe','Visível','Minimizável','Backend Win32','Backend UIA']
    def __init__(self): super().__init__(0,len(self.headers)); self.setHorizontalHeaderLabels(self.headers); self.setSelectionBehavior(self.SelectionBehavior.SelectRows); self.setEditTriggers(self.EditTrigger.NoEditTriggers); self._windows=[]
    def set_windows(self, windows):
        self._windows=windows; self.setRowCount(len(windows))
        for r,w in enumerate(windows):
            vals=[w.title,w.pid,w.process_name,w.handle,w.class_name,'Sim' if w.visible else 'Não','Sim' if w.minimized else 'Não',str(w.win32_available),str(w.uia_available)]
            for c,v in enumerate(vals): self.setItem(r,c,QTableWidgetItem(str(v)))
        self.resizeColumnsToContents()
    def selected_window(self):
        rows=self.selectionModel().selectedRows(); return self._windows[rows[0].row()] if rows else None
