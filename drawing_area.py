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

logging.basicConfig(level=logging.DEBUG, filename='log', filemode='w')


class Corner(QFrame):
    radius = 10
    resizing = Signal(QFrame, QVector2D)
    resizing_done = Signal()

    def __init__(self, rdw: ResizableDragableWidget, coef: QVector2D):
        super().__init__(parent=rdw.area)
        self.setMouseTracking(True)
        self.show()

        self.coef = coef
        self.direc = coef * QVector2D(*rdw.size().toTuple())
        self.rdw = rdw
        self.area = rdw.area

        self.adapt_to_rdw()

    @property
    def coefQFT(self):
        return QVector2D(int(self.coef.x() < 0), int(self.coef.y() < 0))

    @property
    def c_pos(self):
        return QVector2D(self.rdw.pos()) + (QVector2D(1, 1) - self.coefQFT) * QVector2D(*self.rdw.size().toTuple())

    def adapt_to_rdw(self):
        self.setGeometry(*(self.c_pos - QVector2D(self.radius, self.radius)).toTuple(), 2 * self.radius, 2 * self.radius)

    def mouseMoveEvent(self, event):
        if self.area.state == 'idle':
            self.area.state = 'hovering_corner'
            if self.coef in [QVector2D(-1, -1), QVector2D(1, 1)]:
                self.setCursor(Qt.CursorShape.SizeFDiagCursor)
            else:
                self.setCursor(Qt.CursorShape.SizeBDiagCursor)
        elif self.area.state == 'resizing':
            self.resizing.emit(self, QVector2D(event.position()) - QVector2D(self.radius, self.radius))
        event.accept()

    def leaveEvent(self, event):
        self.area.state = 'idle'
        event.accept()

    def mousePressEvent(self, event):
        if self.area.state == 'hovering_corner':
            self.area.state = 'resizing'
            self.rdw.shadow.init()
        event.accept()

    def mouseReleaseEvent(self, event):
        if self.area.state == 'resizing':
            self.area.state = 'idle'
            self.resizing_done.emit()
        event.accept()


class Inside(QFrame):
    moving = Signal(QVector2D)
    moving_done = Signal()

    def __init__(self, rdw: ResizableDragableWidget):
        super().__init__(parent=rdw.area)
        self.setMouseTracking(True)
        self.show()

        self.rdw = rdw
        self.area = rdw.area
        self.drag_anchor: QVector2D = None

        self.adapt_to_rdw()

    def adapt_to_rdw(self):
        self.setGeometry(self.rdw.pos().x() + Corner.radius, self.rdw.pos().y() + Corner.radius,
                         self.rdw.width() - 2 * Corner.radius, self.rdw.height() - 2 * Corner.radius)

    def swap_with_shadow(self):
        ...

    def resize_to_shadow(self):
        ...

    def move_to_shadow(self):
        ...

    def mouseMoveEvent(self, event):
        if self.area.state == 'idle':
            self.area.state = 'hovering_inside'
            self.setCursor(Qt.CursorShape.OpenHandCursor)
        elif self.area.state == 'moving':
            self.moving.emit(QVector2D(event.position()))
        event.accept()

    def leaveEvent(self, event):
            self.area.state = 'idle'
            event.accept()

    def mousePressEvent(self, event):
        if self.area.state == 'hovering_inside':
            self.area.state = 'moving'
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            self.drag_anchor = QVector2D(event.position())
            self.rdw.shadow.init()
        event.accept()

    def mouseReleaseEvent(self, event):
        if self.area.state == 'moving':
            self.area.state = 'idle'
            self.moving_done.emit()
        event.accept()


class Shadow(QLabel):
    def __init__(self, rdw: ResizableDragableWidget):
        super().__init__(rdw.area)
        self.setVisible(False)

        self.rdw = rdw
        self.area = rdw.area

    def init(self):
        self.setPixmap(QPixmap(self.rdw.pixmap()))
        self.move(self.rdw.pos())
        self.adjustSize()
        self.setVisible(True)
        self.rdw.setVisible(False)

    def resize_when_dragged(self):
        ...


