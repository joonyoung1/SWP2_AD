from PyQt5.QtWidgets import QWidget, QSlider, QHBoxLayout, QPushButton, QLineEdit, QLabel
from PyQt5.QtCore import Qt


class BrushSettingSlider(QWidget):
    def __init__(self, minValue, maxValue, baseValue, name):
        super().__init__()
        self.minValue = minValue
        self.maxValue = maxValue
        self.brushSize = baseValue

        hBox = QHBoxLayout()

        self.sizeViewer = QLineEdit(str(baseValue))
        self.sizeViewer.setFixedWidth(30)
        self.sizeViewer.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.sizeViewer.textChanged.connect(self.setValueText)

        nameLabel = QLabel(name)

        buttonSetting = [{'name': '<<', 'width': 23},
                         {'name': '<', 'width': 18},
                         {'name': '>', 'width': 18},
                         {'name': '>>', 'width': 23}]

        buttons = []
        for setting in buttonSetting:
            button = QPushButton(setting['name'])
            button.setFixedWidth(setting['width'])
            button.clicked.connect(self.setValueButton)
            buttons.append(button)

        self.valueSlider = QSlider(Qt.Horizontal)
        self.valueSlider.setMinimum(minValue)
        self.valueSlider.setMaximum(maxValue)
        self.valueSlider.valueChanged.connect(self.setValueSlider)
        self.valueSlider.setValue(baseValue)
        self.valueSlider.setTickInterval(40)
        self.valueSlider.setTickPosition(QSlider.TicksAbove)

        hBox.addWidget(nameLabel)
        hBox.addWidget(buttons[0])
        hBox.addWidget(buttons[1])
        hBox.addWidget(self.valueSlider)
        hBox.addWidget(buttons[2])
        hBox.addWidget(buttons[3])
        hBox.addWidget(self.sizeViewer)

        self.setLayout(hBox)

    def setValueButton(self):
        sender = self.sender()
        if '<' in sender.text():
            if sender.text() == '<':
                value = -1
            else:
                value = -5
            self.brushSize = max(self.minValue, self.valueSlider.value() + value)
        else:
            if sender.text() == '>':
                value = 1
            else:
                value = 5
            self.brushSize = min(self.maxValue, self.valueSlider.value() + value)
        self.valueSlider.setValue(self.brushSize)
        self.sizeViewer.setText(str(self.brushSize))

    def setValueText(self):
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
            self.valueSlider.setValue(size)

    def setValueSlider(self):
        self.sizeViewer.setText(str(self.valueSlider.value()))
        self.brushSize = self.valueSlider.value()

    def getValue(self):
        return self.brushSize
