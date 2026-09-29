import logging
from pathlib import Path
import sys
import subprocess
import tomllib

from PySide6.QtWidgets import QApplication, QWidget, QMainWindow, QPushButton, QLabel, QHBoxLayout, QVBoxLayout, QFileDialog, QMenu, QStatusBar, QToolBar, QStackedLayout, QScrollArea
from PySide6.QtPdf import QPdfDocument
from PySide6.QtGui import QAction, QPixmap
from PySide6.QtPdfWidgets import QPdfView
from PySide6.QtCore import Qt, QMargins, Signal

from src.config import cfg
from src.menu import Menu
from src.pdf_view import PdfView
from src.test import TestButton
from src.strucs import MainStruc

logging.basicConfig(level=logging.DEBUG, filename='log', filemode='w')


class TestCentralWidget(QWidget):
    def __init__(self):
        super().__init__()


class TestMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.showMaximized()

        toolbar = QToolBar()
        self.addToolBar(toolbar)
        action = QAction('test', self)
        action2 = QAction('move', self)

        action.triggered.connect(self.test)
        action2.triggered.connect(self.mv)
        toolbar.addAction(action)
        toolbar.addAction(action2)

        self.central = TestCentralWidget()
        self.setCentralWidget(self.central)

    def test(self):
        self.im = QLabel(self)
        pixmap = QPixmap('static/pp.png')
        self.im.setPixmap(pixmap)
        self.im.setGeometry(pixmap.width(), pixmap.height(), 1000, 400)
        self.im.show()

    def mv(self):
        self.im.move(self.im.x() + 50, self.im.y())


if __name__ == "__main__":
    app = QApplication([])
    main_window = TestMainWindow()
    main_window.show()
    app.exec()
