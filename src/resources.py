import logging
from pathlib import Path
import sys
import subprocess
import tomllib

from PySide6.QtCore import Qt, QMargins, Signal
from PySide6.QtGui import QPixmap, QColor
from PySide6.QtWidgets import QApplication, QWidget, QMainWindow, QPushButton, QLabel, QHBoxLayout, QVBoxLayout, QFileDialog, QStackedLayout, QScrollArea, QFrame, QSizePolicy

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
        # TODO i want the resources not to move when the scroll bar appears
        im = QResourceThumbnail(resource_path, self)
        self.content.layout().addWidget(im)

    def rm_resource(self, resource: str|Path|int):
        ... # TODO (resource) can be path or position


class ResourceListContent(QWidget):
    def __init__(self):
        super().__init__()
        self.setLayout(QVBoxLayout(alignment=Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignTop))


class QResourceThumbnail(QFrame):
    def __init__(self, path: str|Path, scroll_area: QScrollArea):
        super().__init__()
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum)
        self.setLayout(QHBoxLayout(alignment=Qt.AlignmentFlag.AlignCenter))
        self.setContentsMargins(QMargins(0, 0, 0, 0))
        self.im = QResourceThumbnailLabel(path, scroll_area, self)
        self.layout().addWidget(self.im)


class QResourceThumbnailLabel(QLabel):
    def __init__(self, path: str|Path, scroll_area: QScrollArea, frame: QFrame):
        # TODO resize should update each time the window is resized
        # TODO fix bug that moves thin images to the left after opening a wide image
        super().__init__()
        self.path = path
        self.frame = frame
        pixmap = QPixmap(path).scaled(.9 * scroll_area.width(), .22 * scroll_area.height(), Qt.AspectRatioMode.KeepAspectRatio) # .9 factor to prevent pictures to be cropped when scroll bar appears
        self.setPixmap(pixmap)

    def enterEvent(self, e):
        super().enterEvent(e)
        self.frame.setStyleSheet(f'QFrame {{background-color: {QColor(227, 227, 125).name()}}};')

    def leaveEvent(self, e):
        super().leaveEvent(e)
        self.frame.setStyleSheet('')


