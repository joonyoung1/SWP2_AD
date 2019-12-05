from PyQt5.QtWidgets import QDialog, QLineEdit, QVBoxLayout, QGridLayout, QHBoxLayout, QPushButton, QLabel
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon, QPixmap, QImage, QPalette, QBrush
from bs4 import BeautifulSoup
from urllib import request, parse
from clicklabel import ClickLabel
import threading
import json

class ImageFromWeb(QDialog):
    clicked = pyqtSignal()

    def __init__(self):
        super().__init__()

        self.imagesUrl = []
        self.imageLabelList = []
        self.images = [0 for _ in range(10)]
        self.image = None
        self.page = 0

        gridLayout = QGridLayout()
        self.imageLabelList = []
        for i in range(10):
            imageLabel = ClickLabel()
            imageLabel.clicked.connect(self.imageSelected)
            imageLabel.setAutoFillBackground(True)
            imageLabel.setText(str(i))
            self.imageLabelList.append(imageLabel)
            gridLayout.addWidget(imageLabel, i // 5, i % 5, 1, 1)

        beforeButton = QPushButton('<')
        beforeButton.setFixedSize(30, 30)
        beforeButton.clicked.connect(self.turnOverPage)
        nextButton = QPushButton('>')
        nextButton.setFixedSize(30, 30)
        nextButton.clicked.connect(self.turnOverPage)

        h1Box = QHBoxLayout()
        self.searchLabel = QLineEdit()
        self.searchLabel.setFixedWidth(200)
        enterButton = QPushButton('Search')
        enterButton.setFixedWidth(100)
        enterButton.clicked.connect(self.searchImage)
        h1Box.addWidget(self.searchLabel)
        h1Box.addWidget(enterButton)

        h2Box = QHBoxLayout()
        h2Box.addWidget(beforeButton)
        h2Box.addLayout(gridLayout)
        h2Box.addWidget(nextButton)

        vBox = QVBoxLayout()
        vBox.addLayout(h1Box)
        vBox.addLayout(h2Box)
        vBox.setAlignment(self.searchLabel, Qt.AlignCenter)

        self.setLayout(vBox)

    def searchImage(self):
        print('Image search started')
        query = self.searchLabel.text()
        query = '+'.join(query.split())
        hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11'}
        url = "https://www.google.co.kr/search?q=" + parse.quote(query) + "&source=lnms&tbm=isch"
        soup = BeautifulSoup(request.urlopen(request.Request(url, headers=hdr)), 'html.parser')
        images = []
        self.imagesUrl = []
        for a in soup.find_all("div", {"class": "rg_meta"}):
            images.append(str(json.loads(a.text)["ou"]))
        for i in range(10):
            self.imagesUrl.append(images[i*10:i*10+10])
        print(self.imagesUrl)
        self.showImage()
        print('Image search finished')

    def imageSelected(self):
        print(self.sender().text())
        index = int(self.sender().text())
        self.image = QImage(self.images[index])
        self.close()

    def turnOverPage(self):
        if self.sender().text() == '<' and self.page > 0:
            self.page -= 1
            self.showImage()
        elif self.sender().text() == '>' and self.page < 9:
            self.page += 1
            self.showImage()

    def getImage(self):
        return QImage(self.image)

    def showImage(self):
        print('showing Image')
        images = self.imagesUrl[self.page]
        for index, (label, image) in enumerate(zip(self.imageLabelList, images)):
            t = threading.Thread(target=self.loadImage, args=[label, image, index])
            t.start()

    def loadImage(self, label, url, index):
        print('Thread ' + str(index) + ' started')
        hdr = {'User-Agent': 'Mozilla/5.0'}
        label.setText(str(index))
        image = QImage()
        try:
            image.loadFromData(request.urlopen(request.Request(url, headers=hdr)).read())
        except:
            label.setText('e')
        self.images[index] = image
        image = image.scaled(100, 100, Qt.KeepAspectRatio)
        label.resize(image.width(), image.height())
        label.setFixedSize(image.width(), image.height())
        palette = QPalette()
        palette.setBrush(label.backgroundRole(), QBrush(image))
        label.setPalette(palette)
        print('Thread ' + str(index) + ' finished')

    def mousePressEvent(self, event):
        self.clicked.emit()
