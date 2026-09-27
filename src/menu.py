import logging
from pathlib import Path
import subprocess

from PySide6.QtCore import Qt, QMargins, Signal
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QApplication, QWidget, QMainWindow, QPushButton, QLabel, QHBoxLayout, QVBoxLayout, QFileDialog, QToolBar

from src.config import cfg

logging.basicConfig(level=logging.DEBUG, filename='log', filemode='w')


class Menu(QToolBar):
    tex_opened = Signal(str)

    def __init__(self):
        super().__init__()
        self.open_tex_action = QAction('Open tex')
        self.compile_action = QAction('Compile')
        self.swap_action = QAction('Swap')

        self.open_tex_action.triggered.connect(self.on_open_tex_triggered)

        self.addActions([self.open_tex_action, self.compile_action, self.swap_action])

    def on_open_tex_triggered(self):
        path, _ = QFileDialog.getOpenFileName(self, caption='Open tex file', filter='Tex files (*.tex)')
        self.tex_opened.emit(path)
