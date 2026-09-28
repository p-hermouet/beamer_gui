import logging
from pathlib import Path
import sys
import subprocess
import tomllib

from PySide6.QtWidgets import QApplication, QWidget, QMainWindow, QPushButton, QLabel, QHBoxLayout, QVBoxLayout, QFileDialog, QMenu, QStatusBar, QToolBar, QStackedLayout, QScrollArea
from PySide6.QtPdf import QPdfDocument
from PySide6.QtGui import QAction
from PySide6.QtPdfWidgets import QPdfView
from PySide6.QtCore import Qt, QMargins, Signal

from src.config import cfg
from src.menu import Menu
from src.pdf_view import PdfView
from src.test import TestButton
from src.strucs import MainStruc

logging.basicConfig(level=logging.DEBUG, filename='log', filemode='w')


class TestCentralWidget(QScrollArea):
    def __init__(self):
        super().__init__()

        self.wid = QWidget()
        self.wid.setLayout(QVBoxLayout())
        self.setWidget(self.wid)
        self.setWidgetResizable(True)


class TestMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.showMaximized()

        toolbar = QToolBar()
        self.addToolBar(toolbar)
        action = QAction('fill', self)
        action.triggered.connect(self.fill)
        toolbar.addAction(action)

        self.central = TestCentralWidget()
        self.setCentralWidget(self.central)

    def fill(self):
        self.central.wid.layout().addWidget(QPushButton('bli'))

if __name__ == "__main__":
    app = QApplication([])
    main_window = TestMainWindow()
    main_window.show()
    app.exec()
