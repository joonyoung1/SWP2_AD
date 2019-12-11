import os.path

from PyQt5.QtCore import Qt, QRectF, pyqtSignal, QT_VERSION_STR, QSize, QPoint
from PyQt5.QtGui import QImage, QPixmap, QPainterPath, QTransform
from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QFileDialog, QRubberBand
from transaction import Transaction
from drawing import *
from urllib import request, parse

class ImageViewer(QGraphicsView):
    leftMouseButtonPressed = pyqtSignal(float, float)
    rightMouseButtonPressed = pyqtSignal(float, float)
    leftMouseButtonReleased = pyqtSignal(float, float)
    rightMouseButtonReleased = pyqtSignal(float, float)
    leftMouseButtonDoubleClicked = pyqtSignal(float, float)
    rightMouseButtonDoubleClicked = pyqtSignal(float, float)

    def __init__(self):
        QGraphicsView.__init__(self)

        self.scene = QGraphicsScene()
        self.setScene(self.scene)

        self._pixmapHandle = None

        self.aspectRatioMode = Qt.KeepAspectRatio

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        self.zoomStack = []
        self.canZoom = False

        self.drawing = False
        self.brushSize = 2
        self.brushColor = Qt.black
        self.lastPoint = QPoint()
        self.brushStyle = 'Pen'
        self.fullFill = False
        self.backUp = None
        self.clipboardImage = None
        self.startView()
        self.rubberBand = QRubberBand(QRubberBand.Rectangle, self)

        self.hdr = {'User-Agent': 'Mozilla/5.0'}
        self.setAcceptDrops(True)
        self.transaction = Transaction(100, self.image().copy(self.image().rect()))

    def hasImage(self):
        return self._pixmapHandle is not None

    def pixmap(self):
        if self.hasImage():
            return self._pixmapHandle.pixmap()
        return None

    def image(self):
        if self.hasImage():
            return self._pixmapHandle.pixmap().toImage()
        return None

    def setImage(self, image):
        if type(image) is QPixmap:
            pixmap = image
        elif type(image) is QImage:
            pixmap = QPixmap.fromImage(image)
        else:
            raise RuntimeError("ImageViewer.setImage: Argument must be a QImage or QPixmap.")
        if self.hasImage():
            self._pixmapHandle.setPixmap(pixmap)
        else:
            self._pixmapHandle = self.scene.addPixmap(pixmap)
        self.setSceneRect(QRectF(pixmap.rect()))
        self.updateViewer()

    def loadImageFromFile(self, fileName=""):
        if len(fileName) == 0:
            if QT_VERSION_STR[0] == '4':
                fileName = QFileDialog.getOpenFileName(self, "Open image file.")
            elif QT_VERSION_STR[0] == '5':
                fileName, dummy = QFileDialog.getOpenFileName(self, "Open image file.")
        if len(fileName) and os.path.isfile(fileName):
            image = QImage(fileName)
            self.setImage(image)

    def updateViewer(self):
        if not self.hasImage():
            return
        if len(self.zoomStack) and self.sceneRect().contains(self.zoomStack[-1]):
            self.fitInView(self.zoomStack[-1], Qt.KeepAspectRatio)
        else:
            self.zoomStack = []
            self.fitInView(self.sceneRect(), self.aspectRatioMode)

    def resizeEvent(self, event):
        self.updateViewer()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            scenePos = self.mapToScene(event.pos())
            self.lastPoint = scenePos
            if self.brushStyle == 'Move':
                self.setDragMode(QGraphicsView.ScrollHandDrag)
            else:
                self.drawing = True
                if self.brushStyle == 'Pen':
                    self.setImage(drawPoint(self.image(), self.brushColor, self.brushSize, scenePos.x(), scenePos.y()))
                elif self.brushStyle == 'Eraser':
                    self.setImage(drawEraser(self.image(), self.brushSize, scenePos.x(), scenePos.y(), scenePos.x(), scenePos.y()))
                elif self.brushStyle == 'Spray':
                    self.setImage(drawSpray(self.image(), self.brushColor, self.brushSize, scenePos.x(), scenePos.y()))
                elif self.brushStyle in ['Rectangle', 'Circle', 'Line']:
                    self.backUp = self.image().copy(self.image().rect())
            self.leftMouseButtonPressed.emit(scenePos.x(), scenePos.y())

        elif event.button() == Qt.RightButton:
            self.canZoom = True
            self.setDragMode(QGraphicsView.RubberBandDrag)
            self.rightMouseButtonPressed.emit(event.x(), event.y())
        QGraphicsView.mousePressEvent(self, event)

    def mouseMoveEvent(self, event):
        if self.drawing:
            scenePos = self.mapToScene(event.pos())
            if self.brushStyle in ['Pen', 'Eraser', 'Spray']:
                if self.brushStyle == 'Pen':
                    self.setImage(drawLine(self.image(), self.brushColor, self.brushSize, self.lastPoint.x(), self.lastPoint.y(), scenePos.x(), scenePos.y()))
                elif self.brushStyle == 'Eraser':
                    self.setImage(drawEraser(self.image(), self.brushSize, self.lastPoint.x(), self.lastPoint.y(), scenePos.x(), scenePos.y()))
                elif self.brushStyle == 'Spray':
                    self.setImage(drawSpray(self.image(), self.brushColor, self.brushSize, scenePos.x(), scenePos.y()))
                self.lastPoint = scenePos
            elif self.brushStyle in ['Rectangle', 'Circle', 'Line']:
                image = self.backUp.copy(self.image().rect())
                if self.brushStyle == 'Rectangle':
                    self.setImage(drawRectangle(image, self.brushColor, self.brushSize, self.lastPoint.x(), self.lastPoint.y(), scenePos.x(), scenePos.y(), self.fullFill))
                elif self.brushStyle == 'Circle':
                    self.setImage(drawCircle(image, self.brushColor, self.brushSize, self.lastPoint.x(), self.lastPoint.y(), scenePos.x(), scenePos.y(), self.fullFill))
                elif self.brushStyle == 'Line':
                    self.setImage(drawLine(image, self.brushColor, self.brushSize, self.lastPoint.x(), self.lastPoint.y(), scenePos.x(), scenePos.y()))
        else:
            QGraphicsView.mouseMoveEvent(self, event)

    def mouseReleaseEvent(self, event):
        QGraphicsView.mouseReleaseEvent(self, event)
        scenePos = self.mapToScene(event.pos())
        if event.button() == Qt.LeftButton:
            self.drawing = False
            self.setDragMode(QGraphicsView.NoDrag)
            self.leftMouseButtonReleased.emit(scenePos.x(), scenePos.y())
        elif event.button() == Qt.RightButton:
            if self.canZoom:
                viewBBox = self.zoomStack[-1] if len(self.zoomStack) else self.sceneRect()
                selectionBBox = self.scene.selectionArea().boundingRect().intersected(viewBBox)
                self.scene.setSelectionArea(QPainterPath())
                if selectionBBox.isValid() and (selectionBBox != viewBBox):
                    self.zoomStack.append(selectionBBox)
                    self.updateViewer()
                self.canZoom = False
            self.setDragMode(QGraphicsView.NoDrag)
            self.rightMouseButtonReleased.emit(scenePos.x(), scenePos.y())
        if self.brushStyle == 'Eraser':
            self.setImage(drawEraser(self.image(), self.brushSize, scenePos.x(), scenePos.y(), scenePos.x(), scenePos.y()))
        self.transaction.addData(self.image().copy(self.image().rect()))

    def mouseDoubleClickEvent(self, event):
        scenePos = self.mapToScene(event.pos())
        if event.button() == Qt.LeftButton:
            self.leftMouseButtonDoubleClicked.emit(scenePos.x(), scenePos.y())
        elif event.button() == Qt.RightButton:
            self.zoomStack = []
            self.updateViewer()
            self.rightMouseButtonDoubleClicked.emit(scenePos.x(), scenePos.y())
        QGraphicsView.mouseDoubleClickEvent(self, event)

    def startView(self):
        image = QImage(QSize(800, 600), QImage.Format_RGB32)
        image.fill(Qt.white)
        self.setImage(image)

    def clear(self):
        width = self.image().width()
        height = self.image().height()
        image = QImage(QSize(width, height), QImage.Format_RGB32)
        image.fill(Qt.white)
        self.setImage(image)
        self.transaction.addData(self.image().copy(self.image().rect()))

    def setBrushSize(self, brushSize):
        self.brushSize = brushSize

    def setBrushColor(self, brushColor):
        self.brushColor = brushColor

    def changeBrush(self):
        brushStyle = self.sender().text()
        self.brushStyle = brushStyle

    def setFullFill(self, fullFill):
        self.fullFill = fullFill

    def flip(self):
        option = list(self.sender().text().split())[1]
        if option == 'Vertically':
            self.setImage(self.image().mirrored(False, True))
        elif option == 'Horizontally':
            self.setImage(self.image().mirrored(True, False))

    def rotateImage(self):
        angle = int(list(self.sender().text().split())[1])
        transform = QTransform()
        transform.rotate(angle)
        self.setImage(self.image().transformed(transform))
        self.transaction.addData(self.image().copy(self.image().rect()))

    def undoAndRedo(self):
        command = self.sender().text()
        if command == 'Undo':
            data = self.transaction.undo()
        elif command == 'Redo':
            data = self.transaction.redo()
        if data:
            self.setImage(data.copy())

    def dragEnterEvent(self, event):
        m = event.mimeData()
        print(m.hasUrls())
        if m.hasUrls():
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        pass

    def dropEvent(self, event):
        myUrl = event.mimeData().urls()[0]
        if myUrl.isLocalFile():
            newImage = QImage(myUrl.toLocalFile())
        else:
            decoded = parse.parse_qs(myUrl.toString())
            req = request.Request(decoded['https://www.google.com/imgres?imgurl'][0], headers=self.hdr)
            newImage = QImage()
            newImage.loadFromData(request.urlopen(req).read())
        self.setImage(newImage)

if __name__ == '__main__':
    import sys

    from PyQt5.QtWidgets import QApplication

    def handleLeftClick(x, y):
        row = int(y)
        column = int(x)
        print("Clicked on image pixel (row="+str(row)+", column="+str(column)+")")

    app = QApplication(sys.argv)

    viewer = QtImageViewer()
    # viewer.loadImageFromFile()
    viewer.leftMouseButtonPressed.connect(handleLeftClick)
    viewer.show()
    sys.exit(app.exec_())
