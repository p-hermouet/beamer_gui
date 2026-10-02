from enum import Enum, auto, unique
import logging
from pathlib import Path
import sys
import subprocess
import tomllib

from PySide6.QtCore import Qt, QMargins, Signal, QMimeData, QPoint, QRect
from PySide6.QtGui import QAction, QPixmap, QDrag, QPainter, QBrush, QColor, QPen, QVector2D
from PySide6.QtPdf import QPdfDocument
from PySide6.QtPdfWidgets import QPdfView
from PySide6.QtWidgets import QApplication, QWidget, QMainWindow, QPushButton, QLabel, QHBoxLayout, QVBoxLayout, QFileDialog, QMenu, QStatusBar, QToolBar, QStackedLayout, QScrollArea, QSizePolicy

logging.basicConfig(level=logging.DEBUG, filename='log', filemode='w')

FREE_STATE = 1
BUILDING_SQUARE = 2
BEGIN_SIDE_EDIT = 3
END_SIDE_EDIT = 4

DRAG_CORNER_DISTANCE = 5

@unique
class Corners(Enum):
    TL = auto()
    TR = auto()
    BL = auto()
    BR = auto()

@unique
class CursorState(Enum):
    IDLE = auto()
    HOVER_TL = auto()
    HOVER_TR = auto()
    HOVER_BL = auto()
    HOVER_BR = auto()
    RESIZING_TL = auto()
    RESIZING_TR = auto()
    RESIZING_BL = auto()
    RESIZING_BR = auto()

    @classmethod
    def resize_from_corner(cls, corner: Corners):
        match corner:
            case Corners.TL: return cls.RESIZING_TL
            case Corners.TR: return cls.RESIZING_TR
            case Corners.BL: return cls.RESIZING_BL
            case Corners.BR: return cls.RESIZING_BR

    @classmethod
    def hover_from_corner(cls, corner: Corners):
        match corner:
            case Corners.TL: return cls.HOVER_TL
            case Corners.TR: return cls.HOVER_TR
            case Corners.BL: return cls.HOVER_BL
            case Corners.BR: return cls.HOVER_BR

    @classmethod
    def hovers(cls):
        return [cls.HOVER_TL, cls.HOVER_TR, cls.HOVER_BL, cls.HOVER_BR]

class BlueDot(QLabel):
    def __init__(self, parent, pos: QPoint, color='blue'):
        super().__init__(parent)
        self.setStyleSheet(f'QLabel {{background-color: {color};}}')
        self.setGeometry(*pos.toTuple(), 5, 5)
        self.show()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setGeometry(0, 0, 800, 600)
        self.central_wid = CentralWidget()
        self.menu = QToolBar()
        action = QAction('test', parent=self)
        action.triggered.connect(self.central_wid.dots)
        self.menu.addAction(action)
        self.addToolBar(self.menu)
        self.setCentralWidget(self.central_wid)


class CentralWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.img = ResizableImg(self)
        self.setMouseTracking(True)

    def dots(self):
        BlueDot(self, self.img.shadow.pos(), 'green')
        print(self.img.shadow.size(), self.img.size())

    def mouseMoveEvent(self, ev):
        if self.img.state == CursorState.IDLE or self.img.state in CursorState.hovers():
            if C := self.img.cursor_on_corner(ev.position()):
                self.img.state = CursorState.hover_from_corner(C)
                if C in [Corners.TL, Corners.BR]:
                    self.setCursor(Qt.CursorShape.SizeFDiagCursor)
                else:
                    self.setCursor(Qt.CursorShape.SizeBDiagCursor)
            else:
                self.img.state = CursorState.IDLE
                self.unsetCursor()
        elif self.img.state == CursorState.RESIZING_TL:
            curs_vec = QVector2D(ev.position()) - self.img.tl
            direc = QVector2D(self.img.ratio, 1).normalized()
            coef = QVector2D.dotProduct(curs_vec, direc)
            new_tl = coef * direc + self.img.tl
            new_w = abs(new_tl.x() - self.img.tr.x()) + self.img.w
            new_h = abs(new_tl.y() - self.img.bl.y()) + self.img.h
            self.img.shadow.setGeometry(*new_tl.toTuple(), new_w, new_h)
            self.img.shadow.setPixmap(self.img.og_pixmap.scaled(new_w, new_h, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
            self.img.shadow.adjustSize()

    def mousePressEvent(self, event):
        match self.img.state:
            case CursorState.HOVER_TL:
                self.img.state = CursorState.RESIZING_TL
                self.img.init_resized_shadow()
            case _: return

    def mouseReleaseEvent(self, event):
        self.img.state = CursorState.IDLE


class ResizableImg(QLabel):
    def __init__(self, parent):
        super().__init__(parent)
        self.setStyleSheet('QLabel {border: 1px solid red;}')

        self.og_pixmap = QPixmap('static/lwe.png')
        self.w, self.h = self.width(), self.height()
        self.ratio = self.og_pixmap.width() / self.og_pixmap.height()
        self.hover_side = 0
        self.state = CursorState.IDLE
        self.shadow = QLabel(parent)
        self.shadow.show()
        self.shadow.setVisible(False)

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

    def cursor_on_corner(self, pos) -> Corners:
        '''Return which corner the cursor is near, or 0 if not near either.'''
        for c, C in [(self.tl, Corners.TL), (self.tr, Corners.TR), (self.bl, Corners.BL), (self.br, Corners.BR)]:
            if (pos.x() - c.x())**2 + (pos.y() - c.y())**2 <= DRAG_CORNER_DISTANCE**2:
                return C
        return

    def init_resized_shadow(self):
        self.shadow.setPixmap(QPixmap(self.pixmap()))
        self.shadow.setStyleSheet('QLabel {border: 1px solid red;}')
        self.shadow.move(self.pos())
        self.setVisible(False)

if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.showMaximized()
    app.exec()
