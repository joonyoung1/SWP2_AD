from PyQt5.QtWidgets import QMainWindow, QApplication, QMenu, QMenuBar, QAction, QFileDialog
from PyQt5.QtGui import QImage, QPainter, QPen, QBrush, QPixmap, QTransform
from PyQt5.QtCore import Qt, QPoint, pyqtSignal, QUrl
import sys
import requests
from bs4 import BeautifulSoup
from pprint import pprint
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
        brushColor = mainMenu.addMenu("Brush Color")

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

        ninepxAction = QAction("9px", self)
        brushSize.addAction(ninepxAction)
        ninepxAction.triggered.connect(self.ninePixel)

        blackAction = QAction("Black", self)
        blackAction.setShortcut("Ctrl+B")
        brushColor.addAction(blackAction)
        blackAction.triggered.connect(self.blackColor)

        whitekAction = QAction("White", self)
        whitekAction.setShortcut("Ctrl+W")
        brushColor.addAction(whitekAction)
        whitekAction.triggered.connect(self.whiteColor)

        redAction = QAction("Red", self)
        redAction.setShortcut("Ctrl+R")
        brushColor.addAction(redAction)
        redAction.triggered.connect(self.redColor)

        greenAction = QAction("Green", self)
        greenAction.setShortcut("Ctrl+G")
        brushColor.addAction(greenAction)
        greenAction.triggered.connect(self.greenColor)

        yellowAction = QAction("Yellow", self)
        yellowAction.setShortcut("Ctrl+Y")
        brushColor.addAction(yellowAction)
        yellowAction.triggered.connect(self.yellowColor)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drawing = True
            self.lastPoint = event.pos()

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

    def blackColor(self):
        self.brushColor = Qt.black

    def whiteColor(self):
        self.brushColor = Qt.white

    def redColor(self):
        self.brushColor = Qt.red

    def greenColor(self):
        self.brushColor = Qt.green

    def yellowColor(self):
        # self.brushColor = Qt.yellow
        transform = QTransform()
        self.image.scaled(self.image.height(), self.image.width())
        transform.rotate(90)
        self.image = self.image.transformed(transform)
        self.update()

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