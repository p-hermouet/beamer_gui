import logging
from pathlib import Path
import sys
import subprocess
import tomllib

from PySide6.QtWidgets import QApplication, QWidget, QMainWindow, QPushButton, QLabel, QHBoxLayout, QVBoxLayout, QFileDialog
from PySide6.QtPdf import QPdfDocument
from PySide6.QtPdfWidgets import QPdfView
from PySide6.QtCore import Qt, QMargins, Signal

# from src.options import SwapButton, TexSelectButton
from src.config import cfg
from src.menu import Menu
from src.pdf_view import PdfView

logging.basicConfig(level=logging.DEBUG, filename='log', filemode='w')



class TestButton(QPushButton):
    def __init__(self):
        super().__init__('Test')
        self.clicked.connect(self.on_clicked)

    def on_clicked(self):
        pdf_view = self.window().pdf_view
        pdf_view.doc = QPdfDocument(self)
        pdf_view.doc.load('tmp/main.pdf')
        pdf_view.setDocument(pdf_view.doc)
