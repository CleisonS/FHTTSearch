import json, logging
from PySide6.QtWidgets import *
from PySide6.QtCore import QThread, QUrl
from PySide6.QtGui import QDesktopServices
from app.ui.widgets.window_table import WindowTable
from app.ui.widgets.control_tree import ControlTree
from app.ui.widgets.properties_panel import PropertiesPanel
from app.ui.widgets.log_panel import LogPanel, QtLogHandler
from app.ui.live_inspector_window import LiveInspectorWindow
from app.workers.scan_worker import ScanWorker
from app.workers.inspection_worker import InspectionWorker
from app.services.window_service import matches_window_filter
from app.services.export_service import ExportService
from app.services.report_service import ReportService
from app.models.inspection_result import InspectionResult
from app.constants import OUTPUT_DIR
class MainWindow(QMainWindow):
    def __init__(self, config):
        super().__init__(); self.config=config; self.windows=[]; self.inspection=InspectionResult(); self.setWindowTitle('UNM Inspector'); self.resize(1280,800); self.setMinimumSize(1024,700); self._build(); self.refresh_windows()
    def _build(self):
        self._menus(); root=QWidget(); self.setCentralWidget(root); v=QVBoxLayout(root); btns=QHBoxLayout(); v.addLayout(btns)
        for name,slot in [('Atualizar janelas',self.refresh_windows),('Detectar backends',self.inspect_selected),('Inspecionar controles',self.inspect_selected),('Live Inspector',self.open_live),('Capturar janela',self.capture_window),('Capturar tela',self.capture_desktop),('Exportar TXT',self.export_txt),('Exportar CSV',self.export_csv),('Exportar JSON',self.export_json),('Exportar relatório completo',self.export_report)]: b=QPushButton(name); b.clicked.connect(slot); btns.addWidget(b)
        split=QSplitter(); v.addWidget(split,1); left=QWidget(); ll=QVBoxLayout(left); filt=QHBoxLayout(); self.filter=QLineEdit(); self.filter.setPlaceholderText('Filtrar por título/processo'); self.only_unm=QCheckBox('Somente UNM2000'); self.only_visible=QCheckBox('Somente visíveis'); [filt.addWidget(x) for x in [self.filter,self.only_unm,self.only_visible]]; ll.addLayout(filt); self.table=WindowTable(); ll.addWidget(self.table); split.addWidget(left)
        self.tree=ControlTree(); self.tree.on_selected(self.props.show_control if hasattr(self,'props') else lambda c:None); split.addWidget(self.tree); self.props=PropertiesPanel(); self.tree.on_selected(self.props.show_control); split.addWidget(self.props)
        self.tabs=QTabWidget(); v.addWidget(self.tabs); self.log=LogPanel(); self.summary=QTextEdit(); self.readiness=QTextEdit(); self.raw=QTextEdit(); [x.setReadOnly(True) for x in [self.summary,self.readiness,self.raw]]; self.tabs.addTab(self.log,'Log'); self.tabs.addTab(self.summary,'Resumo'); self.tabs.addTab(self.readiness,'Automation Readiness'); self.tabs.addTab(self.raw,'Dados brutos')
        h=QtLogHandler(self.log); h.setFormatter(logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')); logging.getLogger().addHandler(h); self.statusBar().showMessage('Pronto'); self.filter.textChanged.connect(self.apply_filters); self.only_unm.toggled.connect(self.apply_filters); self.only_visible.toggled.connect(self.apply_filters)
    def _menus(self):
        m=self.menuBar(); arq=m.addMenu('Arquivo'); arq.addAction('Atualizar janelas',self.refresh_windows); arq.addAction('Exportar',self.export_report); arq.addAction('Abrir pasta de saída',lambda: QDesktopServices.openUrl(QUrl.fromLocalFile(str(OUTPUT_DIR.resolve())))); arq.addAction('Sair',self.close)
        ins=m.addMenu('Inspeção'); ins.addAction('Detectar backends',self.inspect_selected); ins.addAction('Inspecionar janela selecionada',self.inspect_selected); ins.addAction('Abrir Live Inspector',self.open_live); ins.addAction('Capturar screenshot',self.capture_desktop)
        aju=m.addMenu('Ajuda'); aju.addAction('Sobre',lambda: QMessageBox.information(self,'Sobre','UNM Inspector'))
    def _run_thread(self, worker, done):
        t=QThread(self); worker.moveToThread(t); t.started.connect(worker.run); worker.result.connect(done); worker.error.connect(lambda e: QMessageBox.warning(self,'Aviso',e)); worker.status.connect(self.statusBar().showMessage); worker.finished.connect(t.quit); worker.finished.connect(worker.deleteLater); t.finished.connect(t.deleteLater); t.start()
    def refresh_windows(self): self._run_thread(ScanWorker(), self._windows_done)
    def _windows_done(self, wins): self.windows=wins; self.apply_filters(); self.statusBar().showMessage(f'{len(wins)} janelas encontradas')
    def apply_filters(self): self.table.set_windows([w for w in self.windows if matches_window_filter(w,self.filter.text(),self.only_unm.isChecked(),self.only_visible.isChecked())])
    def selected(self):
        w=self.table.selected_window()
        if not w: QMessageBox.information(self,'Nenhuma janela selecionada','Selecione uma janela.'); return None
        return w
    def inspect_selected(self):
        w=self.selected();
        if w: self._run_thread(InspectionWorker(w,self.config), self._inspection_done)
    def _inspection_done(self,res):
        self.inspection=res; self.tree.populate(res.controls_win32+res.controls_uia); self.readiness.setPlainText(json.dumps(__import__('app.utils.serialization').utils.serialization.to_plain(res.readiness),ensure_ascii=False,indent=2)); self.raw.setPlainText(json.dumps(__import__('app.utils.serialization').utils.serialization.to_plain(res),ensure_ascii=False,indent=2)); self.summary.setPlainText(f'Inspeção concluída: Win32={len(res.controls_win32)} UIA={len(res.controls_uia)}')
    def open_live(self): self.live=LiveInspectorWindow(self.config); self.live.show()
    def export_txt(self): ExportService().export_txt(self.inspection, OUTPUT_DIR/'report.txt')
    def export_csv(self): ExportService().export_controls_csv(self.inspection.controls_win32+self.inspection.controls_uia, OUTPUT_DIR/'controls.csv')
    def export_json(self): ExportService().export_json(self.inspection, OUTPUT_DIR/'report.json')
    def export_report(self): folder,z=ReportService().create_full_report(self.inspection,self.windows); QMessageBox.information(self,'Relatório gerado',f'{z}')
    def capture_desktop(self): from app.services.screenshot_service import ScreenshotService; QMessageBox.information(self,'Screenshot',str(ScreenshotService().capture_desktop()))
    def capture_window(self):
        w=self.selected();
        if w:
            from app.services.screenshot_service import ScreenshotService; QMessageBox.information(self,'Screenshot',str(ScreenshotService().capture_window(w)))
