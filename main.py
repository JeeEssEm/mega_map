import sys

import requests as req
from PyQt5 import uic, QtCore, QtWidgets, QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import Qt
import geocoder

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
        self.coords = [37.595687, 55.787718]
        self.size = (1600, 900)
        self.step = self.spn[0] * 0.1
        self.last_search_flag = None
        self.map_type = "map"
        self.spn_scale = 3
        self.resize(*self.size)
        search_w = self.width() // 16 * 6
        search_h = self.height() / 9
        self.search_le = SearchLine(self)
        self.search_le.setGeometry(
            *map(int, [search_w // 6 * 9.5, search_h // 3, search_w, search_h]))
        self.search_le.setStyleSheet(
            f"QLineEdit {{ background-color: lightgray; border-radius: {search_h // 2}px;"
            f"padding: 0 100px 0 20px; font-size: {int(search_h // 2)}px; }}")
        self.search_btn = SearchButton(self, self.search)
        self.search_btn.setGeometry(*map(int, [self.search_le.x() + search_w - search_h // 1.5,
                                               self.search_le.y() + search_h // 2 - search_h // 4,
                                               search_h // 2, search_h // 2]))
        self.search_btn.setIconSize(self.search_btn.size())
        self.search_le.btn = self.search_btn
        self.map.setGeometry(0, 0, *self.size)
        self.update_()

    def keyPressEvent(self, e):
        if self.search_le.hasFocus():
            return
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
        elif e.key() == Qt.Key_1:
            self.map_type = "map"
        elif e.key() == Qt.Key_2:
            self.map_type = "sat"
        elif e.key() == Qt.Key_3:
            self.map_type = "sat,skl"
        print(self.coords)
        self.update_()

    def update_(self, new_coords=None):
        if new_coords:
            self.coords = list(new_coords)

        img, img_type = geocoder.get_map(self.coords, self.spn[0], self.map_type, self.last_search_flag)
        pixmap = QPixmap()
        pixmap.loadFromData(img, img_type)
        pixmap = pixmap.scaled(*self.size, transformMode=Qt.SmoothTransformation)
        self.map.setPixmap(pixmap)

    def search(self):
        if self.search_btn.searching:
            self.search_btn.searching = False
            self.search_btn.upd()
            self.last_search_flag = None
            self.update_()
            self.search_le.setText("")
            return

        new_coords = geocoder.get_coordinates(self.search_le.text())
        if not new_coords:
            return self.update_()

        self.last_search_flag = new_coords
        self.search_btn.searching = True
        self.search_btn.upd()
        self.update_(new_coords)

    def mousePressEvent(self, a0: QtGui.QMouseEvent) -> None:
        pos = a0.pos()
        sle: QtWidgets.QLineEdit = self.search_le
        if sle.hasFocus() and (not (sle.x() <= pos.x() <= sle.x() + sle.width())
                               or not (sle.y() <= pos.y() <= sle.y() + sle.height())):
            sle.clearFocus()
        if sle.hasFocus() and ((sle.x() <= pos.x() <= sle.x() + sle.width())
                               and (sle.y() <= pos.y() <= sle.y() + sle.height())):
            self.search_btn.searching = True
            self.search_btn.upd()


class SearchLine(QtWidgets.QLineEdit):
    def __init__(self, parent, button=None):
        super(SearchLine, self).__init__(parent)
        self.btn = button

    def keyPressEvent(self, a0: QtGui.QKeyEvent) -> None:
        super(SearchLine, self).keyPressEvent(a0)
        if a0.key() == Qt.Key_Return:
            self.parent().search()

    def focusInEvent(self, a0: QtGui.QFocusEvent) -> None:
        super(SearchLine, self).focusInEvent(a0)
        if self.btn:
            self.btn.searching = False
            self.btn.upd()


class SearchButton(QtWidgets.QPushButton):
    def __init__(self, parent, func):
        super(SearchButton, self).__init__(parent)
        self.func = func
        self.searching = False
        self.setFlat(True)
        self.setIcon(QIcon('search_icon.png'))
        self.setCursor(Qt.PointingHandCursor)

    def mousePressEvent(self, e: QtGui.QMouseEvent) -> None:
        self.func()
        self.parent().setFocus()

    def upd(self):
        self.setIcon(QIcon("search_icon.png" if not self.searching else "cancel_icon.png"))


class SettingsButton(QtWidgets.QPushButton):
    def __init__(self, func):
        super(SettingsButton, self).__init__(parent)
        self.func = func
        self.setFlat(True)
        self.setIcon(QIcon('settings_icon.png'))
        self.setCursor(Qt.PointingHandCursor)

    def mousePressEvent(self, e: QtGui.QMouseEvent) -> None:
        self.func()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Main()
    ex.show()
    sys.exit(app.exec_())