class ResizableDragableWidget(QLabel):
    resizing = Signal(QLabel, Corner, QVector2D)
    resizing_done = Signal(QLabel)
    moving = Signal(QLabel, QVector2D)
    moving_done = Signal(QLabel)


    def __init__(self, area: DrawingArea, path: str|Path, size, pos):
        super().__init__(parent=area)
        self.area = area

        self.px = QPixmap(path)
        self.setPixmap(self.px.scaled(*size, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        self.move(*pos)
        self.adjustSize()
        self.show()

        self.inside = Inside(self)
        self.corner_tl = Corner(self, QVector2D(-1, -1))
        self.corner_tr = Corner(self, QVector2D(1, -1))
        self.corner_br = Corner(self, QVector2D(1, 1))
        self.corner_bl = Corner(self, QVector2D(-1, 1))
        self.shadow = Shadow(self)

        for c in [self.corner_tl, self.corner_tr, self.corner_br, self.corner_bl]:
            c.resizing.connect(lambda c, shift: self.resizing.emit(self, c, shift))
            c.resizing_done.connect(lambda: self.resizing_done.emit(self))
        self.inside.moving.connect(lambda shift: self.moving.emit(self, shift))
        self.inside.moving_done.connect(lambda: self.moving_done.emit(self))

    def adapt_components(self):
        for c in [self.corner_tl, self.corner_tr, self.corner_br, self.corner_bl]:
            c.adapt_to_rdw()
        self.inside.adapt_to_rdw()

    def resizeEvent(self, event):
        self.adapt_components()

    def moveEvent(self, event):
        self.adapt_components()


class DrawingArea(QWidget):
    def __init__(self):
        super().__init__()
        self.state: Literal['idle', 'hovering_corner', 'resizing', 'hovering_inside', 'moving'] = 'idle'

        self.rdws = [ResizableDragableWidget(self, 'static/snow.jpg', (200, 200), (300, 200)),
                     ResizableDragableWidget(self, 'static/pp.png', (200, 200), (100, 200))]

        for rdw in self.rdws:
            rdw.resizing.connect(self.resize_shadow)
            rdw.resizing_done.connect(self.resize_rdw)
            rdw.moving.connect(self.move_shadow)
            rdw.moving_done.connect(self.move_rdw)

    def resize_shadow(self, rdw: ResizableDragableWidget, c: Corner, shift: QVector2D):
        # compute cursor projection
        proj = QVector2D.dotProduct(shift, c.direc.normalized()) * c.direc.normalized()
        # resize and move shadow
        rdw.shadow.setPixmap(rdw.px.scaled(
            *(QVector2D(*rdw.size().toSizeF().toTuple()) + c.coef * proj).toTuple(),
            Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        rdw.shadow.move((QVector2D(rdw.pos().toPointF()) + c.coefQFT * proj).toPoint())
        rdw.shadow.adjustSize()

    def resize_rdw(self, rdw: ResizableDragableWidget):
        rdw.setPixmap(QPixmap(rdw.shadow.pixmap()))
        rdw.move(rdw.shadow.pos())
        rdw.adjustSize()

        self.state = 'idle'
        rdw.shadow.setVisible(False)
        rdw.setVisible(True)

    def move_shadow(self, rdw: ResizableDragableWidget, shift: QVector2D):
        rdw.shadow.move((QVector2D(rdw.pos()) + shift - rdw.inside.drag_anchor).toPoint())

    def move_rdw(self, rdw: ResizableDragableWidget):
        rdw.move(rdw.shadow.pos())

        self.state = 'idle'
        rdw.shadow.setVisible(False)
        rdw.setVisible(True)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setGeometry(0, 0, 800, 600)
        self.ss = '* {border: 2px solid red;}'
        self.ss_on = True
        self.setStyleSheet(self.ss)

        self.menu = QToolBar()
        self.action1 = QAction('Stylesheet: on/off')
        self.action1.triggered.connect(self.ss_on_off)
        self.action2 = QAction('Move RDW')
        self.action2.triggered.connect(self.move_rdw)
        self.action3 = QAction('Scale RDW')
        self.action3.triggered.connect(self.scale_rdw)
        self.menu.addActions([self.action1, self.action2, self.action3])
        self.addToolBar(self.menu)

        self.central_wid = QWidget()
        self.central_wid.setLayout(QHBoxLayout())
        self.rdw = DrawingArea()
        self.central_wid.layout().addWidget(self.rdw, stretch=1)
        self.setCentralWidget(self.central_wid)

    def ss_on_off(self):
        if self.ss_on:
            self.setStyleSheet('')
            self.ss_on = False
        else:
            self.setStyleSheet(self.ss)
            self.ss_on = True

    def move_rdw(self):
        self.rdw.img.move((QVector2D(self.rdw.pos()) + QVector2D(50, 50)).toPoint())

    def scale_rdw(self):
        px = self.rdw.img.pixmap()
        self.rdw.img.setPixmap(px.scaled(2 * px.width(), 2 * px.height()))
        self.rdw.img.adjustSize()


if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.showMaximized()
    app.exec()
