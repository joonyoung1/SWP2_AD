from PyQt5.QtWidgets import QWidget, QSlider, QHBoxLayout, QPushButton, QLineEdit
from PyQt5.QtCore import Qt

class BrushSizePicker(QWidget):
    def __init__(self, minValue, maxValue, brushSize):
        super().__init__()
        self.minValue = minValue
        self.maxValue = maxValue
        self.brushSize = brushSize

        hBox = QHBoxLayout()

        self.sizeViewer = QLineEdit(str(brushSize))
        self.sizeViewer.setFixedWidth(30)
        self.sizeViewer.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.sizeViewer.textChanged.connect(self.setSizeText)

        decreaseButton = QPushButton('<')
        decreaseButton.clicked.connect(self.setSizeButton)
        decreaseButton.setFixedWidth(18)

        decreaseMoreButton = QPushButton('<<')
        decreaseMoreButton.clicked.connect(self.setSizeButton)
        decreaseMoreButton.setFixedWidth(23)

        increaseButton = QPushButton('>')
        increaseButton.clicked.connect(self.setSizeButton)
        increaseButton.setFixedWidth(18)

        increaseMoreButton = QPushButton('>>')
        increaseMoreButton.clicked.connect(self.setSizeButton)
        increaseMoreButton.setFixedWidth(23)

        self.sizeSlider = QSlider(Qt.Horizontal)
        self.sizeSlider.setMinimum(minValue)
        self.sizeSlider.setMaximum(maxValue)
        self.sizeSlider.valueChanged.connect(self.setSizeSlider)
        self.sizeSlider.setValue(brushSize)
        self.sizeSlider.setTickInterval(40)
        self.sizeSlider.setTickPosition(QSlider.TicksAbove)

        hBox.addWidget(decreaseMoreButton)
        hBox.addWidget(decreaseButton)
        hBox.addWidget(self.sizeSlider)
        hBox.addWidget(increaseButton)
        hBox.addWidget(increaseMoreButton)
        hBox.addWidget(self.sizeViewer)

        self.setLayout(hBox)

    def setSizeButton(self):
        sender = self.sender()
        if '<' in sender.text():
            if sender.text() == '<':
                value = -1
            else:
                value = -5
            self.brushSize = max(self.minValue, self.sizeSlider.value() + value)
        else:
            if sender.text() == '>':
                value = 1
            else:
                value = 5
            self.brushSize = min(self.maxValue, self.sizeSlider.value() + value)
        self.sizeSlider.setValue(self.brushSize)
        self.sizeViewer.setText(str(self.brushSize))

    def setSizeText(self):
        try:
            size = int(self.sender().text())
        except:
            size = 0
        if size != self.brushSize:
            if size > self.maxValue:
                self.brushSize = self.maxValue
                self.sizeViewer.setText(str(self.maxValue))
                size = self.maxValue
            elif size < self.minValue:
                self.brushSize = self.minValue
                self.sizeViewer.setText(str(self.minValue))
                size = self.minValue
            else:
                self.brushSize = size
            self.sizeSlider.setValue(size)

    def setSizeSlider(self):
        self.sizeViewer.setText(str(self.sizeSlider.value()))
        self.brushSize = self.sizeSlider.value()

    def getSize(self):
        return self.brushSize
