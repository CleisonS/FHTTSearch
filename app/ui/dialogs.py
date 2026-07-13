from PySide6.QtWidgets import QMessageBox
def show_about(parent): QMessageBox.information(parent, 'Sobre', 'UNM Inspector\nFerramenta passiva de diagnóstico de interfaces Windows.')
def show_error(parent, msg): QMessageBox.critical(parent, 'Erro', msg)
