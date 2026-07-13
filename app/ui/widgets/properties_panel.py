from PySide6.QtWidgets import QTableWidget,QTableWidgetItem
class PropertiesPanel(QTableWidget):
    def __init__(self): super().__init__(0,2); self.setHorizontalHeaderLabels(['Propriedade','Valor']); self.setEditTriggers(self.EditTrigger.NoEditTriggers)
    def show_control(self,c):
        data={k:getattr(c,k,'') for k in ['name','text','control_type','friendly_class_name','class_name','automation_id','handle','process_id','rectangle','enabled','visible','focused','keyboard_focusable','offscreen','backend','parent_index','children_count','patterns','errors']}
        self.setRowCount(len(data))
        for r,(k,v) in enumerate(data.items()): self.setItem(r,0,QTableWidgetItem(k)); self.setItem(r,1,QTableWidgetItem(str(v)))
        self.resizeColumnsToContents()
