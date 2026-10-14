from __future__ import annotations

import logging
from pathlib import Path
import sys
import subprocess
import tomllib
from typing import Any, Literal

from PySide6.QtCore import Qt, QMargins, Signal, QMimeData, QPoint, QRect, QEvent
from PySide6.QtGui import QAction, QPixmap, QDrag, QPainter, QBrush, QColor, QPen, QVector2D
from PySide6.QtPdf import QPdfDocument
from PySide6.QtPdfWidgets import QPdfView
from PySide6.QtWidgets import QApplication, QWidget, QMainWindow, QPushButton, QLabel, QHBoxLayout, QVBoxLayout, QFileDialog, QMenu, QStatusBar, QToolBar, QStackedLayout, QScrollArea, QSizePolicy, QFrame

from src.drawing_area import DrawingArea

logging.basicConfig(level=logging.DEBUG, filename='log', filemode='w')


class Shadow(QLabel):
    def __init__(self, parent):
        super().__init__(parent)

        self.destroyed.connect(lambda: print(__class__.__name__, 'destroyed')) # debug


class Corner(QFrame):
    left_clicked = Signal(int, int)
    released = Signal(int, int)
    moved = Signal(float, float)

    def __init__(self, parent, id: tuple[int, int], radius: int):
        super().__init__(parent)
        self.id = id
        self.setGeometry(id[0] * (parent.width() - 2 * radius),
                         id[1] * (parent.height() - 2 * radius),
                        2 * radius, 2 * radius)
        self.setMouseTracking(True)
        self.show()

        self.setStyleSheet('QFrame {background-color: blue;}') # debug
        self.destroyed.connect(lambda: print(__class__.__name__, 'destroyed')) # debug

    def mouseMoveEvent(self, event):
        self.moved.emit(*event.position().toTuple())
        if self.id in [(0, 0), (1, 1)]:
            self.setCursor(Qt.CursorShape.SizeFDiagCursor)
        else:
            self.setCursor(Qt.CursorShape.SizeBDiagCursor)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.left_clicked.emit(*self.id)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.released.emit(*self.id)

