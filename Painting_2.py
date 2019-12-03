from PyQt5.QtWidgets import QMainWindow, QApplication, QAction, QWidgetAction, QFileDialog, QColorDialog
from PyQt5.QtGui import QImage, QPainter, QPen, QTransform
from PyQt5.QtCore import Qt, QPoint
from brushsizepicker import BrushSizePicker
from transaction import Transaction
import sys, random
from urllib import parse, request


class Window(QMainWindow):

    def __init__(self):
        super().__init__()

        title = "Paint Application"
        top = 100
        left = 100
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
        self.brushStyle = 'Pen'

        mainMenu = self.menuBar()
        fileMenu = mainMenu.addMenu("File")
        modify = mainMenu.addMenu("Modify")
        brushStyle = mainMenu.addMenu("Brush Style")
        brushSize = mainMenu.addMenu("Brush Size")
        colorPicker = QAction('Color Picker', self)

        saveAction = QAction("Save", self)
        saveAction.setShortcut("Ctrl+S")
        fileMenu.addAction(saveAction)
        saveAction.triggered.connect(self.save)

        loadAction = QAction("Load", self)
        loadAction.setShortcut("Ctrl+O")
        fileMenu.addAction(loadAction)
        loadAction.triggered.connect(self.load)

        clearAction = QAction("Clear", self)
        clearAction.setShortcut("Ctrl+C")
        fileMenu.addAction(clearAction)
        clearAction.triggered.connect(self.clear)

        undoAction = QAction("Undo", self)
        undoAction.setShortcut("Ctrl+Z")
        fileMenu.addAction(undoAction)
        undoAction.triggered.connect(self.undo)

        redoAction = QAction("Redo", self)
        redoAction.setShortcut("Ctrl+Shift+Z")
        fileMenu.addAction(redoAction)
        redoAction.triggered.connect(self.redo)

        for angle in [90, 180, 270]:
            rotateAction = QAction("Rotate " + str(angle), self)
            rotateAction.triggered.connect(self.rotate)
            modify.addAction(rotateAction)

        for flip in ['Vertically', 'Horizontally']:
            flipAction = QAction("filp " + flip, self)
            flipAction.triggered.connect(self.flip)
            modify.addAction(flipAction)

        for brushType in ['Pen', 'Eraser', 'Spray']:
            brushAction = QAction(brushType, self)
            brushAction.triggered.connect(self.changeBrush)
            brushStyle.addAction(brushAction)

        brushSize.aboutToHide.connect(self.getSize)
        sizePickAction = QWidgetAction(self)
        self.sizeSlider = BrushSizePicker(1, 200, self.brushSize)
        sizePickAction.setDefaultWidget(self.sizeSlider)
        brushSize.addAction(sizePickAction)

        colorPicker.triggered.connect(self.pickColor)
        mainMenu.addAction(colorPicker)

        self.transaction = Transaction(20, self.image.copy(self.image.rect()))

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drawing = True
            self.lastPoint = event.pos()
            painter = QPainter(self.image)
            if self.brushStyle == 'Pen':
                painter.setPen(QPen(self.brushColor, self.brushSize, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
                painter.drawPoint(event.pos())
            elif self.brushStyle == 'Spray':
                painter.setPen(QPen(self.brushColor, 1))
                for n in range(self.brushSize**2 // 20):
                    x = random.gauss(0, self.brushSize // 4)
                    y = random.gauss(0, self.brushSize // 4)
                    painter.drawPoint(event.x() + x, event.y() + y)
            self.update()

    def mouseMoveEvent(self, event):
        if self.drawing:
            painter = QPainter(self.image)
            if self.brushStyle == 'Pen':
                painter.setPen(QPen(self.brushColor, self.brushSize, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
                painter.drawLine(self.lastPoint, event.pos())
            elif self.brushStyle == 'Spray':
                painter.setPen(QPen(self.brushColor, 1))
                for n in range(self.brushSize**2 // 20):
                    x = random.gauss(0, self.brushSize // 4)
                    y = random.gauss(0, self.brushSize // 4)
                    painter.drawPoint(event.x() + x, event.y() + y)
            self.lastPoint = event.pos()
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drawing = False
        self.transaction.addData(self.image.copy(self.image.rect()))

    def paintEvent(self, event):
        canvasPainter = QPainter(self)
        canvasPainter.drawImage(self.rect(), self.image, self.image.rect())

    def save(self):
        filePath, type = QFileDialog.getSaveFileName(self, "Save Image", "",
                                               "PNG(*.png);;JPEG(*.jpg *.jpeg);;All Files(*.*) ")

        if filePath == "":
            return
        self.image.save(filePath)

    def load(self):
        filePath, type = QFileDialog.getOpenFileName(self, "Import Image", "",
                                               "PNG(*.png);;JPEG(*.jpg *.jpeg);;All Files(*.*) ")
        newImage = QImage(filePath)
        self.resize(newImage.width(), newImage.height())
        self.image = newImage
        self.transaction.addData(self.image.copy(self.image.rect()))

    def clear(self):
        self.image.fill(Qt.white)
        self.update()

    def undo(self):
        data = self.transaction.undo()
        if data:
            self.resize(data.width(), data.height())
            self.image = data.copy()
            self.update()

    def redo(self):
        data = self.transaction.redo()
        if data:
            self.resize(data.width(), data.height())
            self.image = data.copy()
            self.update()

    def getSize(self):
        self.brushSize = self.sizeSlider.getSize()

    def rotate(self):
        angle = int(list(self.sender().text().split())[1])
        transform = QTransform()
        transform.rotate(angle)
        self.image = self.image.transformed(transform)
        self.setGeometry(self.pos().x(), self.pos().y() + 30, self.image.width(), self.image.height())
        self.transaction.addData(self.image.copy(self.image.rect()))
        self.update()

    def flip(self):
        option = list(self.sender().text().split())[1]
        if option == 'Vertically':
            self.image = self.image.mirrored(False, True)
        else:
            self.image = self.image.mirrored(True, False)
        self.update()

    def changeBrush(self):
        brushType = self.sender().text()
        self.brushStyle = brushType
        print(self.brushStyle)

    def pickColor(self):
        self.brushColor = QColorDialog.getColor()

    def resizeEvent(self, e):
        resizedImage = QImage(e.size(), QImage.Format_RGB32)
        resizedImage.fill(Qt.white)
        painter = QPainter(resizedImage)
        painter.drawImage(self.image.rect(), self.image, self.image.rect())
        self.image = resizedImage
        self.update()

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
            decoded = parse.parse_qs(myUrl.toString())
            hdr = {'User-Agent': 'Mozilla/5.0'}
            req = request.Request(decoded['https://www.google.com/imgres?imgurl'][0], headers=hdr)
            newImage = QImage()
            newImage.loadFromData(request.urlopen(req).read())

        self.resize(newImage.width(), newImage.height())
        self.image = newImage
        self.update()
        self.transaction.addData(self.image.copy(self.image.rect()))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    app.exec()