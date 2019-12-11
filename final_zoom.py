from PyQt5.QtWidgets import QMainWindow, QApplication, QAction, QWidgetAction, QFileDialog, QColorDialog, QLabel ,QHBoxLayout,QSizePolicy, QScrollArea
from PyQt5.QtGui import QImage, QPainter, QPen, QTransform, QPixmap, QPalette, QColor
from PyQt5.QtCore import Qt, QPoint
from brushsizepicker import BrushSizePicker
from transaction import Transaction
import sys, random
from urllib import parse, request


class Window(QMainWindow):

    def __init__(self):
        super().__init__()
        self.can = 0
        self.scaleFactor = 1.0

        title = "Paint Application"
        width = 800
        height = 600
        self.image = QImage(width,height, QImage.Format_ARGB32)
        self.image.fill(Qt.transparent)
        print("self.size",self.size())

        self.imagelabel = QLabel()
        self.imagelabel.setBackgroundRole(QPalette.Base)
        self.imagelabel.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.imagelabel.setScaledContents(True)




        self.imagelabel.setPixmap(QPixmap.fromImage(self.image))
        # self.imagelabel.resize(self.scaleFactor * self.imagelabel.pixmap().size
        self.scrollArea = QScrollArea()
        self.scrollArea.setBackgroundRole(QPalette.Dark)
        self.scrollArea.setWidget(self.imagelabel)

        self.setCentralWidget(self.scrollArea)
        self.setAcceptDrops(True)
        self.setWindowTitle(title)
        print("image pixmap", self.imagelabel.pixmap().size())

