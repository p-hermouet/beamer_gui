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
    mouse_moving = Signal(QPoint, QFrame)

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
        self.mouse_moving.emit(event.pos(), self)

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

    @property
    def children_strucs(self):
        return [self.layout().itemAt(i).widget() for i in range(self.layout().count())
                if isinstance(self.layout().itemAt(i).widget(), __class__)]

    @property
    def seps(self):
        return [self.layout().itemAt(i).widget() for i in range(self.layout().count())
                if isinstance(self.layout().itemAt(i).widget(), Sep)]

    def add_child_struc(self, stretch: int, index:int = -1):
        struc = Struc()
        struc.dividing.connect(self.on_div_triggered)
        self.layout().insertWidget(index, struc, stretch)

    def add_step(self, direction: Literal['h', 'v'], index: int=-1):
        sep = Sep(direction)
        sep.mouse_moving.connect(self.restretch)
        self.layout().insertWidget(index, sep)

    def first_div(self, direction: Literal['h', 'v']):
        self.direction = direction
        layout = QHBoxLayout() if direction == 'h' else QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.setLayout(layout)

        self.add_child_struc(self.stretch_steps // 2)
        self.add_step(direction)
        self.add_child_struc(self.stretch_steps // 2)

    def new_div(self, direction: Literal['h', 'v'], child: Self):
        idx = self.layout().indexOf(child)
        stretch = self.layout().stretch(idx)
        self.add_step(direction, index=idx)
        self.layout().setStretchFactor(child, stretch // 2)
        self.add_child_struc(stretch - stretch // 2, index=idx)

    def on_div_triggered(self, direction: Literal['h', 'v'], child: Self):
        if direction == self.direction:
            self.new_div(direction, child)
        else:
            child.first_div(direction)

    def delete(self):
        print('delete') # TODO: implement this method

    def contextMenuEvent(self, event):
        self.context_menu.popup(QCursor.pos())

    def restretch(self, pos: QPoint, sep: Sep):
        if self.status == 'resizing':
            idx = self.seps.index(sep)
            l_struc = self.children_strucs[idx]
            r_struc = self.children_strucs[idx + 1]
            x, y = sep.x() + pos.x(), sep.y() + pos.y()
            if l_struc.x() <= x <= r_struc.x() + r_struc.width() and l_struc.y() <= y <= r_struc.y() + r_struc.height():
                if self.direction == 'h':
                    prop = (x - l_struc.x()) / (l_struc.width() + r_struc.width())
                else:
                    prop = (y - l_struc.y()) / (l_struc.height() + r_struc.height())
                tot_stretch = self.layout().stretch(self.layout().indexOf(l_struc)) +\
                    self.layout().stretch(self.layout().indexOf(r_struc))
                self.layout().setStretchFactor(l_struc, int(tot_stretch * prop))
                self.layout().setStretchFactor(r_struc, tot_stretch - int(tot_stretch * prop))


class BodyStruc(Struc):
    def init_menu(self):
        self.context_menu = QMenu(self)
        h_div_action = QAction('Divide Horizontally', self)
        h_div_action.triggered.connect(lambda: self.first_div('h'))
        self.context_menu.addAction(h_div_action)
        v_div_action = QAction('Divide Vertically', self)
        v_div_action.triggered.connect(lambda: self.first_div('v'))
        self.context_menu.addAction(v_div_action)


class TitleStruc(QLabel):
    def __init__(self):
        super().__init__('Title')
        self.setObjectName('title_struc')
