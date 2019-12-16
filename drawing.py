from PyQt5.QtGui import QPainter, QPen, QPolygon, QBrush, QColor
from PyQt5.QtCore import Qt, QPoint
import random


def drawRectangle(image, color, size, x1, y1, x2, y2, fill, rightAngle, opacity):
    painter = QPainter(image)
    painter.setOpacity(opacity / 100)
    if rightAngle:
        painter.setPen(color)
        painter.setBrush(color)
        d = size / 2
        if size % 2 == 1:
            x1 += 1
            x2 += 1
        for x in [x1, x2]:
            for y in [y1, y2]:
                polygon = []
                dx = [x - d, x - d, x + d - 1, x + d - 1]
                dy = [y - d, y + d - 1, y + d - 1, y - d]
                for i in range(4):
                    if size % 2 == 0:
                        polygon.append(QPoint(dx[i], dy[i]))
                    else:
                        polygon.append(QPoint(dx[i] + 1, dy[i] + 1))
                painter.drawPolygon(QPolygon(polygon))
        painter.setBrush(QBrush())
    painter.setPen(QPen(color, size, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
    if fill:
        painter.setBrush(color)
    painter.drawRect(x1, y1, x2 - x1, y2 - y1)
    return image


def drawCircle(image, color, size, x1, y1, x2, y2, fill, opacity):
    painter = QPainter(image)
    painter.setOpacity(opacity / 100)
    painter.setPen(QPen(color, size, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
    if fill:
        painter.setBrush(color)
    painter.drawEllipse(x1, y1, x2 - x1, y2 - y1)
    return image


def drawPoint(image, color, size, x, y, opacity):
    painter = QPainter(image)
    painter.setOpacity(opacity / 100)
    painter.setPen(QPen(color, size, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
    painter.drawPoint(x, y)
    return image


def drawLine(image, color, size, x1, y1, x2, y2, opacity):
    painter = QPainter(image)
    painter.setOpacity(opacity / 100)
    painter.setPen(QPen(color, size, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
    painter.drawLine(x1, y1, x2, y2)
    return image


def drawEraser(image, size, x1, y1, x2, y2):
    painter = QPainter(image)
    painter.setBrush(Qt.white)
    painter.setPen(Qt.white)
    dx = dy = size
    x1 = x1 - dx / 2
    y1 = y1 - dy / 2
    x2 = x2 - dx / 2
    y2 = y2 - dy / 2
    painter.drawRect(x1, y1, dx, dx)
    polygons = [QPolygon([QPoint(x1, y1), QPoint(x1, y1 + dy), QPoint(x2, y2 + dy), QPoint(x2, y2)]),
                QPolygon([QPoint(x1, y1 + dy), QPoint(x1 + dx, y1 + dy), QPoint(x2 + dx, y2 + dy), QPoint(x2, y2 + dy)]),
                QPolygon([QPoint(x1 + dx, y1 + dy), QPoint(x1 + dx, y1), QPoint(x2 + dx, y2), QPoint(x2 + dx, y2 + dy)]),
                QPolygon([QPoint(x1 + dx, y1), QPoint(x1, y1), QPoint(x2, y2), QPoint(x2 + dx, y2)])]
    for polygon in polygons:
        painter.drawPolygon(polygon)
    return image


def drawSpray(image, color, size, x, y, opacity):
    painter = QPainter(image)
    painter.setOpacity(opacity / 100)
    painter.setPen(QPen(color, 1))
    for n in range(size ** 2 // 10):
        dx = random.gauss(0, size // 4)
        dy = random.gauss(0, size // 4)
        painter.drawPoint(x + dx, y + dy)
    return image


def drawPaintBucket(image, color, x, y, opacity):

    def getColor(x, y):
        i = (x + (y * width)) * 4
        return bytesImage[i: i + 3]
    painter = QPainter(image)
    painter.setOpacity(opacity / 100)
    painter.setPen(color)
    width = image.width()
    height = image.height()
    if not (0 <= x < width and 0 <= y < height):
        return image
    color = QColor(color)
    color = bytes([color.blue(), color.green(), color.red()])
    bytesImage = image.bits().asstring(width * height * 4)
    baseColor = getColor(x, y)
    if baseColor == color:
        return image
    done = set()
    done.add((x, y))
    posStack = [(x, y)]
    dx = [0, 0, -1, 1]
    dy = [-1, 1, 0, 0]
    checked = 0
    while posStack:
        checked += 1
        x, y = posStack.pop()
        if not (0 <= x < width and 0 <= y < height) or getColor(x, y) != baseColor:
            continue
        painter.drawPoint(x, y)
        for i in range(4):
            point = (x + dx[i], y + dy[i])
            if point not in done:
                posStack.append(point)
                done.add(point)
    return image