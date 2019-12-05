from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtWidgets import QLabel

class ClickLabel(QLabel):
    clicked = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setFixedSize(100, 100)
        self.setAlignment(Qt.AlignCenter)

    def mousePressEvent(self, event):
        self.clicked.emit()
        QLabel.mousePressEvent(self, event)