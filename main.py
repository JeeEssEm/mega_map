import sys

import requests as req
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt


class Main(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('window.ui', self)
        self.url = "http://static-maps.yandex.ru/1.x/?ll={},{}&spn={},{}&l=map"
        self.spn = [0.002, 0.002]
        self.coords = [37.530887, 55.703118]
        self.size = (1920, 1080)
        self.step = self.spn[0] * 0.1
        self.spn_scale = 5
        self.resize(*self.size)
        self.label.resize(*self.size)
        self.update_()

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_PageUp and self.spn[0] < 20:
            self.spn[0] *= self.spn_scale
            self.spn[1] *= self.spn_scale
            self.step = self.spn[0] * 0.1
        elif e.key() == Qt.Key_PageDown and self.spn[0] > 0.00002:
            self.spn[0] /= self.spn_scale
            self.spn[1] /= self.spn_scale
            self.step = self.spn[0] * 0.1
        elif e.key() == Qt.Key_Left:
            self.coords[0] -= self.step
            if self.coords[0] < -180:
                self.coords[0] += 360
        elif e.key() == Qt.Key_Right:
            self.coords[0] += self.step
            if self.coords[0] > 180:
                self.coords[0] -= 360
        elif e.key() == Qt.Key_Up:
            self.coords[1] += self.step
        elif e.key() == Qt.Key_Down:
            self.coords[1] -= self.step
        print(self.coords)
        self.update_()

    def update_(self):
        img = req.get(self.url.format(*self.coords, *self.spn)).content
        pixmap = QPixmap()
        pixmap.loadFromData(img, 'PNG')
        pixmap = pixmap.scaled(*self.size)
        self.label.setPixmap(pixmap)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Main()
    ex.show()
    sys.exit(app.exec_())