from __future__ import annotations

import logging
from pathlib import Path
import sys
import subprocess
import tomllib
from typing import Any, Literal

from PySide6.QtCore import Qt, QMargins, Signal, QMimeData, QPoint, QRect
from PySide6.QtGui import QAction, QPixmap, QDrag, QPainter, QBrush, QColor, QPen, QVector2D
from PySide6.QtPdf import QPdfDocument
from PySide6.QtPdfWidgets import QPdfView
from PySide6.QtWidgets import QApplication, QWidget, QMainWindow, QPushButton, QLabel, QHBoxLayout, QVBoxLayout, QFileDialog, QMenu, QStatusBar, QToolBar, QStackedLayout, QScrollArea, QSizePolicy, QFrame

logging.basicConfig(level=logging.DEBUG, filename='log', filemode='w')


class Shadow(QLabel):
    def __init__(self, rdw: ResizableDraggableImg):
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

    def resize(self):
        ...


class ResizableDraggableImg(QLabel):
    corner_radius = 10

    def __init__(self, parent: DrawingArea, path: str|Path):
        super().__init__(parent)
        self.setStyleSheet('QLabel {border: 1px solid blue;}')
        self.area = parent

        self.px = QPixmap(path)
        self.setPixmap(self.px.scaled(200, 200, Qt.AspectRatioMode.KeepAspectRatio))
        self.move(300, 200)
        self.show()

        self.shadow = Shadow(self)

    @property
    def tl(self): return QVector2D(self.pos())
    @property
    def br(self): return QVector2D(self.x() + self.width(), self.y() + self.height())
    @property
    def tr(self): return QVector2D(self.br.x(), self.tl.y())
    @property
    def bl(self): return QVector2D(self.tl.x(), self.br.y())

    def opposed_corner(self, corner: QVector2D):
        match corner:
            case self.tl: return self.br
            case self.br: return self.tl
            case self.tr: return self.bl
            case self.bl: return self.tr

    def new_tl(self, corner: QVector2D, new_diag: QVector2D):
        match corner:
            case self.tl: return self.br + new_diag
            case self.br: return self.tl
            case self.tr: return QVector2D(self.tl.x(), self.bl.y() + new_diag.y())
            case self.bl: return QVector2D(self.tr.x() + new_diag.x(), self.tl.y())

    def cursor_on_corner(self, pos) -> QVector2D:
        '''Return which corner the cursor is near, or None if not near either.'''
        for c in [self.tl, self.tr, self.bl, self.br]:
            if (pos.x() - c.x())**2 + (pos.y() - c.y())**2 <= self.corner_radius**2:
                return c

    def init_resized_shadow(self):
        self.shadow.setPixmap(QPixmap(self.pixmap()))
        self.shadow.setStyleSheet('QLabel {border: 1px solid red;}')
        self.shadow.move(self.pos())
        self.shadow.setVisible(True)
        self.shadow.adjustSize()
        self.setVisible(False)


class DrawingArea(QFrame):
    def __init__(self):
        super().__init__()
        # self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        self.img = ResizableDraggableImg(self, 'static/snow.jpg')
        self.state: Literal['idle', 'hovering', 'resizing', 'cancel_resizing'] = 'idle'

    def mouseMoveEvent(self, ev):
        # change cursor shape and state
        if self.state == 'idle' or self.state == 'hovering':
            if c := self.img.cursor_on_corner(ev.position()):
                self.state = 'hovering'
                self.state.corner = c
                self.state.target_wid = self.img
                if c in [self.img.tl, self.img.br]:
                    self.setCursor(Qt.CursorShape.SizeFDiagCursor)
                else:
                    self.setCursor(Qt.CursorShape.SizeBDiagCursor)
            else:
                self.state = 'idle'
                self.unsetCursor()
        # resize floating image's shadow
        elif self.state == 'resizing':
            c = self.state.corner
            opp_c = self.img.opposed_corner(c)
            img = self.state.target_wid

            curs_vec = QVector2D(ev.position()) - opp_c
            diag = c - opp_c
            new_diag = QVector2D.dotProduct(curs_vec, diag.normalized()) * diag.normalized()

            # print(img.shadow.rect)
            if any(x <= 0 for x in (diag / new_diag).toTuple()):
                self.state = 'cancel_resizing'
            else:
                img.shadow.setPixmap(img.px.scaled(abs(new_diag.x()), abs(new_diag.y()), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
                img.shadow.move(*(img.new_tl(c, new_diag)).toTuple())
                img.shadow.adjustSize()

    def mousePressEvent(self, event):
        if self.state == 'hovering':
            self.state = 'resizing'
            self.state.target_wid.init_resized_shadow()

    def mouseReleaseEvent(self, event):
        if self.state == 'resizing':
            self.state = 'idle'
            self.img.shadow.setVisible(False)
            self.img.setPixmap(QPixmap(self.img.shadow.pixmap()))
            self.img.move(self.img.shadow.pos())
            self.adjustSize()
            self.img.setVisible(True)
        elif self.state == 'cancel_resizing':
            self.img.shadow.setVisible(False)
            self.img.setVisible(True)
            self.state = 'idle'

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape and self.state == 'resizing':
            self.state = 'cancel_resizing'
        else:
            super().keyPressEvent(event)


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
