from PyQt5.QtWidgets import QMainWindow, QApplication, QAction, QWidgetAction, QFileDialog, QColorDialog
from PyQt5.QtGui import QImage, QClipboard
from PyQt5.QtCore import Qt
from brushsizepicker import BrushSizePicker
from checkboxsetting import CheckboxSetting
from imagefromweb import ImageFromWeb
from imageviewer import ImageViewer
from drawing import *
import sys
from urllib import parse, request


class PaintApplication(QMainWindow):

    def __init__(self):
        super().__init__()

        title = 'Paint Application'

        self.setAcceptDrops(True)
        self.setWindowTitle(title)

        self.imageViewer = ImageViewer()
        self.hdr = {'User-Agent': 'Mozilla/5.0'}
        self.setStyleSheet("QWidget {background-color: rgb(239, 235, 230);}")

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
                           {'name': 'Clear', 'shortcut': 'Ctrl+C', 'callback': self.imageViewer.clear},
                           {'name': 'Undo', 'shortcut': 'Ctrl+Z', 'callback': self.imageViewer.undoAndRedo},
                           {'name': 'Redo', 'shortcut': 'Ctrl+Shift+Z', 'callback': self.imageViewer.undoAndRedo},
                           {'name': 'Paste', 'shortcut': 'Ctrl+V', 'callback': self.paste}]

        for setting in fileMenuSetting:
            action = QAction(setting['name'], self)
            action.setShortcut(setting['shortcut'])
            action.triggered.connect(setting['callback'])
            fileMenu.addAction(action)

        for angle in [90, 180, 270]:
            rotateAction = QAction("Rotate " + str(angle), self)
            rotateAction.triggered.connect(self.imageViewer.rotateImage)
            modify.addAction(rotateAction)

        for flip in ['Vertically', 'Horizontally']:
            flipAction = QAction("filp " + flip, self)
            flipAction.triggered.connect(self.imageViewer.flip)
            modify.addAction(flipAction)

        for brushType in ['Pen', 'Eraser', 'Spray', 'Move']:
            brushAction = QAction(brushType, self)
            brushAction.triggered.connect(self.imageViewer.changeBrush)
            brushStyle.addAction(brushAction)

        drawingMenu.aboutToHide.connect(self.getDrawingOption)
        optionSettingAction = QWidgetAction(self)
        self.checkboxSetting = CheckboxSetting('Full Fill')
        optionSettingAction.setDefaultWidget(self.checkboxSetting)
        drawingMenu.addAction(optionSettingAction)

        for figure in ['Rectangle', 'Circle', 'Line']:
            drawAction = QAction(figure, self)
            drawAction.triggered.connect(self.imageViewer.changeBrush)
            drawingMenu.addAction(drawAction)

        brushSize.aboutToHide.connect(self.getSize)
        sizePickAction = QWidgetAction(self)
        self.sizeSlider = BrushSizePicker(1, 200, 2)
        sizePickAction.setDefaultWidget(self.sizeSlider)
        brushSize.addAction(sizePickAction)

        colorPicker.triggered.connect(self.pickColor)
        mainMenu.addAction(colorPicker)

        imageSearch.triggered.connect(self.searchImage)
        mainMenu.addAction(imageSearch)

        QApplication.clipboard().dataChanged.connect(self.copy)
        self.setCentralWidget(self.imageViewer)

    def save(self):
        filePath, type = QFileDialog.getSaveFileName(self, "Save Image", "", "PNG(*.png);;JPEG(*.jpg *.jpeg);;All Files(*.*) ")
        if filePath == "":
            return
        image = self.imageViewer.getImage()
        image.save(filePath)

    def load(self):
        filePath, type = QFileDialog.getOpenFileName(self, "Import Image", "", "PNG(*.png);;JPEG(*.jpg *.jpeg);;All Files(*.*) ")
        if filePath == "":
            return
        newImage = QImage(filePath)
        self.imageViewer.setImage(newImage)

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
        self.imageViewer.setImage(newImage)

    def copy(self):
        self.clipboardImage = QApplication.clipboard().image(QClipboard.Clipboard)

    def paste(self):
        if self.clipboardImage and not self.clipboardImage.isNull():
            self.imageViewer.setImage(self.clipboardImage)

    def getDrawingOption(self):
        self.imageViewer.setFullFill(self.checkboxSetting.getSetting())

    def getSize(self):
        self.imageViewer.setBrushSize(self.sizeSlider.getSize())

    def pickColor(self):
        self.imageViewer.setBrushColor(QColorDialog.getColor())

    def searchImage(self):
        imgSearchDialog = ImageFromWeb()
        imgSearchDialog.exec_()
        searchedImage = imgSearchDialog.image
        if searchedImage:
            self.image = searchedImage
            while self.image.width() >= 1920 or self.image.height() >= 1080:
                self.image = self.image.scaled(self.image.width() // 2, self.image.height() // 2, Qt.KeepAspectRatio)
            self.imageViewer.setImage(self.image)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = PaintApplication()
    window.show()
    app.exec()