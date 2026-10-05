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

from src.drawing_area import DrawingArea

logging.basicConfig(level=logging.DEBUG, filename='log', filemode='w')


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setGeometry(0, 0, 800, 600)
        self.ss = '* {border: 2px solid red;}'
        self.ss_on = True
        self.setStyleSheet('')

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
        self.area = DrawingArea()
        self.area.add_rdw('static/pp.png', (200, 200), (200, 100))
        self.area.add_rdw('static/snow.jpg', (200, 200), (500, 200))
        self.central_wid.layout().addWidget(self.area, stretch=1)
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
    window.show()
    app.exec()
