from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto, unique
import logging
from pathlib import Path
import sys
import subprocess
import tomllib
from typing import Any, Literal, Self

from PySide6.QtCore import Qt, QMargins, Signal, QMimeData, QPoint, QRect, QEvent, QRectF
from PySide6.QtGui import QAction, QPixmap, QDrag, QPainter, QBrush, QColor, QPen, QVector2D, QCursor
from PySide6.QtPdf import QPdfDocument
from PySide6.QtPdfWidgets import QPdfView
from PySide6.QtWidgets import QApplication, QWidget, QMainWindow, QPushButton, QLabel, QHBoxLayout, QVBoxLayout, QFileDialog, QMenu, QStatusBar, QToolBar, QStackedLayout, QScrollArea, QSizePolicy, QFrame

from src.config import cfg
from src.drawing_area import DrawingArea
from src.pdf_model import PdfModel, RDWModel
from src.pdf_view import PdfView
from src.resources import Resources
from src.rdw import ResizableDragableWidget, Mask
from src.strucs import MainStruc

logging.basicConfig(level=logging.DEBUG, filename='log', filemode='w')


class Menu(QToolBar):
    tex_opened = Signal(str)

    def __init__(self):
        super().__init__()
        self.open_tex_action = QAction('Open tex')
        self.compile_action = QAction('Compile')
        self.swap_action = QAction('Swap')

        self.open_tex_action.triggered.connect(self.on_open_tex_triggered)

        self.addActions([self.open_tex_action, self.compile_action, self.swap_action])

        # For testing purpose only
        from src.test import on_resource_fill_pressed
        self.test_resource_action = QAction('Fill Resources')
        self.test_resource_action.triggered.connect(on_resource_fill_pressed)
        self.addAction(self.test_resource_action)
        info_action = QAction('Info', self)
        info_action.triggered.connect(self.info_triggered)
        self.addAction(info_action)
        load_pdf_action = QAction('load_pdf', self)
        load_pdf_action.triggered.connect(self.load_pdf_triggered)
        self.addAction(load_pdf_action)

    def on_open_tex_triggered(self):
        path, _ = QFileDialog.getOpenFileName(self, caption='Open tex file', filter='Tex files (*.tex)')
        self.tex_opened.emit(path)

    def info_triggered(self):
        print(self.parent().struc.size())
        self.parent().struc.setStyleSheet('* {background-color: pink;}')
        import ipdb; ipdb.set_trace()

    def load_pdf_triggered(self):
        window = self.parent()
        window.pdf_view.pdf_path = Path('tmp/main.pdf')
        window.pdf_view.display()
        window.draw_area.clear()
        model = PdfModel.parse(window.tex_path)
        ratio = window.pdf_view.doc_size[0] / window.pdf_view.view.size().width()
        rdws = [ResizableDragableWidget.from_model(window.draw_area, m_rdw, ratio) for m_rdw in model.rdws]
        for rdw in rdws:
            rdw.hidding_mask.stackUnder(rdws[0])
            window.draw_area.add_rdw(rdw)
        window.struc.fit_pdf(window.pdf_view.view_size)
