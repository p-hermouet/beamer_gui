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
            self.rdw.shadow.activate()
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
            self.rdw.shadow.activate()
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

    def activate(self):
        self.setPixmap(QPixmap(self.rdw.pixmap()))
        self.move(self.rdw.pos())
        self.adjustSize()
        self.setVisible(True)
        self.rdw.setVisible(False)

    def resize_when_dragged(self, c: Corner, shift: QVector2D):
        # compute cursor projection
        proj = QVector2D.dotProduct(shift, c.direc.normalized()) * c.direc.normalized()
        # resize and move shadow
        new_px_size =  QVector2D(*c.rdw.size().toSizeF().toTuple()) + c.coef * proj
        if new_px_size.x() >= 2 * Corner.radius and new_px_size.y() >= 2 * Corner.radius:
            c.rdw.shadow.setPixmap(c.rdw.px.scaled(*new_px_size.toTuple(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
            c.rdw.shadow.move((QVector2D(c.rdw.pos().toPointF()) + c.coefQFT * proj).toPoint())
            c.rdw.shadow.adjustSize()

    def move_when_dragged(self, shift: QVector2D):
        new_pos = QVector2D(self.rdw.pos()) + shift - self.rdw.inside.drag_anchor
        if 0 <= new_pos.x() <= self.area.size().width() - Corner.radius and 0 <= new_pos.y() <= self.area.size().height() - Corner.radius:
            self.rdw.shadow.move(new_pos.toPoint())


class ResizableDragableWidget(QLabel):
    resizing = Signal(QLabel, Corner, QVector2D)
    resizing_done = Signal(QLabel)
    moving = Signal(QLabel, QVector2D)
    moving_done = Signal(QLabel)


    def __init__(self, area: DrawingArea, path: str|Path, size: tuple[int, int], pos: tuple[int, int]):
        # TODO: ideally, i should not need to know that area is a DrawingArea. All use of self.area.<...> should be replaced by signals sent to the DrawingArea instance.
        super().__init__(parent=area)
        self.area = area
        self.path = path
        # self.setStyleSheet('QLabel {border: 2px solid red;}')

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

    def resize_to_shadow(self):
        self.setPixmap(QPixmap(self.shadow.pixmap()))
        self.adjustSize()
        self.move(self.shadow.pos())
        self.state = 'idle'
        self.adapt_components()
        self.shadow.setVisible(False)
        self.setVisible(True)

    def move_to_shadow(self):
        self.move(self.shadow.pos())
        self.state = 'idle'
        self.shadow.setVisible(False)
        self.setVisible(True)

    def resizeEvent(self, event):
        # TODO: it never gets called, figure out why; i currently circumvent it by calling directly self.adapt_components when needed
        self.adapt_components()

    def moveEvent(self, event):
        self.adapt_components()
