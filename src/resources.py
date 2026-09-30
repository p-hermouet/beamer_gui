import logging
from pathlib import Path
import sys
import subprocess
import tomllib

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
        path, _ = QFileDialog.getOpenFileName(self, caption='Open resource file', filter='Image files (*.png *.jpg *.jpeg)')
        self.resource_list.add_resource(path)


class ResourceList(QScrollArea):
    double_clicked = Signal(Path)

    def __init__(self):
        super().__init__()
        self.content = ResourceListContent()
        self.setWidget(self.content)
        self.setWidgetResizable(True)

    def add_resource(self, resource_path: str|Path):
        # TODO i want the resources not to move when the scroll bar appears
        im = ResourceThumbnail(resource_path, self)
        if not im.im.pixmap().isNull():
            self.content.layout().addWidget(im)

    def rm_resource(self, resource: str|Path|int):
        ... # TODO (resource) can be path or position


class ResourceListContent(QWidget):
    def __init__(self):
        super().__init__()
        self.setLayout(QVBoxLayout(alignment=Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignTop))


class ResourceThumbnail(QFrame):
    def __init__(self, path: str|Path, scroll_area: QScrollArea):
        super().__init__()
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum)
        self.setContentsMargins(QMargins(0, 0, 0, 0))

        self.path = path
        self.scroll_area = scroll_area

        self.im = ResourceThumbnailLabel(path, scroll_area)

        self.setLayout(QHBoxLayout(alignment=Qt.AlignmentFlag.AlignCenter))
        self.layout().addWidget(self.im)

    def mouseDoubleClickEvent(self, e):
        super().mouseDoubleClickEvent(e)
        self.scroll_area.double_clicked.emit(self.path)

    def enterEvent(self, e):
        super().enterEvent(e)
        self.setStyleSheet(f'QFrame {{background-color: {QColor(227, 227, 125).name()}}};')

    def leaveEvent(self, e):
        super().leaveEvent(e)
        self.setStyleSheet('')

class ResourceThumbnailLabel(QLabel):
    def __init__(self, path: str|Path, scroll_area: QScrollArea):
        # TODO resize should update each time the window is resized
        # TODO fix bug that moves thin images to the left after opening a wide image
        super().__init__()
        pixmap = QPixmap(path)
        if not pixmap.isNull():
            pixmap = pixmap.scaled(.9 * scroll_area.width(), .22 * scroll_area.height(), Qt.AspectRatioMode.KeepAspectRatio) # .9 factor to prevent pictures to be cropped when scroll bar appears
        self.setPixmap(pixmap)


class FloatingResource(QLabel):
    def __init__(self, path:str|Path, pdf_view: QPdfView):
        super().__init__(pdf_view)
        self.setStyleSheet('QLabel {border: 2px solid blue;}')

        self.path = path
        self.offset = 0., 0.

        w, h = pdf_view.size().width(), pdf_view.size().height()
        pixmap = QPixmap(path).scaled(w/10, h/10, Qt.AspectRatioMode.KeepAspectRatio)
        self.setPixmap(pixmap)

        x = (pdf_view.x() + pdf_view.width()) / 2
        y = (pdf_view.y() + pdf_view.height()) / 2
        self.setGeometry(x, y, pixmap.width(), pixmap.height())

        self.show()

    def mouseMoveEvent(self, ev):
        super().mouseMoveEvent(ev)
        if ev.buttons() == Qt.MouseButton.LeftButton:
            drag = QDrag(self)
            pixmap = QPixmap(self.size())
            self.render(pixmap)
            drag.setMimeData(QMimeData())
            drag.setPixmap(pixmap)
            offset = drag.hotSpot()
            drag.setHotSpot(ev.pos())
            self.offset = ev.pos() - offset
            drag.exec(Qt.DropAction.MoveAction)
