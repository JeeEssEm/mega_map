import sys

import requests as req
from PyQt5 import uic, QtCore, QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import Qt

if hasattr(QtCore.Qt, 'AA_EnableHighDpiScaling'):
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)

if hasattr(QtCore.Qt, 'AA_UseHighDpiPixmaps'):
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)


class Main(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('window.ui', self)
        self.url = "http://static-maps.yandex.ru/1.x/?ll={},{}&spn={},{}&l=map"
        self.spn = [0.002, 0.002]
        self.coords = [37.530887, 55.703118]
        self.size = (1600, 900)
        self.step = self.spn[0] * 0.1
        self.spn_scale = 5
        self.resize(*self.size)
        search_w = self.width() // 16 * 6
        search_h = self.height() / 9
        self.search_le.setGeometry(*map(int, [search_w // 6, search_h // 3, search_w, search_h]))
        self.search_le.setStyleSheet(f"QLineEdit {{ background-color: lightgray; border-radius: {search_h // 2}px;"
                                     f"padding: 0 100px 0 20px; font-size: {int(search_h // 2)}px; }}")
        self.search_btn = SearchButton(self, self.search)
        self.search_btn.setGeometry(*map(int, [self.search_le.x() + search_w - search_h // 1.5, self.search_le.y() + search_h // 2 - search_h // 4,
                                    search_h // 2, search_h // 2]))
        self.search_btn.setIconSize(self.search_btn.size())
        self.map.setGeometry(0, 0, *self.size)
        self.update_()

    def keyPressEvent(self, e):
        self.search_le.clearFocus()
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
        pixmap = pixmap.scaled(*self.size, transformMode=Qt.SmoothTransformation)
        self.map.setPixmap(pixmap)

    def search(self):
        print('ok')


class SearchButton(QtWidgets.QPushButton):
    def __init__(self, parent, func):
        super(SearchButton, self).__init__(parent)
        self.func = func
        self.setFlat(True)
        self.setIcon(QIcon('search_icon.png'))
        self.setCursor(Qt.PointingHandCursor)

    def event(self, e: QtCore.QEvent) -> bool:
        if e.type() == QtCore.QEvent.Paint:
            return super().event(e)
        elif e.type() == QtCore.QEvent.MouseButtonPress:
            self.func()
        return True



if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Main()
    ex.show()
    sys.exit(app.exec_())