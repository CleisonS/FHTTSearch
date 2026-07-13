from PySide6.QtWidgets import QMainWindow,QWidget,QVBoxLayout,QHBoxLayout,QPushButton,QComboBox,QCheckBox,QSpinBox,QTextEdit,QApplication
from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QShortcut,QKeySequence
from app.services.live_inspector_service import LiveInspectorService
from app.utils.serialization import to_plain
import json
class LiveInspectorWindow(QMainWindow):
    def __init__(self, config):
        super().__init__(); self.setWindowTitle('Live Inspector'); self.resize(520,600); self.service=LiveInspectorService(); self.current=None
        c=QWidget(); self.setCentralWidget(c); lay=QVBoxLayout(c); bar=QHBoxLayout(); lay.addLayout(bar)
        self.backend=QComboBox(); self.backend.addItems(['uia','win32']); self.interval=QSpinBox(); self.interval.setRange(100,1000); self.interval.setValue(config.get('live_inspector_interval_ms',250)); self.top=QCheckBox('Sempre no topo'); self.overlay=QCheckBox('Destacar controle')
        for b in ['Iniciar','Pausar','Congelar','Copiar propriedades','Exportar elemento']:
            btn=QPushButton(b); bar.addWidget(btn); setattr(self,b.split()[0].lower(),btn)
        bar.addWidget(self.backend); bar.addWidget(self.interval); bar.addWidget(self.top); bar.addWidget(self.overlay)
        self.text=QTextEdit(); self.text.setReadOnly(True); lay.addWidget(self.text); self.timer=QTimer(self); self.timer.timeout.connect(self.refresh); self.iniciar.clicked.connect(lambda:self.timer.start(self.interval.value())); self.pausar.clicked.connect(self.timer.stop); self.congelar.clicked.connect(self.timer.stop); self.copiar.clicked.connect(self.copy); self.top.toggled.connect(self._top); QShortcut(QKeySequence('F8'),self,self.timer.stop); QShortcut(QKeySequence('Ctrl+C'),self,self.copy)
    def _top(self,v): self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint,v); self.show()
    def refresh(self):
        self.current=self.service.inspect_at_cursor(self.backend.currentText()); self.text.setPlainText(json.dumps(to_plain(self.current),ensure_ascii=False,indent=2))
    def copy(self): QApplication.clipboard().setText(self.text.toPlainText())
