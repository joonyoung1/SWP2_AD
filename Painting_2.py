from PyQt5.QtWidgets import QMainWindow, QApplication, QAction, QWidgetAction, QFileDialog, QColorDialog
from PyQt5.QtGui import QImage, QPainter, QPen, QTransform, QPolygon, QClipboard
from PyQt5.QtCore import Qt, QPoint
from brushsizepicker import BrushSizePicker
from transaction import Transaction
from figuresetting import FigureSetting
from imagefromweb import ImageFromWeb
import sys
from urllib import parse, request
import random


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
        self.fullFill = False
        self.backUp = None
        self.clipboardImage = None
        self.hdr = {'User-Agent': 'Mozilla/5.0'}

        mainMenu = self.menuBar()
        fileMenu = mainMenu.addMenu("File")
        modify = mainMenu.addMenu("Modify")
        brushStyle = mainMenu.addMenu("Brush Style")
        brushSize = mainMenu.addMenu("Brush Size")
        colorPicker = QAction('Color Picker', self)
        drawingMenu = mainMenu.addMenu("Drawing")
        imageSearch = QAction('Image Search', self)

        fileMenuSetting = [{'name': 'Save', 'shortcut': 'Ctrl+S', 'callback': self.save},
                           {'name': 'Load', 'shortcut': 'Ctrl+O', 'callback': self.load},
                           {'name': 'Clear', 'shortcut': 'Ctrl+C', 'callback': self.clear},
                           {'name': 'Undo', 'shortcut': 'Ctrl+Z', 'callback': self.undoAndRedo},
                           {'name': 'Redo', 'shortcut': 'Ctrl+Shift+Z', 'callback': self.undoAndRedo},
                           {'name': 'Paste', 'shortcut': 'Ctrl+V', 'callback': self.paste}]

        for setting in fileMenuSetting:
            action = QAction(setting['name'], self)
            action.setShortcut(setting['shortcut'])
            action.triggered.connect(setting['callback'])
            fileMenu.addAction(action)

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

        drawingMenu.aboutToHide.connect(self.getDrawingOption)
        optionSettingAction = QWidgetAction(self)
        self.figureSetting = FigureSetting()
        optionSettingAction.setDefaultWidget(self.figureSetting)
        drawingMenu.addAction(optionSettingAction)

        for figure in ['Rectangle', 'Circle', 'Line']:
            drawAction = QAction(figure, self)
            drawAction.triggered.connect(self.changeBrush)
            drawingMenu.addAction(drawAction)

        brushSize.aboutToHide.connect(self.getSize)
        sizePickAction = QWidgetAction(self)
        self.sizeSlider = BrushSizePicker(1, 200, self.brushSize)
        sizePickAction.setDefaultWidget(self.sizeSlider)
        brushSize.addAction(sizePickAction)

        colorPicker.triggered.connect(self.pickColor)
        mainMenu.addAction(colorPicker)

        imageSearch.triggered.connect(self.searchImage)
        mainMenu.addAction(imageSearch)

        self.transaction = Transaction(20, self.image.copy(self.image.rect()))
        QApplication.clipboard().dataChanged.connect(self.copy)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self.brushStyle in ['Pen', 'Eraser', 'Spray']:
                self.drawing = True
                self.lastPoint = event.pos()
                painter = QPainter(self.image)
                if self.brushStyle == 'Pen':
                    painter.setPen(QPen(self.brushColor, self.brushSize, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
                    painter.drawPoint(event.pos())
                elif self.brushStyle == 'Spray':
                    painter.setPen(QPen(self.brushColor, 1))
                    for n in range(self.brushSize**2 // 10):
                        x = random.gauss(0, self.brushSize // 4)
                        y = random.gauss(0, self.brushSize // 4)
                        painter.drawPoint(event.x() + x, event.y() + y)
                elif self.brushStyle == 'Eraser':
                    painter.setBrush(Qt.white)
                    painter.setPen(Qt.white)
                    x = event.x() - self.brushSize / 2
                    y = event.y() - self.brushSize / 2
                    dx = dy = self.brushSize
                    painter.drawRect(x, y, dx, dy)
                self.update()
            elif self.brushStyle in ['Rectangle', 'Circle', 'Line']:
                self.drawing = True
                self.lastPoint = event.pos()
                self.backUp = self.image.copy(self.image.rect())

    def mouseMoveEvent(self, event):
        if self.drawing:
            # painter = QPainter(self.image)
            # image = QImage('/home/user/사진/autumn_leaves_PNG3611.png')
            # image = image.scaledToHeight(self.brushSize)
            # transform = QTransform()
            # transform.rotate(random.randint(0, 360))
            # image = image.transformed(transform)
            # painter.drawImage(event.x() - image.width() / 2, event.y() - image.height() / 2, image)
            # self.update()
            if self.brushStyle in ['Pen', 'Eraser', 'Spray']:
                painter = QPainter(self.image)
                if self.brushStyle == 'Pen':
                    painter.setPen(QPen(self.brushColor, self.brushSize, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
                    painter.drawLine(self.lastPoint, event.pos())
                elif self.brushStyle == 'Spray':
                    painter.setPen(QPen(self.brushColor, 1))
                    for n in range(self.brushSize**2 // 10):
                        x = random.gauss(0, self.brushSize // 4)
                        y = random.gauss(0, self.brushSize // 4)
                        painter.drawPoint(event.x() + x, event.y() + y)
                elif self.brushStyle == 'Eraser':
                    painter.setBrush(Qt.white)
                    painter.setPen(Qt.white)
                    dx = dy = self.brushSize
                    x1 = event.x() - dx / 2
                    y1 = event.y() - dy / 2
                    x2 = self.lastPoint.x() - dx / 2
                    y2 = self.lastPoint.y() - dy / 2
                    polygons = [QPolygon([QPoint(x1, y1), QPoint(x2, y2), QPoint(x2+dx, y2+dy), QPoint(x1+dx, y1+dy)]),
                                QPolygon([QPoint(x1, y1+dy), QPoint(x2, y2+dy), QPoint(x2+dx, y2), QPoint(x1+dx, y1)])]
                    for polygon in polygons:
                        painter.drawPolygon(polygon)
                    painter.drawRect(x1, y1, dx, dy)
                self.lastPoint = event.pos()
                self.update()
            elif self.brushStyle in ['Rectangle', 'Circle', 'Line']:
                self.image = self.backUp.copy(self.image.rect())
                painter = QPainter(self.image)
                painter.setPen(QPen(self.brushColor, self.brushSize, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
                if self.brushStyle == 'Rectangle':
                    x, y = self.lastPoint.x(), self.lastPoint.y()
                    dx, dy = event.pos().x() - x, event.pos().y() - y
                    if self.fullFill:
                        painter.setBrush(self.brushColor)
                    painter.drawRect(x, y, dx, dy)
                elif self.brushStyle == 'Circle':
                    x, y = self.lastPoint.x(), self.lastPoint.y()
                    dx, dy = event.pos().x() - x, event.pos().y() - y
                    if self.fullFill:
                        painter.setBrush(self.brushColor)
                    painter.drawEllipse(x, y, dx, dy)
                elif self.brushStyle == 'Line':
                    x1, y1 = self.lastPoint.x(), self.lastPoint.y()
                    x2, y2 = event.x(), event.y()
                    painter.drawLine(x1, y1, x2, y2)
                self.update()

    def mouseReleaseEvent(self, event):
        self.lastPoint = event.pos()
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
        if filePath == "":
            return

        newImage = QImage(filePath)
        self.resize(newImage.width(), newImage.height())
        self.image = newImage
        self.transaction.addData(self.image.copy(self.image.rect()))

    def clear(self):
        self.image.fill(Qt.white)
        self.update()
        self.transaction.addData(self.image.copy(self.image.rect()))

    def undoAndRedo(self):
        command = self.sender().text()
        if command == 'Undo':
            data = self.transaction.undo()
        elif command == 'Redo':
            data = self.transaction.redo()
        if data:
            self.resize(data.width(), data.height())
            self.image = data.copy()
            self.update()

    def copy(self):
        self.clipboardImage = QApplication.clipboard().image(QClipboard.Clipboard)

    def paste(self):
        if self.clipboardImage and not self.clipboardImage.isNull():
            self.image = self.clipboardImage
            self.resize(self.image.size())
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

    def getDrawingOption(self):
        self.fullFill = self.figureSetting.getSetting()

    def pickColor(self):
        self.brushColor = QColorDialog.getColor()

    def searchImage(self):
        imgSearchDialog = ImageFromWeb()
        imgSearchDialog.exec_()
        searchedImage = imgSearchDialog.image
        if searchedImage:
            self.image = searchedImage
            while self.image.width() >= 1920 or self.image.height() >= 1080:
                self.image = self.image.scaled(self.image.width() // 2, self.image.height() // 2, Qt.KeepAspectRatio)
            self.resize(self.image.width(), self.image.height())
            self.update()
            self.transaction.addData(self.image.copy(self.image.rect()))

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

            req = request.Request(decoded['https://www.google.com/imgres?imgurl'][0], headers=self.hdr)
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