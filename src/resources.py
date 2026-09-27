import logging
from pathlib import Path
import sys
import subprocess
import tomllib

from PySide6.QtCore import Qt, QMargins, Signal
from PySide6.QtWidgets import QApplication, QWidget, QMainWindow, QPushButton, QLabel, QHBoxLayout, QVBoxLayout, QFileDialog, QStackedLayout

from src.config import cfg

logging.basicConfig(level=logging.DEBUG, filename='log', filemode='w')


class Resources(QWidget):
    def __init__(self):
        super().__init__()

        self.recource_paths: list[str|Path] = []

        self.add_resource_btn = QPushButton('Open')
        self.resource_list = QWidget()

        self.setLayout(QVBoxLayout())
        self.layout().addWidget(self.add_resource_btn, stretch=20)
        self.layout().addWidget(self.resource_list, stretch=80)


class ResourceList(QWidget):
    ...
