from PyQt5.QtWidgets import QWidget, QCheckBox, QHBoxLayout


class CheckboxSetting(QWidget):
    def __init__(self, name):
        super().__init__()

        self.option = QCheckBox(name)
        self.setFixedHeight(32)
        hBox = QHBoxLayout()
        hBox.addWidget(self.option)
        self.setLayout(hBox)

    def getSetting(self):
        return self.option.isChecked()
