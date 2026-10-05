from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto, unique
import logging
from pathlib import Path
import sys
import subprocess
import tomllib
from typing import Any, Literal, Self

from PySide6.QtCore import Qt, QMargins, Signal, QMimeData, QPoint, QRect, QEvent
from PySide6.QtGui import QAction, QPixmap, QDrag, QPainter, QBrush, QColor, QPen, QVector2D
from PySide6.QtPdf import QPdfDocument
from PySide6.QtPdfWidgets import QPdfView
from PySide6.QtWidgets import QApplication, QWidget, QMainWindow, QPushButton, QLabel, QHBoxLayout, QVBoxLayout, QFileDialog, QMenu, QStatusBar, QToolBar, QStackedLayout, QScrollArea, QSizePolicy, QFrame

from src.rdw import Corner, Inside, ResizableDragableWidget, Shadow

logging.basicConfig(level=logging.DEBUG, filename='log', filemode='w')


class DrawingArea(QWidget):
    rdw_modified = Signal(QLabel)

    def __init__(self):
        super().__init__()
        self.state: Literal['idle', 'hovering_corner', 'resizing', 'hovering_inside', 'moving'] = 'idle'

        self.rdws = []

    def add_rdw(self, path: str|Path, size: tuple[int, int], pos: tuple[int, int]):
        rdw = ResizableDragableWidget(self, path, size, pos)
        rdw.resizing.connect(self.resize_shadow)
        rdw.resizing_done.connect(self.resize_rdw)
        rdw.moving.connect(self.move_shadow)
        rdw.moving_done.connect(self.move_rdw)
        self.rdws.append(rdw)

    def resize_shadow(self, rdw: ResizableDragableWidget, c: Corner, shift: QVector2D):
        rdw.shadow.resize_when_dragged(c, shift)

    def resize_rdw(self, rdw: ResizableDragableWidget):
        rdw.resize_to_shadow()
        self.rdw_modified.emit(rdw)

    def move_shadow(self, rdw: ResizableDragableWidget, shift: QVector2D):
        rdw.shadow.move_when_dragged(shift)

    def move_rdw(self, rdw: ResizableDragableWidget):
        rdw.move_to_shadow()
        self.rdw_modified.emit(rdw)


# class MainWindow(QMainWindow):
#     def __init__(self):
#         super().__init__()
#         self.setGeometry(0, 0, 800, 600)
#         self.ss = '* {border: 2px solid red;}'
#         self.ss_on = True
#         self.setStyleSheet(self.ss)

#         self.menu = QToolBar()
#         self.action1 = QAction('Stylesheet: on/off')
#         self.action1.triggered.connect(self.ss_on_off)
#         self.action2 = QAction('Move RDW')
#         self.action2.triggered.connect(self.move_rdw)
#         self.action3 = QAction('Scale RDW')
#         self.action3.triggered.connect(self.scale_rdw)
#         self.menu.addActions([self.action1, self.action2, self.action3])
#         self.addToolBar(self.menu)

#         self.central_wid = QWidget()
#         self.central_wid.setLayout(QHBoxLayout())
#         self.rdw = DrawingArea()
#         self.central_wid.layout().addWidget(self.rdw, stretch=1)
#         self.setCentralWidget(self.central_wid)

#     def ss_on_off(self):
#         if self.ss_on:
#             self.setStyleSheet('')
#             self.ss_on = False
#         else:
#             self.setStyleSheet(self.ss)
#             self.ss_on = True

#     def move_rdw(self):
#         self.rdw.img.move((QVector2D(self.rdw.pos()) + QVector2D(50, 50)).toPoint())

#     def scale_rdw(self):
#         px = self.rdw.img.pixmap()
#         self.rdw.img.setPixmap(px.scaled(2 * px.width(), 2 * px.height()))
#         self.rdw.img.adjustSize()


# if __name__ == "__main__":
#     app = QApplication([])
#     window = MainWindow()
#     window.showMaximized()
#     app.exec()
