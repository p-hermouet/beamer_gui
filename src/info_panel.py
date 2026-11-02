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


class InfoPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.focused_wid: QWidget = None
        self.setLayout(QVBoxLayout())

    def clear(self):
        for i in range(self.layout().count()):
            self.layout().itemAt(i).widget().deleteLater()

    def set_focused_wid(self, wid: QWidget):
        self.clear()
        self.focused_wid = wid
        match wid:
            case ResizableDragableWidget():
                self.layout().addWidget(QLabel(f'width: {wid.width()}'))
                self.layout().addWidget(QLabel(f'height: {wid.height()}'))
