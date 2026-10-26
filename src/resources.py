import logging
from pathlib import Path
import sys
import subprocess
import tomllib
from typing import Literal

from PySide6.QtCore import Qt, QMargins, Signal, QMimeData
from PySide6.QtGui import QPixmap, QColor, QDrag
from PySide6.QtPdfWidgets import QPdfView
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
        path, _ = QFileDialog.getOpenFileName(self, caption='Open resource file', filter='Image files (*.png *.jpg *.jpeg, *.svg)')
        self.resource_list.add_resource(path)


class ResourceList(QScrollArea):
    def __init__(self):
        super().__init__()
        self.content = ResourceListContent()
        self.setWidget(self.content)
        self.setWidgetResizable(True)

    def add_resource(self, resource_path: str|Path):
        self.content.add_resource(resource_path)

    def rm_resource(self, resource: QWidget):
        self.content.rm_resource(resource)


class ResourceListContent(QWidget):
    double_clicked = Signal(Path)

    def __init__(self):
        super().__init__()
        self.setLayout(QVBoxLayout(alignment=Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignTop))

    def add_resource(self, resource_path: str|Path):
        # TODO i want the resources not to move when the scroll bar appears
        im = ResourceThumbnail(resource_path, self)
        if not im.im.pixmap().isNull():
            self.layout().addWidget(im)
            im.destroyed_resource.connect(self.rm_resource)
            im.double_clicked.connect(self.double_clicked.emit)

    def rm_resource(self, resource: QWidget):
        self.layout().removeWidget(resource)
        resource.deleteLater()


class ResourceThumbnail(QFrame):
    destroyed_resource = Signal(QWidget)
    double_clicked = Signal(Path)

    def __init__(self, path: str|Path, scroll_area: QScrollArea):
        super().__init__()
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum)
        self.setContentsMargins(QMargins(0, 0, 0, 0))

        self.path = path
        self.scroll_area = scroll_area

        self.im = ResourceThumbnailLabel(path, scroll_area)
        self.cross = Cross(self, self.im)

        self.setLayout(QHBoxLayout(alignment=Qt.AlignmentFlag.AlignCenter))
        self.layout().addWidget(self.im)
        self.im.stackUnder(self.cross)

        self.cross.destroy_resource.connect(lambda: self.destroyed_resource.emit(self))

    def mouseDoubleClickEvent(self, e):
        super().mouseDoubleClickEvent(e)
        self.double_clicked.emit(self.path)

    def enterEvent(self, e):
        super().enterEvent(e)
        self.setStyleSheet(f'QFrame {{background-color: {QColor(227, 227, 125).name()}}};')
        self.cross.setVisible(True)

    def leaveEvent(self, e):
        super().leaveEvent(e)
        self.setStyleSheet('')
        self.cross.setVisible(False)

class ResourceThumbnailLabel(QLabel):
    def __init__(self, path: str|Path, scroll_area: QScrollArea):
        # TODO resize should update each time the window is resized
        # TODO fix bug that moves thin images to the left after opening a wide image
        super().__init__()
        pixmap = QPixmap(path)
        if not pixmap.isNull():
            pixmap = pixmap.scaled(.9 * scroll_area.width(), .22 * scroll_area.height(), Qt.AspectRatioMode.KeepAspectRatio) # .9 factor to prevent pictures to be cropped when scroll bar appears
        self.setPixmap(pixmap)


class Cross(QLabel):
    destroy_resource = Signal()

    def __init__(self, parent, tb: ResourceThumbnailLabel):
        super().__init__(parent)
        self.px = QPixmap('icons/xmark-square-solid.svg')
        self.setPixmap(self.px.scaled(.05 * parent.width(), .05 * parent.width(), Qt.AspectRatioMode.KeepAspectRatio))
        self.adjustSize()
        self.move(tb.pos())

    def enterEvent(self, event):
        super().enterEvent(event)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def leaveEvent(self, event):
        super().leaveEvent(event)
        self.unsetCursor()

    def mousePressEvent(self, ev):
        self.destroy_resource.emit()
