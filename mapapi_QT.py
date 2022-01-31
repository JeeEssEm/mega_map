import sys
from io import BytesIO
import requests
from PIL import Image, ImageQt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QWidget, QLabel
SCREEN_SIZE = [600, 450]
# Класс для демонстрации карты при помощи PyQT


class Example(QWidget):
    def __init__(self):
        super().__init__()
        self.getImage()
        self.initUI()
