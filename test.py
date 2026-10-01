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


class MyWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setGeometry(0, 0, 1600, 1200)
        self.img = QLabel(self)
        self.pixmap = QPixmap('static/lwe.png')
        self.img.setStyleSheet('QLabel {border: 2px solid red;}')
        self.img.setPixmap(self.pixmap.scaled(200, 200, Qt.AspectRatioMode.KeepAspectRatio))
        self.img.move(1300, 950)
        self.img.show()
        self.begin = self.img.pos()
        self.end = QPoint(self.img.x() + self.img.width(), self.img.y() + self.img.height())
        self.state = FREE_STATE

        self.setMouseTracking(True)
        self.hover_side = 0

    def paintEvent(self, event):
        qp = QPainter(self)
        br = QBrush(QColor(100, 10, 10, 40))
        qp.setBrush(br)
        # qp.drawRect(QRect(self.begin, self.end))

        # Draw a dashed line on the hovered edge.
        if not self.hover_side:
            return

        qp.setPen(QPen(Qt.GlobalColor.black, 5, Qt.PenStyle.DashLine))
        if self.hover_side == CURSOR_ON_BEGIN_SIDE:
            edge_end = QPoint(self.begin.x(), self.end.y())
            qp.drawLine(self.begin, edge_end)
        elif self.hover_side == CURSOR_ON_END_SIDE:
            edge_start = QPoint(self.end.x(), self.begin.y())
            qp.drawLine(edge_start, self.end)

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

    def apply_event(self, event):
        if self.state == BEGIN_SIDE_EDIT:
            # self.begin.setX(event.x())
            if self.img.pixmap().height():
                ratio = self.pixmap.width() / self.pixmap.height()
                new_width = self.img.pixmap().width() + (self.begin.x() - event.position().x())
                self.img.setPixmap(self.pixmap.scaled(new_width, new_width / ratio))
                self.img.resize(self.img.pixmap().size())
                self.img.move(event.position().x(), self.begin.y() + (event.position().x() - self.begin.x()) / ratio)
        elif self.state == END_SIDE_EDIT:
            self.end.setX(event.x())

    def mouseMoveEvent(self, event):
        if self.state == FREE_STATE:
            # Update hover feedback.
            self.hover_side = self.cursor_on_side(event.position().toPoint())
            if self.hover_side:
                self.setCursor(Qt.CursorShape.SizeHorCursor)
            else:
                self.unsetCursor()
            self.update()
        else:
            self.apply_event(event)
            self.update()

    # def mouseReleaseEvent(self, event):
    #     self.apply_event(event)
    #     self.state = FREE_STATE


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyWidget()
    window.show()
    sys.exit(app.exec())