#######################################################################
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
        saveAction.setShortcut("Ctrl+S  ")
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

        self.zoomInAct = QAction("Zoom &In (25%)", self, shortcut="Ctrl++", enabled=True, triggered=self.zoomIn)
        self.zoomOutAct = QAction("Zoom &Out (25%)", self, shortcut="Ctrl+-", enabled=True, triggered=self.zoomOut)
        modify.addAction(self.zoomInAct)
        modify.addAction(self.zoomOutAct)

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
        self.scaleImage(1.0)

        self.transaction = Transaction(20, self.image.copy(self.image.rect()))
        # self.transaction.addData(self.image.copy(newimage.rect()))
        # self.transaction.addData(self.image.copy(newimage.rect()))
        # canvasPainter = QPainter(self)
        # canvasPainter.drawImage(self.rect(), self.image, self.image.rect())
        # self.label.setPixmap(QPixmap.fromImage(self.image))
        #
        # self.imagelabel.setPixmap(QPixmap.fromImage(self.image))
        # self.imagelabel.adjustSize()
        # self.imagelabel.adjustSize()
        self.load_start()
        print("image pixmap", self.imagelabel.pixmap().size())
    def mousePressEvent(self, event):
        print( event.pos().x(), event.pos().y())
        if event.button() == Qt.LeftButton:
            self.drawing = True
            self.lastPoint = event.pos()
            painter = QPainter(self.image)
            painter.setOpacity(50)
            if self.brushStyle == 'Pen':
                painter.setPen(QPen(self.brushColor, self.brushSize, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
                painter.drawPoint(int((1/self.scaleFactor)*event.x())-int(self.imagelabel.x()/self.scaleFactor) , int((1/self.scaleFactor)*(event.y() - 23))-int(self.imagelabel.y()/self.scaleFactor))
            elif self.brushStyle == 'Spray':
                painter.setPen(QPen(self.brushColor, 1))
                for n in range(self.brushSize**2 // 20):
                    x = random.gauss(0, self.brushSize // 4)
                    y = random.gauss(0, self.brushSize // 4)
                    painter.drawPoint(int((1/self.scaleFactor)*(event.x() + x))-int(self.imagelabel.x()/self.scaleFactor), int((1/self.scaleFactor)*(event.y() + y - 23))-int(self.imagelabel.y()/self.scaleFactor))
            self.update()

    def mouseMoveEvent(self, event):
        if self.drawing:
            painter = QPainter(self.image)
            if self.brushStyle == 'Pen':
                painter.setPen(QPen(self.brushColor, self.brushSize, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
                painter.drawLine(int((1/self.scaleFactor)*self.lastPoint.x())-int(self.imagelabel.x()/self.scaleFactor), int((1/self.scaleFactor)*(self.lastPoint.y()-23))-int(self.imagelabel.y()/self.scaleFactor), int((1/self.scaleFactor)*event.x())-int(self.imagelabel.x()/self.scaleFactor) , int((1/self.scaleFactor)*(event.y() - 23))-int(self.imagelabel.y()/self.scaleFactor))
            elif self.brushStyle == 'Spray':
                painter.setPen(QPen(self.brushColor, 1))
                for n in range(self.brushSize**2 // 20):
                    x = random.gauss(0, self.brushSize // 4)
                    y = random.gauss(0, self.brushSize // 4)
                    painter.drawPoint(int((1/self.scaleFactor)*(event.x() + x))-int(self.imagelabel.x()/self.scaleFactor), int((1/self.scaleFactor)*(event.y() + y-23))-int(self.imagelabel.y()/self.scaleFactor))
            self.lastPoint = event.pos()
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drawing = False
        self.transaction.addData(self.image.copy(self.image.rect()))

    def paintEvent(self, event):
        zoom = QImage(self.image)

        # canvasPainter = QPainter(self)
        # canvasPainter.drawImage(self.rect(), self.image, self.image.rect())
        # self.label.setPixmap(QPixmap.fromImage(self.image))
        self.imagelabel.setPixmap(QPixmap.fromImage(zoom))
        # self.imagelabel.adjustSize()
        # self.imagelabel.resize(self.scaleFactor * self.imagelabel.pixmap().size())
        # self.scrollArea.setVisible(True)
        # self.printAct.setEnabled(True)
        # self.fitToWindowAct.setEnabled(True)

    def wheelEvent(self, event):

        if event.angleDelta().y() > 0:
            self.scaleImage(1.01)

        elif event.angleDelta().y()<0:
            self.scaleImage(0.99)

        else:
            pass
    def zoomIn(self):
        self.scaleImage(1.25)
        self.imagelabel = self.imagelabel

    def zoomOut(self):
        self.scaleImage(0.8)
        self.imagelabel = self.imagelabel

    def nomarSize(self):
        self.imagelabel.adjustSize()
        self.scaleFactor = 1.0

    def scaleImage(self, factor):
        print("imagelabel.pixmap.size",self.imagelabel.pixmap().size(),"self.size",self.size())
        self.scaleFactor *= factor
        self.imagelabel.resize(self.scaleFactor * self.imagelabel.pixmap().size())
        self.adjustScrollBar(self.scrollArea.horizontalScrollBar(), factor)
        self.adjustScrollBar(self.scrollArea.verticalScrollBar(), factor)

        self.zoomInAct.setEnabled(self.scaleFactor < 3.0)
        self.zoomOutAct.setEnabled(self.scaleFactor > 0.111)

    def adjustScrollBar(self, scrollBar, factor):
        scrollBar.setValue(int(factor * scrollBar.value()
                               + ((factor - 1) * scrollBar.pageStep() / 2)))

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
        self.resize(newImage.width()+2, newImage.height() + 22)
        self.image = newImage
        print("image pixmap", self.imagelabel.pixmap().size())
        self.imagelabel.setPixmap(QPixmap.fromImage(self.image))
        print("image pixmap",self.imagelabel.pixmap().size())
        self.scaleFactor = 1.0
        self.imagelabel.adjustSize()
        self.transaction.addData(self.image.copy(newImage.rect()))

    def load_start(self):
        newImage =  QImage(800,600, QImage.Format_ARGB32)
        newImage.fill(Qt.transparent)
        self.resize(newImage.width() +2, newImage.height() +22)
        print("self size",self.size())
        self.image = newImage
        self.imagelabel.setPixmap(QPixmap.fromImage(self.image))
        self.scaleFactor = 1.0
        self.imagelabel.adjustSize()



    def clear(self):
        self.image.fill(Qt.transparent)
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
        if self.can!=0:
            resizedImage = QImage(e.size(), QImage.Format_RGB32)
            resizedImage.fill(Qt.transparent)
            painter = QPainter(resizedImage)
            painter.drawImage(self.image.rect(), self.image, self.image.rect())
            self.image = resizedImage
            self.update()
        else:
            self.can+=1
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
            print(myUrl.toString())
            decoded = parse.parse_qs(myUrl.toString())
            hdr = {'User-Agent': 'Mozilla/5.0'}
            req = request.Request(decoded['https://www.google.com/imgres?imgurl'][0], headers=hdr)
            newImage = QImage()
            newImage.loadFromData(request.urlopen(req).read())

        self.resize(newImage.width(), newImage.height())
        self.image = newImage
        self.imagelabel.resize(self.image.width(), self.image.height() + 30)
        self.update()
        self.transaction.addData(self.image.copy(self.image.rect()))


if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    window = Window()
    window.setAttribute(Qt.WA_TranslucentBackground)
    window.show()
    app.exec()
