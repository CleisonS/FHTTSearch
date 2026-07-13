from PySide6.QtWidgets import QLabel
class StatusPanel(QLabel):
    def set_status(self, text): self.setText(text)
