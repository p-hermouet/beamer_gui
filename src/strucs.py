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

logging.basicConfig(level=logging.DEBUG, filename='log', filemode='w')


class MainStruc(QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName('main_struc')
        self.setVisible(False)
        self.struc = QLabel()
        self.setLayout(QHBoxLayout())
        self.layout().addWidget(self.struc, alignment=Qt.AlignmentFlag.AlignCenter)

        layout = QVBoxLayout(self.struc)
        layout.setContentsMargins(QMargins(0, 0, 0, 0))
        layout.addWidget(TitleStruc(), stretch=15)
        layout.addWidget(TitleStruc(), stretch=85)


class TitleStruc(QLabel):
    def __init__(self):
        super().__init__('bli')
        self.setObjectName('title_struc')
