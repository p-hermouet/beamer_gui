import logging
from pathlib import Path
import sys
import subprocess
import tomllib

from PySide6.QtCore import Qt, QMargins, Signal, QPointF, QPoint, QRectF
from PySide6.QtGui import QPixmap, QColor
from PySide6.QtWidgets import QApplication, QWidget, QMainWindow, QPushButton, QLabel, QHBoxLayout, QVBoxLayout, QFileDialog, QStackedLayout, QScrollArea, QGraphicsDropShadowEffect, QGraphicsEffect

from src.config import cfg

logging.basicConfig(level=logging.DEBUG, filename='log', filemode='w')


# Source - https://stackoverflow.com/a/59970347
# Posted by eyllanesc, modified by community. See post 'Timeline' for change history
# Retrieved 2026-09-29, License - CC BY-SA 4.0


class GraphicsBorderEffect(QGraphicsEffect):
    def __init__(self, parent=None, offset=1.5):
        super().__init__()
        self.color = QColor(237, 231, 66)
        self.offset = offset * QPointF(1, 1)

    def boundingRectFor(self, sourceRect):
        return sourceRect.adjusted(-self.offset.x(), -self.offset.y(), self.offset.x(), self.offset.y())

    def draw(self, painter):
        offset = QPoint()
        try:
            pixmap = self.sourcePixmap(Qt.LogicalCoordinates, offset)
        except TypeError:
            pixmap, offset = self.sourcePixmap(Qt.LogicalCoordinates)

        bound = self.boundingRectFor(QRectF(pixmap.rect()))
        painter.save()
        painter.setPen(Qt.NoPen)
        painter.setBrush(self.color)
        p = QPointF(offset.x() - self.offset.x(), offset.y() - self.offset.y())
        bound.moveTopLeft(p)
        painter.drawRoundedRect(bound, 5, 5, Qt.RelativeSize)
        painter.drawPixmap(offset, pixmap)
        painter.restore()


# if __name__ == "__main__":
#     app = QtWidgets.QApplication(sys.argv)
#     w = QtWidgets.QWidget()
#     lay = QtWidgets.QVBoxLayout(w)
#     for _ in range(3):
#         o = QtWidgets.QLabel()
#         o.setStyleSheet(
#             """background-color : {}""".format(
#                 QtGui.QColor(*random.sample(range(255), 3)).name()
#             )
#         )
#         effect = HighlightEffect(parent=o)
#         o.setGraphicsEffect(effect)
#         lay.addWidget(o)
#     w.show()
#     w.resize(640, 480)
#     sys.exit(app.exec_())
