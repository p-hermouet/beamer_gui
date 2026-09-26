import logging
from pathlib import Path
import subprocess

from PySide6.QtWidgets import QApplication, QWidget, QMainWindow, QPushButton, QLabel, QHBoxLayout, QVBoxLayout, QFileDialog
from PySide6.QtPdf import QPdfDocument
from PySide6.QtPdfWidgets import QPdfView
from PySide6.QtCore import Qt, QMargins, Signal

from src.config import cfg

logging.basicConfig(level=logging.DEBUG, filename='log', filemode='w')


class Menu(QWidget):
    def __init__(self):
        super().__init__()
        self.open_tex_btn = OpenTexButton()
        self.compile_btn = CompileButton()
        self.swap_btn = SwapButton()

        self.setLayout(QVBoxLayout())
        self.layout().addWidget(self.open_tex_btn)
        self.layout().addWidget(self.compile_btn)
        self.layout().addWidget(self.swap_btn)


class OpenTexButton(QPushButton):
    tex_opened = Signal(str)

    def __init__(self):
        super().__init__('Open tex')

        self.clicked.connect(self.on_clicked)

    def on_clicked(self):
        path, _ = QFileDialog.getOpenFileName(self, caption='Open tex file', filter='Tex files (*.tex)')
        self.tex_opened.emit(path)


class CompileButton(QPushButton):
    def __init__(self):
        super().__init__('Compile')


class SwapButton(QPushButton):
    def __init__(self):
        super().__init__('Swap')
