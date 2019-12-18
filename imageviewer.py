from PyQt5.QtCore import Qt, QRectF, QSize, QPoint, pyqtSignal
from PyQt5.QtGui import QImage, QPixmap, QPainterPath, QTransform
from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene
from transaction import Transaction
from drawing import *
from urllib import request, parse


class ImageViewer(QGraphicsView):
    update = pyqtSignal()
    mouseMoved = pyqtSignal(int, int)

    def __init__(self):
        super().__init__()

        self.scene = QGraphicsScene()
        self.setScene(self.scene)

        self.aspectRatioMode = Qt.KeepAspectRatio
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        self.zoomStack = []
        self.canZoom = False
        self.imageHandler = None

        self.drawing = False
        self.brushSize = 2
        self.brushOpacity = 100
        self.brushColor = Qt.black
        self.lastPoint = QPoint()
        self.brushStyle = 'Pen'
        self.fullFill = False
        self.backUp = None

        self.clipboardImage = None
        self.setMouseTracking(True)
        self.setAcceptDrops(True)

        self.hdr = {'User-Agent': 'Mozilla/5.0'}
        self.startView()
        self.transaction = Transaction(100, self.image().copy(self.image().rect()))

    def hasImage(self):
        return self.imageHandler is not None

    def image(self):
        if self.hasImage():
            return self.imageHandler.pixmap().toImage()
        return None

    def setImage(self, image):
        pixmap = QPixmap.fromImage(image)
        if self.hasImage():
            self.imageHandler.setPixmap(pixmap)
        else:
            self.imageHandler = self.scene.addPixmap(pixmap)
        self.setSceneRect(QRectF(pixmap.rect()))

    def updateViewer(self):
        if len(self.zoomStack) and self.sceneRect().contains(self.zoomStack[-1]):
            self.fitInView(self.zoomStack[-1], Qt.KeepAspectRatio)
        else:
            self.zoomStack = []
            self.setSceneRect(QRectF(self.image().rect()))
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
                    self.setImage(drawPoint(self.image(), self.brushColor, self.brushSize, scenePos.x(), scenePos.y(), self.brushOpacity))
                elif self.brushStyle == 'Fountain Pen':
                    self.setImage(drawFountain(self.image(), self.brushColor, self.brushSize, self.lastPoint.x(), self.lastPoint.y(), scenePos.x(), scenePos.y(), self.brushOpacity))
                elif self.brushStyle == 'Spray':
                    self.setImage(drawSpray(self.image(), self.brushColor, self.brushSize, scenePos.x(), scenePos.y(), self.brushOpacity))
                elif self.brushStyle == 'Paint Bucket':
                    self.setImage(drawPaintBucket(self.image(), self.brushColor, int(scenePos.x()), int(scenePos.y()), self.brushOpacity))
                elif self.brushStyle == 'Eraser':
                    self.setImage(drawEraser(self.image(), self.brushSize, scenePos.x(), scenePos.y(), scenePos.x(), scenePos.y()))
                elif self.brushStyle in ['Rectangle', 'Circle', 'Line']:
                    self.backUp = self.image().copy(self.image().rect())

        elif event.button() == Qt.RightButton:
            self.canZoom = True
            self.setDragMode(QGraphicsView.RubberBandDrag)
        QGraphicsView.mousePressEvent(self, event)

    def mouseMoveEvent(self, event):
        scenePos = self.mapToScene(event.pos())
        if self.drawing:
            if self.brushStyle in ['Pen', 'Fountain Pen', 'Eraser', 'Spray']:
                if self.brushStyle == 'Pen':
                    self.setImage(drawLine(self.image(), self.brushColor, self.brushSize, self.lastPoint.x(), self.lastPoint.y(), scenePos.x(), scenePos.y(), self.brushOpacity))
                elif self.brushStyle == 'Fountain Pen':
                    self.setImage(drawFountain(self.image(), self.brushColor, self.brushSize, self.lastPoint.x(), self.lastPoint.y(), scenePos.x(), scenePos.y(), self.brushOpacity))
                elif self.brushStyle == 'Spray':
                    self.setImage(drawSpray(self.image(), self.brushColor, self.brushSize, scenePos.x(), scenePos.y(), self.brushOpacity))
                elif self.brushStyle == 'Eraser':
                    self.setImage(drawEraser(self.image(), self.brushSize, self.lastPoint.x(), self.lastPoint.y(), scenePos.x(), scenePos.y()))
                self.lastPoint = scenePos
            elif self.brushStyle in ['Rectangle', 'Circle', 'Line']:
                image = self.backUp.copy(self.image().rect())
                if self.brushStyle == 'Rectangle':
                    self.setImage(drawRectangle(image, self.brushColor, self.brushSize, self.lastPoint.x(), self.lastPoint.y(), scenePos.x(), scenePos.y(), self.fullFill, self.brushOpacity))
                elif self.brushStyle == 'Circle':
                    self.setImage(drawCircle(image, self.brushColor, self.brushSize, self.lastPoint.x(), self.lastPoint.y(), scenePos.x(), scenePos.y(), self.fullFill, self.brushOpacity))
                elif self.brushStyle == 'Line':
                    self.setImage(drawLine(image, self.brushColor, self.brushSize, self.lastPoint.x(), self.lastPoint.y(), scenePos.x(), scenePos.y(), self.brushOpacity))
        else:
            QGraphicsView.mouseMoveEvent(self, event)
        self.mouseMoved.emit(scenePos.x(), scenePos.y())

    def mouseReleaseEvent(self, event):
        QGraphicsView.mouseReleaseEvent(self, event)
        if event.button() == Qt.LeftButton:
            self.drawing = False
            self.setDragMode(QGraphicsView.NoDrag)
            self.transaction.addData(self.image().copy(self.image().rect()))
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

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.RightButton:
            if self.zoomStack:
                self.zoomStack = []
                self.updateViewer()
            else:
                self.reset()
        QGraphicsView.mouseDoubleClickEvent(self, event)

    def wheelEvent(self, event):
        scenePos = self.mapToScene(event.pos())
        self.mouseMoved.emit(scenePos.x(), scenePos.y())
        QGraphicsView.wheelEvent(self, event)
        if event.buttons() == Qt.LeftButton:
            self.mouseMoveEvent(event)

    def startView(self):
        image = QImage(QSize(800, 600), QImage.Format_RGB32)
        image.fill(Qt.white)
        self.resize(image.size())
        self.setImage(image)

    def clear(self):
        width = self.image().width()
        height = self.image().height()
        image = QImage(QSize(width, height), QImage.Format_RGB32)
        image.fill(Qt.white)
        self.setImage(image)
        self.reset()
        self.transaction.addData(self.image().copy(self.image().rect()))

    def setBrushSize(self, brushSize):
        self.brushSize = brushSize

    def setBrushOpacity(self, brushOpacity):
        self.brushOpacity = brushOpacity

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
        self.updateViewer()

    def rotateImage(self):
        angle = int(list(self.sender().text().split())[1])
        transform = QTransform()
        transform.rotate(angle)
        self.setImage(self.image().transformed(transform))
        self.transaction.addData(self.image().copy(self.image().rect()))
        self.updateViewer()

    def invertColor(self):
        image = self.image()
        image.invertPixels()
        self.setImage(image)
        self.transaction.addData(self.image().copy(self.image().rect()))

    def undoAndRedo(self):
        command = self.sender().text()
        if command == 'Undo':
            data = self.transaction.undo()
        elif command == 'Redo':
            data = self.transaction.redo()
        if data:
            self.setImage(data.copy())
            self.fitInView(self.sceneRect(), self.aspectRatioMode)

    def dragEnterEvent(self, event):
        m = event.mimeData()
        if m.hasUrls():
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        pass

    def dropEvent(self, event):
        myUrl = event.mimeData().urls()[0]
        if myUrl.isLocalFile():
            image = QImage(myUrl.toLocalFile())
        else:
            try:
                decoded = parse.parse_qs(myUrl.toString())
                req = request.Request(decoded['https://www.google.com/imgres?imgurl'][0], headers=self.hdr)
                image = QImage()
                image.loadFromData(request.urlopen(req).read())
            except:
                return
        self.setNewImage(image)

    def setNewImage(self, image):
        self.setImage(image)
        self.reset()
        self.transaction.addData(self.image().copy(self.image().rect()))

    def reset(self):
        self.zoomStack = []
        self.updateViewer()
        self.update.emit()