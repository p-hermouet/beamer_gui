from dataclasses import dataclass
from enum import Enum, auto, unique
import logging
from pathlib import Path
import sys
import subprocess
import tomllib
from typing import Any

from PySide6.QtCore import Qt, QMargins, Signal, QMimeData, QPoint, QRect
from PySide6.QtGui import QAction, QPixmap, QDrag, QPainter, QBrush, QColor, QPen, QVector2D
from PySide6.QtPdf import QPdfDocument
from PySide6.QtPdfWidgets import QPdfView
from PySide6.QtWidgets import QApplication, QWidget, QMainWindow, QPushButton, QLabel, QHBoxLayout, QVBoxLayout, QFileDialog, QMenu, QStatusBar, QToolBar, QStackedLayout, QScrollArea, QSizePolicy

logging.basicConfig(level=logging.DEBUG, filename='log', filemode='w')


@unique
class CursorState(Enum):
    IDLE = auto()
    HOVER_CORNER = auto()
    RESIZING = auto()

@dataclass
class State:
    cursor: CursorState
    target_wid: QLabel|None
    corner: QVector2D|None


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setGeometry(0, 0, 800, 600)
        self.central_wid = CentralWidget()
        self.setCentralWidget(self.central_wid)


class CentralWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.img = ResizableImg(self)
        self.setMouseTracking(True)
        self.state = State(CursorState.IDLE, None,   None)

    def mouseMoveEvent(self, ev):
        # change cursor shape and state
        if self.state.cursor == CursorState.IDLE or self.state.cursor == CursorState.HOVER_CORNER:
            if c := self.img.cursor_on_corner(ev.position()):
                self.state.cursor = CursorState.HOVER_CORNER
                self.state.corner = c
                self.state.target_wid = self.img
                if c in [self.img.tl, self.img.br]:
                    self.setCursor(Qt.CursorShape.SizeFDiagCursor)
                else:
                    self.setCursor(Qt.CursorShape.SizeBDiagCursor)
            else:
                self.state.cursor = CursorState.IDLE
                self.unsetCursor()
        # resize floating image's shadow
        elif self.state.cursor == CursorState.RESIZING:
            c = self.state.corner
            img = self.state.target_wid
            curs_vec = QVector2D(ev.position()) - c
            direc = QVector2D(img.ratio, 1).normalized()
            coef = QVector2D.dotProduct(curs_vec, direc)
            new_c = coef * direc + c
            print(c, new_c, img.opposed_corner(c))
            new_w = abs(new_c.x() - img.opposed_corner(c).x())
            new_h = abs(new_c.y() - img.opposed_corner(c).y())
            img.shadow.setPixmap(img.og_pixmap.scaled(new_w, new_h, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
            img.shadow.move(*(img.new_tl(c, new_c)).toTuple())
            img.shadow.adjustSize()

    def mousePressEvent(self, event):
        if self.state.cursor == CursorState.HOVER_CORNER:
            self.state.cursor = CursorState.RESIZING
            self.state.target_wid.init_resized_shadow()

    def mouseReleaseEvent(self, event):
        self.state.cursor = CursorState.IDLE
        self.img.shadow.setVisible(False)
        self.img.setPixmap(QPixmap(self.img.shadow.pixmap()))
        self.img.move(self.img.shadow.pos())
        self.adjustSize()
        self.img.setVisible(True)


class ResizableImg(QLabel):
    def __init__(self, parent):
        super().__init__(parent)
        self.setStyleSheet('QLabel {border: 1px solid red;}')

        self.og_pixmap = QPixmap('static/lwe.png')
        self.ratio = self.og_pixmap.width() / self.og_pixmap.height()

        self.shadow = QLabel(parent)
        self.shadow.setVisible(False)
        self.shadow.show()

        self.setPixmap(self.og_pixmap.scaled(200, 200, Qt.AspectRatioMode.KeepAspectRatio))

        self.move(300, 200)
        self.show()

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

    def new_tl(self, corner: QVector2D, new_c: QVector2D):
        match corner:
            case self.tl: return new_c
            case self.br: return self.tl
            case self.tr: return QVector2D(self.tl.x(), new_c.y())
            case self.bl: return QVector2D(new_c.x(), self.tl.y())

    def cursor_on_corner(self, pos) -> QVector2D:
        '''Return which corner the cursor is near, or None if not near either.'''
        for c in [self.tl, self.tr, self.bl, self.br]:
            if (pos.x() - c.x())**2 + (pos.y() - c.y())**2 <= 5**2: # 5 is the distance from the corner to drag
                return c

    def init_resized_shadow(self):
        self.shadow.setPixmap(QPixmap(self.pixmap()))
        self.shadow.setStyleSheet('QLabel {border: 1px solid green;}')
        self.shadow.move(self.pos())
        self.shadow.setVisible(True)
        self.shadow.adjustSize()
        self.setVisible(False)

if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.showMaximized()
    app.exec()
