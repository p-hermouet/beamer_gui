import logging
from pathlib import Path
import sys
import subprocess
import tomllib

from PySide6.QtCore import Qt, QMargins, Signal
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QApplication, QWidget, QMainWindow, QPushButton, QLabel, QHBoxLayout, QVBoxLayout, QFileDialog, QStackedLayout, QScrollArea

from src.config import cfg

logging.basicConfig(level=logging.DEBUG, filename='log', filemode='w')


class Resources(QWidget):
    def __init__(self):
        super().__init__()

        self.add_resource_btn = QPushButton('Open')
        self.resource_list = ResourceList()

        self.add_resource_btn.clicked.connect(self.on_open_btn_clicked)

        self.setLayout(QVBoxLayout())
        self.layout().addWidget(self.add_resource_btn, stretch=20)
        self.layout().addWidget(self.resource_list, stretch=80)

    def on_open_btn_clicked(self):
        path, _ = QFileDialog.getOpenFileName(self, caption='Open resource file', filter='Image files (*.png *.jpg *.jpeg)')
        self.resource_list.add_resource(path)


class ResourceList(QScrollArea):
    def __init__(self):
        super().__init__()
        self.content = ResourceListContent()
        self.setWidget(self.content)
        self.setWidgetResizable(True)

    def add_resource(self, resource_path: str|Path):
        self.content.resource_paths.append(resource_path)
        im  = QLabel()
        im.setPixmap(QPixmap(resource_path))
        ratio = im.pixmap().width() / im.pixmap().height()
        w, h = .22 * self.height() * ratio, .22 * self.height()
        if w > self.width():
            w, h = self.width(), self.width() / ratio
        im.setFixedSize(.9 * w, .9 * h) # .9 factor to prevent pictures to be cropped when scroll bar appears
        im.setScaledContents(True)
        self.content.layout().addWidget(im)

    def rm_resource(self, resource: str|Path|int):
        ... # TODO (resource) can be path or position


class ResourceListContent(QWidget):
    def __init__(self):
        super().__init__()
        self.resource_paths: list[str|Path] = []

        self.setLayout(QVBoxLayout(alignment=Qt.AlignmentFlag.AlignCenter))

