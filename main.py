import sys

from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow


class Main(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('window.ui', self)

    def keyPressEvent(self, a0):
        pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Main()
    ex.show()
    sys.exit(app.exec_())