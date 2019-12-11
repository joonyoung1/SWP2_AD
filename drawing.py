from PyQt5.QtGui import QPainter, QPen, QPolygon
from PyQt5.QtCore import Qt, QPoint
import random


def drawRectangle(image, color, size, x1, y1, x2, y2, fill):
    painter = QPainter(image)
    painter.setPen(QPen(color, size, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
    if fill:
        painter.setBrush(color)
    painter.drawRect(x1, y1, x2 - x1, y2 - y1)
    return image


def drawCircle(image, color, size, x1, y1, x2, y2, fill):
    painter = QPainter(image)
    painter.setPen(QPen(color, size, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
    if fill:
        painter.setBrush(color)
    painter.drawEllipse(x1, y1, x2 - x1, y2 - y1)
    return image


def drawPoint(image, color, size, x, y):
    painter = QPainter(image)
    painter.setPen(QPen(color, size, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
    painter.drawPoint(x, y)
    return image


def drawLine(image, color, size, x1, y1, x2, y2):
    painter = QPainter(image)
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
    polygons = [QPolygon([QPoint(x1, y1), QPoint(x2, y2), QPoint(x2 + dx, y2 + dy), QPoint(x1 + dx, y1 + dy)]),
                QPolygon([QPoint(x1, y1 + dy), QPoint(x2, y2 + dy), QPoint(x2 + dx, y2), QPoint(x1 + dx, y1)])]
    for polygon in polygons:
        painter.drawPolygon(polygon)
    painter.drawRect(x1, y1, dx, dx)
    return image


def drawSpray(image, color, size, x, y):
    painter = QPainter(image)
    painter.setPen(QPen(color, 1))
    for n in range(size ** 2 // 10):
        dx = random.gauss(0, size // 4)
        dy = random.gauss(0, size // 4)
        painter.drawPoint(x + dx, y + dy)
    return image