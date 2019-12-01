from PyQt5.QtWidgets import QMainWindow, QApplication, QAction, QWidgetAction, QFileDialog, QColorDialog, QWidget
from PyQt5.QtWidgets import QSlider
from PyQt5.QtGui import QImage, QPainter, QPen, QTransform
from PyQt5.QtCore import Qt, QPoint
from brushsizepicker import BrushSizePicker
import sys
import requests
from bs4 import BeautifulSoup
import urllib.request


class Window(QMainWindow):

    def __init__(self):
        super().__init__()

        title = "Paint Application"
        top = 400
        left = 400
        width = 800
        height = 600

        self.setAcceptDrops(True)
        self.setWindowTitle(title)
        self.setGeometry(top, left, width, height)

        self.image = QImage(self.size(), QImage.Format_RGB32)
        self.image.fill(Qt.white)

        self.drawing = False
        self.brushSize = 2
        self.brushColor = Qt.black
        self.lastPoint = QPoint()

        mainMenu = self.menuBar()
        fileMenu = mainMenu.addMenu("File")
        brushSize = mainMenu.addMenu("Brush Size")
        brushSize.aboutToHide.connect(self.test)
        rotate = mainMenu.addMenu("Rotate")
        colorPicker = QAction('Color Picker', self)
        colorPicker.triggered.connect(self.pickColor)
        mainMenu.addAction(colorPicker)

        saveAction = QAction("save", self)
        saveAction.setShortcut("Ctrl+S")
        fileMenu.addAction(saveAction)
        saveAction.triggered.connect(self.save)

        clearAction = QAction("clear", self)
        clearAction.setShortcut("Ctrl+C")
        fileMenu.addAction(clearAction)
        clearAction.triggered.connect(self.clear)

        threepxAction = QAction("3px", self)
        brushSize.addAction(threepxAction)
        threepxAction.triggered.connect(self.threePixel)

        fivepxAction = QAction("5px", self)
        brushSize.addAction(fivepxAction)
        fivepxAction.triggered.connect(self.fivePixel)

        sevenpxAction = QAction("7px", self)
        brushSize.addAction(sevenpxAction)
        sevenpxAction.triggered.connect(self.sevenPixel)

        sizePickAction = QWidgetAction(self)
        self.sizeSlider = BrushSizePicker(1, 200, self.brushSize)
        sizePickAction.setDefaultWidget(self.sizeSlider)
        brushSize.addAction(sizePickAction)
        sizePickAction.changed.connect(self.test)

        rotate90Action = QAction("90", self)
        rotate.addAction(rotate90Action)
        rotate90Action.triggered.connect(self.rotate90)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drawing = True
            self.lastPoint = event.pos()
            painter = QPainter(self.image)
            painter.setPen(QPen(self.brushColor, self.brushSize, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            painter.drawPoint(event.pos())
            self.update()

    def mouseMoveEvent(self, event):
        if self.drawing:
            painter = QPainter(self.image)
            painter.setPen(QPen(self.brushColor, self.brushSize, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            painter.drawLine(self.lastPoint, event.pos())
            self.lastPoint = event.pos()
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drawing = False

    def paintEvent(self, event):
        canvasPainter = QPainter(self)
        canvasPainter.drawImage(self.rect(), self.image, self.image.rect())

    def save(self):
        filePath, type = QFileDialog.getSaveFileName(self, "Save Image", "",
                                               "PNG(*.png);;JPEG(*.jpg *.jpeg);;All Files(*.*) ")

        if filePath == "":
            return
        self.image.save(filePath)

    def clear(self):
        self.image.fill(Qt.white)
        self.update()

    def threePixel(self):
        self.brushSize = 3

    def fivePixel(self):
        self.brushSize = 5

    def sevenPixel(self):
        self.brushSize = 7

    def ninePixel(self):
        self.brushSize = 9

    def test(self):
        self.brushSize = self.sizeSlider.getSize()

    def rotate90(self):
        transform = QTransform()
        transform.rotate(90)
        self.image = self.image.transformed(transform)
        self.setGeometry(self.pos().x(), self.pos().y() + 30, self.image.width(), self.image.height())


    def pickColor(self):
        self.brushColor = QColorDialog.getColor()

    def resizeEvent(self, e):
        resizedImage = QImage(e.size(), QImage.Format_RGB32)
        resizedImage.fill(Qt.white)
        painter = QPainter(resizedImage)
        painter.drawImage(self.image.rect(), self.image, self.image.rect())
        self.image = resizedImage

    def dragEnterEvent(self, e):
        m = e.mimeData()
        if m.hasUrls():
            e.accept()
        else:
            e.ignore()

    def dropEvent(self, e):
        myUrl = e.mimeData().urls()[0]
        if myUrl.isLocalFile():
            newImage = QImage(myUrl.toLocalFile())
        else:
            html = requests.get(myUrl.toString())
            soup = BeautifulSoup(html.text, 'html.parser')
            html.close()

            data = soup.findAll('div', {'id': 'il_ic'})
            result = (data[0].findAll('img'))
            url = result[0]['src']
            newImage = QImage()
            newImage.loadFromData(urllib.request.urlopen(url).read())

        self.resize(newImage.width(), newImage.height())
        self.image = newImage
        self.update()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    app.exec()