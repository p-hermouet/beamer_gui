from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto, unique
import logging
from pathlib import Path
import sys
import subprocess
import tomllib
from typing import Any, Literal, Self

from PySide6.QtCore import Qt, QMargins, Signal, QMimeData, QPoint, QRect, QEvent, QSize
from PySide6.QtGui import QAction, QPixmap, QDrag, QPainter, QBrush, QColor, QPen, QVector2D, QCursor
from PySide6.QtPdf import QPdfDocument
from PySide6.QtPdfWidgets import QPdfView
from PySide6.QtWidgets import QApplication, QWidget, QMainWindow, QPushButton, QLabel, QHBoxLayout, QVBoxLayout, QFileDialog, QMenu, QStatusBar, QToolBar, QStackedLayout, QScrollArea, QSizePolicy, QFrame

from src.rdw import Corner, Inside, ResizableDragableWidget, Shadow, Mask

logging.basicConfig(level=logging.DEBUG, filename='log', filemode='w')


class MainStruc(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet('QWidget {background-color: AliceBlue;}')
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(TitleStruc(), stretch=15)
        self.layout().addWidget(BodyStruc(), stretch=85)

    def fit_pdf(self, size: tuple[float, float]):
        self.setFixedSize(*size)


class Sep(QFrame):
    thiness = 10
    mouse_moving = Signal(QPoint)

    def __init__(self, direction: Literal['h', 'v']):
        super().__init__()
        self.direction = direction

        self.setStyleSheet('QFrame {background-color: gray;}')
        self.setMouseTracking(True)
        if self.direction == 'h':
            self.setFixedWidth(self.thiness)
        else:
            self.setFixedHeight(self.thiness)

    def mouseMoveEvent(self, event):
        if self.direction == 'h':
            self.setCursor(Qt.CursorShape.SplitHCursor)
        else:
            self.setCursor(Qt.CursorShape.SplitVCursor)
        self.mouse_moving.emit(event.pos())

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.parent().status = 'resizing'

    def mouseReleaseEvent(self, event):
        self.parent().status = 'idle'


class Struc(QFrame):
    stretch_steps = 1000
    dividing = Signal(str, QFrame)

    def __init__(self):
        super().__init__()
        self.status: Literal['idle', 'resizing'] = 'idle'
        self.direction: Literal['h', 'v'] = None
        self.children_strucs: list[Self] = [] # TODO: use a property iterating over self.children instead
        self.seps: list[Sep] = [] # TODO: use a property iterating over self.children instead

        self.setMouseTracking(True)
        self.setObjectName('struc')
        self.setStyleSheet('#struc {border: 2px dashed black;}') # TODO: replace with paintevent

        self.init_menu()

    def init_menu(self):
        self.context_menu = QMenu(self)
        h_div_action = QAction('Divide Horizontally', self)
        h_div_action.triggered.connect(lambda: self.dividing.emit('h', self))
        self.context_menu.addAction(h_div_action)
        v_div_action = QAction('Divide Vertically', self)
        v_div_action.triggered.connect(lambda: self.dividing.emit('v', self))
        self.context_menu.addAction(v_div_action)
        suppr_action = QAction('Delete', self)
        suppr_action.triggered.connect(self.delete)
        self.context_menu.addAction(suppr_action)

    def on_div_triggered(self, direction: Literal['h', 'v'], children: Self):
        if direction == self.direction:
            self.div(direction)
        else:
            children.div(direction)

    def div(self, direction: Literal['h', 'v']):
        self.direction = direction

        if not self.children_strucs:
            layout = QHBoxLayout() if direction == 'h' else QVBoxLayout()
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(0)

            l_struc = Struc()
            l_struc.dividing.connect(self.on_div_triggered)
            self.children_strucs.append(l_struc)
            layout.addWidget(l_struc)

            self.setLayout(layout)

        sep = Sep(direction)
        sep.mouse_moving.connect(self.restretch)
        self.seps.append(sep)
        self.layout().addWidget(sep)

        r_struc = Struc()
        r_struc.dividing.connect(self.on_div_triggered)
        self.children_strucs.append(r_struc)
        self.layout().addWidget(r_struc)


    def delete(self):
        print('delete') # TODO: implement this method

    def contextMenuEvent(self, event):
        self.context_menu.popup(QCursor.pos())

    def restretch(self, pos: QPoint):
        if self.status == 'resizing':
            x, y = self.sep.x() + pos.x(), self.sep.y() + pos.y()
            if 0 <= x <= self.width() and 0 <= y <= self.height():
                if isinstance(self.layout().__class__, QHBoxLayout()):
                    prop = x / self.width()
                else:
                    prop = y / self.height()
                self.layout().setStretch(0, 100)
                self.layout().setStretch(2, round(100/prop - 100)) # TODO: change that so the streches' sum is 1000


class BodyStruc(Struc):
    def init_menu(self):
        self.context_menu = QMenu(self)
        h_div_action = QAction('Divide Horizontally', self)
        h_div_action.triggered.connect(lambda: self.div('h'))
        self.context_menu.addAction(h_div_action)
        v_div_action = QAction('Divide Vertically', self)
        v_div_action.triggered.connect(lambda: self.div('v'))
        self.context_menu.addAction(v_div_action)


class TitleStruc(QLabel):
    def __init__(self):
        super().__init__('Title')
        self.setObjectName('title_struc')
