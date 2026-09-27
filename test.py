import logging
from pathlib import Path
import sys
import subprocess
import tomllib

from PySide6.QtWidgets import QApplication, QWidget, QMainWindow, QPushButton, QLabel, QHBoxLayout, QVBoxLayout, QFileDialog
from PySide6.QtPdf import QPdfDocument
from PySide6.QtPdfWidgets import QPdfView
from PySide6.QtCore import Qt, QMargins, Signal

from src.config import cfg
from src.menu import Menu
from src.pdf_view import PdfView
from src.test import TestButton
from src.strucs import MainStruc

logging.basicConfig(level=logging.DEBUG, filename='log', filemode='w')


class TestMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.pdf_view = QPdfView()
        doc = QPdfDocument(self)
        doc.load('tmp/main.pdf')
        self.pdf_view.setDocument(doc)

        self.setCentralWidget(self.pdf_view)


if __name__ == "__main__":
    app = QApplication([])
    main_window = TestMainWindow()
    main_window.show()
    app.exec()
