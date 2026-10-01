import logging
from pathlib import Path
import sys
import subprocess
import tomllib

from PySide6.QtCore import Qt, QMargins, Signal, QMimeData, QPoint, QRect
from PySide6.QtGui import QAction, QPixmap, QDrag, QPainter, QBrush, QColor, QPen
from PySide6.QtPdf import QPdfDocument
from PySide6.QtPdfWidgets import QPdfView
from PySide6.QtWidgets import QApplication, QWidget, QMainWindow, QPushButton, QLabel, QHBoxLayout, QVBoxLayout, QFileDialog, QMenu, QStatusBar, QToolBar, QStackedLayout, QScrollArea

logging.basicConfig(level=logging.DEBUG, filename='log', filemode='w')

FREE_STATE = 1
BUILDING_SQUARE = 2
BEGIN_SIDE_EDIT = 3
END_SIDE_EDIT = 4

CURSOR_ON_BEGIN_SIDE = 1
CURSOR_ON_END_SIDE = 2


class BlueDot(QLabel):
    def __init__(self, parent, pos: QPoint):
        super().__init__(parent)
        self.setStyleSheet('QLabel {background-color: blue;}')
        self.setGeometry(*pos.toTuple(), 20, 20)
        self.show()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.central_wid = CentralWidget()
        self.setCentralWidget(self.central_wid)


class CentralWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.img = ResizableImgFrame(self)


class ResizableImgFrame(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.setStyleSheet('QWidget {border: 2px solid black;}')
        self.setLayout(QHBoxLayout(alignment=Qt.AlignmentFlag.AlignCenter))
        self.layout().setSpacing(10)
        self.img = ResizableImg()
        self.layout().addWidget(self.img)
        self.setMouseTracking(True)
        self.move(700, 500)
        self.show()

    def cursor_on_side(self, pos):
        """Return which side the cursor is near, or 0 if not near either."""
        print(pos)
        y1, y2 = sorted([self.tl.y(), self.br.y()])
        if y1 <= pos.y() <= y2:
            if abs(self.tl.x() - pos.x()) <= 5:
                return CURSOR_ON_BEGIN_SIDE
            elif abs(self.br.x() - pos.x()) <= 5:
                return CURSOR_ON_END_SIDE
        return 0

    def resizeEvent(self, event):
        self.tl = self.pos()
        self.br = QPoint(self.x() + self.width(), self.y() + self.height())
        print(self.tl, self.br)
        BlueDot(self.window(), self.tl)
        BlueDot(self.window(), QPoint(self.br.x() - 20, self.br.y() - 20))


class ResizableImg(QLabel):
    def __init__(self):
        super().__init__()
        self.setStyleSheet('QLabel {border: 2px solid red;}')

        self.original_pixmap = QPixmap('static/snow.jpg')
        self.hover_side = 0
        self.state = FREE_STATE

        self.setPixmap(self.original_pixmap.scaled(200, 200, Qt.AspectRatioMode.KeepAspectRatio))
        self.tl = self.pos()
        self.br = QPoint(self.x() + self.width(), self.y() + self.height())


if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.showMaximized()
    app.exec()



class MyWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setGeometry(0, 0, 1600, 1200)
        self.img = QLabel(self)
        self.pixmap = QPixmap('static/lwe.png')
        self.img.setStyleSheet('QLabel {border: 2px solid red;}')
        self.img.setPixmap(self.pixmap.scaled(200, 200, Qt.AspectRatioMode.KeepAspectRatio))
        self.img.move(700, 500)
        self.img.show()
        self.begin = self.img.pos()
        self.end = QPoint(self.img.x() + self.img.width(), self.img.y() + self.img.height())
        self.state = FREE_STATE

        self.setMouseTracking(True)
        self.hover_side = 0

    def cursor_on_side(self, pos):
        """Return which side the cursor is near, or 0 if not near either."""
        y1, y2 = sorted([self.begin.y(), self.end.y()])
        if y1 <= pos.y() <= y2:
            if abs(self.begin.x() - pos.x()) <= 5:
                return CURSOR_ON_BEGIN_SIDE
            elif abs(self.end.x() - pos.x()) <= 5:
                return CURSOR_ON_END_SIDE
        return 0

    def mousePressEvent(self, event):
        side = self.cursor_on_side(event.position().toPoint())
        if side == CURSOR_ON_BEGIN_SIDE:
            self.state = BEGIN_SIDE_EDIT
        elif side == CURSOR_ON_END_SIDE:
            self.state = END_SIDE_EDIT

    def mouseMoveEvent(self, event):
        if self.state == FREE_STATE:
            self.hover_side = self.cursor_on_side(event.position().toPoint())
            if self.hover_side:
                self.setCursor(Qt.CursorShape.SizeHorCursor)
            else:
                self.unsetCursor()
        else:
            ...
            # self.apply_event(event)

    def mouseReleaseEvent(self, event):
        self.apply_event(event)
        self.state = FREE_STATE

    def apply_event(self, event):
        if self.state == BEGIN_SIDE_EDIT:
            if self.img.pixmap().height():
                ratio = self.pixmap.width() / self.pixmap.height()
                new_width = self.img.pixmap().width() + (self.begin.x() - event.position().x())
                self.img.setPixmap(self.pixmap.scaled(new_width, new_width / ratio))
                self.img.resize(self.img.pixmap().size())
                self.img.move(event.position().x(), self.begin.y() + (event.position().x() - self.begin.x()) / ratio)
                self.begin = self.img.pos()
                self.end = QPoint(self.img.x() + self.img.width(), self.img.y() + self.img.height())
        elif self.state == END_SIDE_EDIT:
            self.end.setX(event.x())


# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     window = MyWidget()
#     window.show()
#     sys.exit(app.exec())