class Image(QLabel):
    left_clicked = Signal()
    released = Signal()
    moved = Signal(float, float)

    def __init__(self, parent, path: str|Path, size: QVector2D, radius: int):
        super().__init__(parent)
        self.path = path

        self.px = QPixmap(path)
        self.setPixmap(self.px.scaled(*size.toTuple(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        self.adjustSize()

        self.move(radius, radius)
        self.setMouseTracking(True)
        self.show()

        self.destroyed.connect(lambda: print(__class__.__name__, 'destroyed')) # debug

    def mouseMoveEvent(self, ev):
        self.setCursor(Qt.CursorShape.OpenHandCursor)
        self.moved.emit(*ev.position().toTuple())

    def mousePressEvent(self, event):
            if event.button() == Qt.MouseButton.LeftButton:
                self.left_clicked.emit()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.released.emit()


class RDW(QFrame):
    corner_radius = 5
    corner_left_clicked = Signal(QFrame, int, int)
    corner_released = Signal(QFrame, int, int)
    img_left_clicked = Signal(QFrame)
    img_released = Signal(QFrame)
    moved = Signal(QFrame, float, float)

    def __init__(self, parent, path: str|Path, pos: QPoint, size: QVector2D):
        super().__init__(parent)
        self.path = path
        self.setGeometry(*pos.toTuple(), *size.toTuple())

        self.img = Image(self, path, size, self.corner_radius)
        self.resize(self.img.width() + 2 * self.corner_radius,
                    self.img.height() + 2 * self.corner_radius)
        self.corner_tl = Corner(self, (0, 0), self.corner_radius)
        self.corner_bl = Corner(self, (0, 1), self.corner_radius)
        self.corner_tr = Corner(self, (1, 0), self.corner_radius)
        self.corner_br = Corner(self, (1, 1), self.corner_radius)
        self.shadow = Shadow(self)

        self.img.left_clicked.connect(lambda: self.img_left_clicked.emit(self))
        self.img.released.connect(lambda: self.img_released.emit(self))
        self.img.moved.connect(lambda x, y: self.moved.emit(self, x, y))
        for c in [self.corner_tl, self.corner_bl, self.corner_tr, self.corner_br]:
            c.left_clicked.connect(lambda x, y: self.corner_left_clicked.emit(self, x, y))
            c.released.connect(lambda x, y: self.corner_released.emit(self, x, y))
            c.moved.connect(lambda x, y: self.moved.emit(self, x, y))

        self.show()

        self.setStyleSheet('QFrame {background-color: pink;}') # debug
        self.destroyed.connect(lambda: print(__class__.__name__, 'destroyed')) # debug

    def activate_shadow(self):
        self.shadow.setPixmap(QPixmap(self.img.pixmap()))
        self.shadow.move(self.img.pos())
        self.shadow.adjustSize()
        self.shadow.setVisible(True)
        self.img.setVisible(False)

    def deactivate_shadow(self):
        self.shadow.setVisible(False)
        self.img.setVisible(True)


class DrawingArea(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self._status: Literal['idle', 'resizing', 'moving'] = 'idle'
        self.rdw_selected: RDW = None
        self.rdws: list[RDW] = []
        self.show()

        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet('QWidget {background-color: red;}')

    def add_rdw(self, path: str|Path):
        rdw = RDW(self, path, QPoint(400, 200), QPoint(400, 400))
        self.rdws.append(rdw)
        rdw.corner_left_clicked.connect(self.on_corner_left_clicked)
        rdw.corner_released.connect(self.on_corner_released)
        rdw.img_left_clicked.connect(self.on_img_left_clicked)
        rdw.img_released.connect(self.on_img_released)
        rdw.moved.connect(self.on_rdw_moved)

    @property # debug
    def status(self): return self._status
    @status.setter
    def status(self, s: str):
        print(f'status changing from {self.status} to {s}')
        self._status = s

    def on_corner_left_clicked(self, rdw: RDW, idx: int, idy: int):
        if self.status == 'idle':
            self.rdw_selected = rdw
            self.status = 'resizing'
            rdw.activate_shadow()

    def on_corner_released(self, rdw: RDW, idx: int, idy: int):
        if self.status == 'resizing':
            print('blii')
            self.rdw_selected = None
            self.status = 'idle'
            rdw.deactivate_shadow()

    def on_img_left_clicked(self, rdw: RDW):
        if self.status == 'idle':
            self.rdw_selected = rdw
            self.status = 'moving'
            rdw.activate_shadow()

    def on_img_released(self, rdw: RDW):
        if self.status == 'moving':
            self.rdw_selected = None
            self.status = 'idle'
            rdw.deactivate_shadow()

    def on_rdw_moved(self, rdw: RDW, x: float, y: float):
        if self.rdw_selected == rdw:
            if self.status == 'moving':
                # o_pos = QVector2D(rdw.img.pos())

                # rdw.shadow.move()
                print(rdw.img.pos())
            elif self.status == 'resizing':
                ...

    def mouseMoveEvent(self, event):
        # if self.status == 'moving':
        ...


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.menu = QToolBar()
        action = QAction('size', self)
        action.triggered.connect(lambda: print(self.area.size()))
        self.menu.addAction(action)
        self.addToolBar(self.menu)

        self.area = DrawingArea(self)
        self.area.setLayout(QVBoxLayout())
        # self.area.add_rdw('static/pp.png')
        self.area.add_rdw('static/snow.jpg')

        self.container = QWidget()
        self.container.setLayout(QVBoxLayout())
        self.container.layout().addWidget(self.area, stretch=1)
        self.container.layout().addWidget(QWidget(), stretch=1)
        self.setCentralWidget(self.container)

if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.showMaximized()
    app.exec()
