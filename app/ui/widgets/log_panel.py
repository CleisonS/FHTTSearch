import logging
from PySide6.QtWidgets import QTextEdit
class QtLogHandler(logging.Handler):
    def __init__(self, widget): super().__init__(); self.widget=widget
    def emit(self, record): self.widget.append(self.format(record))
class LogPanel(QTextEdit):
    def __init__(self): super().__init__(); self.setReadOnly(True)
