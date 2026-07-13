from __future__ import annotations

import json
import logging
from typing import Callable

from PySide6.QtCore import QThread, QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QCheckBox,
    QHBoxLayout,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSplitter,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from app.constants import OUTPUT_DIR
from app.models.inspection_result import InspectionResult
from app.services.export_service import ExportService
from app.services.report_service import ReportService
from app.services.window_service import matches_window_filter
from app.ui.live_inspector_window import LiveInspectorWindow
from app.ui.widgets.control_tree import ControlTree
from app.ui.widgets.log_panel import LogPanel, QtLogHandler
from app.ui.widgets.properties_panel import PropertiesPanel
from app.ui.widgets.window_table import WindowTable
from app.utils.serialization import to_plain
from app.workers.backend_worker import BackendWorker
from app.workers.inspection_worker import InspectionWorker
from app.workers.scan_worker import ScanWorker

LOG = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    def __init__(self, config: dict) -> None:
        super().__init__()
        self.config = config
        self.windows = []
        self.inspection = InspectionResult()
        self._threads: list[QThread] = []
        self._workers: list[object] = []
        self._busy = False
        self._has_inspection = False
        self.setWindowTitle("UNM Inspector")
        self.resize(1280, 800)
        self.setMinimumSize(1024, 700)
        self._build()
        self.refresh_windows()

    def _build(self) -> None:
        self._menus()
        root = QWidget()
        self.setCentralWidget(root)
        layout = QVBoxLayout(root)
        button_bar = QHBoxLayout()
        layout.addLayout(button_bar)

        self.refresh_button = self._add_button(button_bar, "Atualizar janelas", self.refresh_windows)
        self.detect_button = self._add_button(button_bar, "Detectar backends", self.detect_backends_selected)
        self.inspect_button = self._add_button(button_bar, "Inspecionar controles", self.inspect_controls_selected)
        self.live_button = self._add_button(button_bar, "Live Inspector", self.open_live)
        self.cancel_button = self._add_button(button_bar, "Cancelar", self.cancel_current_workers)
        self.capture_window_button = self._add_button(button_bar, "Capturar janela", self.capture_window)
        self.capture_desktop_button = self._add_button(button_bar, "Capturar tela", self.capture_desktop)
        self.export_txt_button = self._add_button(button_bar, "Exportar TXT", self.export_txt)
        self.export_csv_button = self._add_button(button_bar, "Exportar CSV", self.export_csv)
        self.export_json_button = self._add_button(button_bar, "Exportar JSON", self.export_json)
        self.export_report_button = self._add_button(button_bar, "Exportar relatório completo", self.export_report)

        splitter = QSplitter()
        layout.addWidget(splitter, 1)

        left = QWidget()
        left_layout = QVBoxLayout(left)
        filter_layout = QHBoxLayout()
        self.filter = QLineEdit()
        self.filter.setPlaceholderText("Filtrar por título/processo/classe/PID/handle")
        self.only_unm = QCheckBox("Somente UNM2000")
        self.only_visible = QCheckBox("Somente visíveis")
        self.only_visible.setChecked(True)
        filter_layout.addWidget(self.filter)
        filter_layout.addWidget(self.only_unm)
        filter_layout.addWidget(self.only_visible)
        left_layout.addLayout(filter_layout)
        self.table = WindowTable()
        self.table.itemSelectionChanged.connect(self._update_actions)
        self.table.window_double_clicked.connect(lambda _window: self.detect_backends_selected())
        left_layout.addWidget(self.table)
        splitter.addWidget(left)

        self.tree = ControlTree()
        self.props = PropertiesPanel()
        self.tree.on_selected(self.props.show_control)
        splitter.addWidget(self.tree)
        splitter.addWidget(self.props)

        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)
        self.log = LogPanel()
        self.summary = QTextEdit()
        self.readiness = QTextEdit()
        self.raw = QTextEdit()
        for widget in (self.summary, self.readiness, self.raw):
            widget.setReadOnly(True)
        self.tabs.addTab(self.log, "Log")
        self.tabs.addTab(self.summary, "Resumo")
        self.tabs.addTab(self.readiness, "Automation Readiness")
        self.tabs.addTab(self.raw, "Dados brutos")
        self._install_log_handler()

        self.filter.textChanged.connect(self.apply_filters)
        self.only_unm.toggled.connect(self.apply_filters)
        self.only_visible.toggled.connect(self.apply_filters)
        self.statusBar().showMessage("Pronto")
        self._update_actions()

    def _add_button(self, layout: QHBoxLayout, text: str, slot: Callable[[], None]) -> QPushButton:
        button = QPushButton(text)
        button.clicked.connect(slot)
        layout.addWidget(button)
        return button

    def _install_log_handler(self) -> None:
        if getattr(self, "_qt_log_handler", None) is not None:
            return
        self._qt_log_handler = QtLogHandler(self.log)
        self._qt_log_handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))
        logging.getLogger().addHandler(self._qt_log_handler)

    def _menus(self) -> None:
        menu = self.menuBar()
        file_menu = menu.addMenu("Arquivo")
        file_menu.addAction("Atualizar janelas", self.refresh_windows)
        file_menu.addAction("Exportar", self.export_report)
        file_menu.addAction("Abrir pasta de saída", lambda: QDesktopServices.openUrl(QUrl.fromLocalFile(str(OUTPUT_DIR.resolve()))))
        file_menu.addAction("Sair", self.close)
        inspection_menu = menu.addMenu("Inspeção")
        inspection_menu.addAction("Detectar backends", self.detect_backends_selected)
        inspection_menu.addAction("Inspecionar janela selecionada", self.inspect_controls_selected)
        inspection_menu.addAction("Abrir Live Inspector", self.open_live)
        inspection_menu.addAction("Capturar screenshot", self.capture_desktop)
        help_menu = menu.addMenu("Ajuda")
        help_menu.addAction("Sobre", lambda: QMessageBox.information(self, "Sobre", "UNM Inspector"))

    def _run_worker(self, worker: object, result_callback: Callable[[object], None]) -> None:
        if self._busy:
            self.statusBar().showMessage("Aguarde a operação atual terminar ou clique em Cancelar.")
            return
        thread = QThread(self)
        self._threads.append(thread)
        self._workers.append(worker)
        worker.moveToThread(thread)
        thread.started.connect(worker.run)
        worker.started.connect(lambda: self._set_busy(True))
        worker.result.connect(result_callback)
        worker.status.connect(self.statusBar().showMessage)
        worker.error.connect(self._worker_error)
        worker.cancelled.connect(lambda: self.statusBar().showMessage("Operação cancelada."))
        worker.finished.connect(thread.quit)
        worker.finished.connect(worker.deleteLater)
        thread.finished.connect(lambda t=thread, w=worker: self._cleanup_worker(t, w))
        thread.finished.connect(thread.deleteLater)
        thread.start()

    def _cleanup_worker(self, thread: QThread, worker: object) -> None:
        if thread in self._threads:
            self._threads.remove(thread)
        if worker in self._workers:
            self._workers.remove(worker)
        self._set_busy(bool(self._threads))

    def _set_busy(self, busy: bool) -> None:
        self._busy = busy
        self.cancel_button.setEnabled(busy)
        self.refresh_button.setEnabled(not busy)
        self._update_actions()

    def _worker_error(self, message: str) -> None:
        LOG.error("Worker retornou erro: %s", message, exc_info=True)
        self.statusBar().showMessage(message)
        self.log.append(f"ERRO: {message}")
        QMessageBox.warning(self, "Aviso", message)

    def cancel_current_workers(self) -> None:
        for worker in list(self._workers):
            cancel = getattr(worker, "cancel", None)
            if callable(cancel):
                cancel()
        self.statusBar().showMessage("Cancelamento solicitado...")

    def refresh_windows(self) -> None:
        self.statusBar().showMessage("Listando janelas do Windows...")
        self._run_worker(ScanWorker(), self._windows_done)

    def _windows_done(self, windows: object) -> None:
        self.windows = list(windows)
        self.apply_filters()
        msg = f"{len(self.windows)} janelas encontradas"
        self.statusBar().showMessage(msg)
        LOG.info(msg)
        if not self.windows:
            QMessageBox.warning(
                self,
                "Nenhuma janela enumerada",
                "Nenhuma janela foi enumerada. Consulte o log para verificar falha no pywin32, permissões ou ambiente de execução.",
            )

    def apply_filters(self) -> None:
        selected = self.table.selected_window()
        preserve = selected.handle if selected else None
        filtered = [
            window
            for window in self.windows
            if matches_window_filter(window, self.filter.text(), self.only_unm.isChecked(), self.only_visible.isChecked())
        ]
        self.table.set_windows(filtered, preserve)
        self._update_actions()

    def selected(self):
        window = self.table.selected_window()
        if window is None:
            QMessageBox.information(self, "Nenhuma janela selecionada", "Selecione uma janela.")
        return window

    def detect_backends_selected(self) -> None:
        window = self.selected()
        if window is not None:
            self._run_worker(BackendWorker(window), self._backend_done)

    def _backend_done(self, payload: object) -> None:
        window, win32, uia, classification = payload
        window.win32_available = win32.success
        window.uia_available = uia.success
        self.apply_filters()
        self.summary.setPlainText(
            f"Backend recomendado: {classification}\n"
            f"Win32: sucesso={win32.success}, controles={win32.controls_count}, erro={win32.error}\n"
            f"UIA: sucesso={uia.success}, controles={uia.controls_count}, erro={uia.error}"
        )
        if (not win32.success or win32.controls_count < 3) and (not uia.success or uia.controls_count < 3):
            self.summary.append(
                "\nO UNM2000 pode estar executando com privilégios superiores. "
                "Feche o Inspector e execute-o como administrador para comparar o resultado."
            )

    def inspect_controls_selected(self) -> None:
        window = self.selected()
        if window is not None:
            self._run_worker(InspectionWorker(window, self.config), self._inspection_done)

    def _inspection_done(self, result: object) -> None:
        self.inspection = result
        self._has_inspection = bool(result.controls_win32 or result.controls_uia)
        self.tree.populate_backend_roots(result.controls_win32, result.controls_uia)
        self.readiness.setPlainText(json.dumps(to_plain(result.readiness), ensure_ascii=False, indent=2))
        self.raw.setPlainText(json.dumps(to_plain(result), ensure_ascii=False, indent=2))
        self.summary.setPlainText(
            f"Inspeção concluída: Win32={len(result.controls_win32)} UIA={len(result.controls_uia)}\n"
            f"Erros parciais: {len(result.errors)}"
        )
        self._update_actions()

    def open_live(self) -> None:
        self.live = LiveInspectorWindow(self.config)
        self.live.show()

    def _require_inspection(self) -> bool:
        if not self._has_inspection:
            QMessageBox.information(self, "Inspeção necessária", "Execute uma inspeção antes de exportar.")
            return False
        return True

    def export_txt(self) -> None:
        if self._require_inspection():
            ExportService().export_txt(self.inspection, OUTPUT_DIR / "report.txt")

    def export_csv(self) -> None:
        if self._require_inspection():
            ExportService().export_controls_csv(self.inspection.controls_win32 + self.inspection.controls_uia, OUTPUT_DIR / "controls.csv")

    def export_json(self) -> None:
        if self._require_inspection():
            ExportService().export_json(self.inspection, OUTPUT_DIR / "report.json")

    def export_report(self) -> None:
        if self._require_inspection():
            _folder, zip_path = ReportService().create_full_report(self.inspection, self.windows)
            QMessageBox.information(self, "Relatório gerado", str(zip_path.resolve()))

    def capture_desktop(self) -> None:
        from app.services.screenshot_service import ScreenshotService

        QMessageBox.information(self, "Screenshot", str(ScreenshotService().capture_desktop().resolve()))

    def capture_window(self) -> None:
        window = self.selected()
        if window is None:
            return
        from app.services.screenshot_service import ScreenshotService

        QMessageBox.information(self, "Screenshot", str(ScreenshotService().capture_window(window).resolve()))

    def _update_actions(self) -> None:
        has_selection = self.table.selected_window() is not None
        for button in (self.detect_button, self.inspect_button, self.capture_window_button):
            button.setEnabled(has_selection and not self._busy)
        for button in (self.export_txt_button, self.export_csv_button, self.export_json_button, self.export_report_button):
            button.setEnabled(self._has_inspection and not self._busy)
        self.cancel_button.setEnabled(self._busy)

    def closeEvent(self, event) -> None:
        self.cancel_current_workers()
        for thread in list(self._threads):
            thread.quit()
            thread.wait(3000)
        super().closeEvent(event)
