from PyQt5.QtWidgets import QDialog, QLineEdit, QVBoxLayout, QGridLayout, QHBoxLayout, QPushButton, QLabel, QFrame
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QImage, QPalette, QBrush, QFont
from bs4 import BeautifulSoup
from urllib import request, parse
from clicklabel import ClickLabel
import threading
from itertools import zip_longest
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
        self.hdr = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.95 Safari/537.36'}
        self.loadedImageNum = 0
        self.lock = threading.Lock()
        self.threads = None
        self.setWindowTitle('Search Image')

        gridLayout = QGridLayout()
        gridLayout.setAlignment(Qt.AlignCenter)
        self.imageLabelList = []
        for i in range(10):
            imageLabel = ClickLabel()
            imageLabel.setFixedSize(100, 100)
            font = QFont()
            font.setPointSize(1)
            imageLabel.setFont(font)
            imageLabel.clicked.connect(self.imageSelected)
            imageLabel.setAutoFillBackground(True)
            imageLabel.setText(str(i))
            box = QHBoxLayout()
            box.addWidget(imageLabel)
            frame = QFrame()
            frame.setFixedSize(100, 100)
            frame.setLayout(box)
            frame.setLineWidth(5)
            self.imageLabelList.append(imageLabel)
            gridLayout.addWidget(frame, i // 5, i % 5, 1, 1)

        self.beforeButton = QPushButton('<')
        self.beforeButton.setFixedSize(30, 30)
        self.beforeButton.setEnabled(False)
        self.beforeButton.clicked.connect(self.turnOverPage)
        self.nextButton = QPushButton('>')
        self.nextButton.setFixedSize(30, 30)
        self.nextButton.setEnabled(False)
        self.nextButton.clicked.connect(self.turnOverPage)

        h1Box = QHBoxLayout()
        self.searchLabel = QLineEdit()
        self.searchLabel.setFixedWidth(200)
        enterButton = QPushButton('Search')
        enterButton.setFixedWidth(100)
        enterButton.clicked.connect(self.searchImage)
        self.statusLabel = QLabel()
        self.statusLabel.setFixedWidth(150)
        h1Box.addWidget(self.searchLabel)
        h1Box.addWidget(enterButton)
        h1Box.addWidget(self.statusLabel)

        h2Box = QHBoxLayout()
        h2Box.addWidget(self.beforeButton)
        h2Box.addLayout(gridLayout)
        h2Box.addWidget(self.nextButton)

        vBox = QVBoxLayout()
        vBox.addLayout(h1Box)
        vBox.addLayout(h2Box)

        self.pageLabel = QLabel('1 / 10')
        self.pageLabel.setAlignment(Qt.AlignCenter)
        vBox.addWidget(self.pageLabel)
        vBox.setAlignment(self.searchLabel, Qt.AlignCenter)

        self.setLayout(vBox)

    def searchImage(self):
        self.beforeButton.setEnabled(False)
        self.nextButton.setEnabled(False)
        self.statusLabel.setText('Searching Images...')
        self.update()
        self.page = 0
        self.pageLabel.repaint()
        query = self.searchLabel.text()
        query = '+'.join(query.split())
        url = "https://www.google.com/search?q=" + parse.quote(query) + "&hl=en&tbm=isch"
        try:
            soup = BeautifulSoup(request.urlopen(request.Request(url, headers=self.hdr), timeout=2), 'html.parser')
        except:
            self.statusLabel.setText('Network Connection Error!')
            return
        images = []
        self.imagesUrl = []
        for a in soup.find_all("div", {"class": "rg_meta"}):
            images.append(str(json.loads(a.text)["ou"]))
        if images:
            for i in range(10):
                self.imagesUrl.append(images[i*10:i*10+10])
            self.showImage()
        else:
            self.statusLabel.setText('Unexpected Error Occured!')
            self.update()

    def imageSelected(self):
        if self.threads:
            for thread in self.threads:
                thread.join()
        try:
            index = int(self.sender().text())
            self.image = self.images[index]
            self.close()
        except:
            pass

    def turnOverPage(self):
        if self.sender().text() == '<' and self.page > 0:
            self.page -= 1
            self.showImage()
        elif self.sender().text() == '>' and self.page < 9:
            self.page += 1
            self.showImage()
        else:
            self.statusLabel.setText('End of page!')
            self.update()
        self.pageLabel.setText(str(self.page + 1) + ' / 10')

    def showImage(self):
        self.statusLabel.setText('0% done...')
        self.update()
        self.beforeButton.setEnabled(False)
        self.nextButton.setEnabled(False)
        for label in self.imageLabelList:
            empty = QPalette()
            label.setPalette(empty)
        self.loadedImageNum = 0
        images = self.imagesUrl[self.page]
        self.threads = []
        for index, (label, image) in enumerate(zip_longest(self.imageLabelList, images, fillvalue=None)):
            self.threads.append(threading.Thread(target=self.loadImage, args=[label, image, index]))
        for thread in self.threads:
            thread.start()

    def loadImage(self, label, url, index):
        label.setText(str(index))
        image = QImage()
        try:
            image.loadFromData(request.urlopen(request.Request(url, headers=self.hdr)).read())
            if image.isNull():
                raise Exception
            self.images[index] = image
            image = image.scaled(100, 100, Qt.KeepAspectRatio)
            label.setFixedSize(image.width(), image.height())
            palette = QPalette()
            palette.setBrush(label.backgroundRole(), QBrush(image))
            label.setPalette(palette)
        except:
            label.setText('Error')
        self.lock.acquire()
        self.loadedImageNum += 1
        if self.loadedImageNum == 10:
            text = 'Successfully done'
            self.beforeButton.setEnabled(True)
            self.nextButton.setEnabled(True)
        else:
            text = str(self.loadedImageNum*10) + '% done...'
        self.updateStatus(text)
        self.lock.release()

    def updateStatus(self, text):
        self.statusLabel.setText(text)
        self.update()

    def mousePressEvent(self, event):
        self.clicked.emit()
