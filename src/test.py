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
        win = self.window()
        win.resources.resource_list.add_resource('static.pp.png')


def get_main_window() -> QMainWindow | None:
    for w in QApplication.topLevelWidgets():
        if isinstance(w, QMainWindow):
            return w
    return None


def on_resource_fill_pressed(*args):
    if (win := get_main_window()):
        win.resources.resource_list.add_resource('static/pp.png')
    else:
        print('MainWindow cannot be found')
