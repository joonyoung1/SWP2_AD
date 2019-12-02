from collections import deque
import itertools


class Transaction:
    def __init__(self, size, data):
        self.dataBase = deque(maxlen=size)
        self.position = 0
        self.maxPosition = size - 1
        self.dataBase.append(data)

    def addData(self, data):
        if self.position != self.maxPosition:
            self.dataBase = deque(itertools.islice(self.dataBase, 0, self.position + 1), maxlen=self.maxPosition + 1)
            self.position += 1
        self.dataBase.append(data)

    def undo(self):
        if self.position > 0:
            self.position -= 1
            data = self.dataBase[self.position]
        else:
            data = None
        return data

    def redo(self):
        if self.position < len(self.dataBase) - 1:
            self.position += 1
            data = self.dataBase[self.position]
        else:
            data = None
        return data
