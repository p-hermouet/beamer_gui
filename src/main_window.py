import logging
from pathlib import Path
import sys
import subprocess
import tomllib

from PySide6.QtCore import Qt, QMargins, Signal
from PySide6.QtGui import QPixmap
from PySide6.QtPdf import QPdfDocument
from PySide6.QtPdfWidgets import QPdfView
from PySide6.QtWidgets import QApplication, QWidget, QMainWindow, QPushButton, QLabel, QHBoxLayout, QVBoxLayout, QFileDialog, QStackedLayout

from src.config import cfg
from src.menu import Menu
from src.pdf_view import PdfView
from src.resources import Resources, ResourceThumbnail
from src.strucs import MainStruc
from src.test import TestButton

logging.basicConfig(level=logging.DEBUG, filename='log', filemode='w')


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Beamer GUI')
        self.showMaximized()

        self._tex_path = Path('')

        self.test_btn = TestButton()
        self.menu = Menu()
        self.resources = Resources()
        self.stack = QWidget()
        self.pdf_view = PdfView()
        self.struc = MainStruc()

        self.menu.open_tex_action.triggered.connect(self.set_tex_path)
        self.menu.compile_action.triggered.connect(self.compile_and_display)
        self.menu.compile_action.triggered.connect(self.resize_struc)
        self.menu.swap_action.triggered.connect(self.swap_pdf_struc)
        self.resources.resource_list.double_clicked.connect(self.add_resource_to_pdf)

        if Path(cfg['last_tex']).is_file():
            self.tex_path = Path(cfg['last_tex'])
        else:
            self.tex_path = Path('')

        container = QWidget()
        self.addToolBar(self.menu)
        container.setLayout(QHBoxLayout())
        container.layout().addWidget(self.resources, stretch=10)
        container.layout().addWidget(self.stack, stretch=40)
        stack_layout = QStackedLayout(self.stack)
        stack_layout.addWidget(self.pdf_view)
        stack_layout.addWidget(self.struc)
        self.setCentralWidget(container)

    @property
    def tex_path(self):
        return self._tex_path

    @tex_path.setter
    def tex_path(self, path: str|Path):
        self._tex_path = path
        if Path(path).parts:
            self.menu.compile_action.setText(f'Compile {Path(path).parts[-1]}')

    def set_tex_path(self, path: str|Path):
        self.tex_path = path

    def compile_and_display(self):
        self.pdf_view.compile_tex(self.tex_path)
        self.pdf_view.display()

    def swap_pdf_struc(self):
        if self.stack.layout().currentIndex() == 0:
            self.stack.layout().setCurrentIndex(1)
        else:
            self.stack.layout().setCurrentIndex(0)

    def resize_struc(self):
        if self.pdf_view.doc.pageCount() > 0:
            w_doc, h_doc = self.pdf_view.doc_size
            ratio = w_doc / h_doc
            w_view, h_view = self.pdf_view.view.width(), self.pdf_view.view.height()
            if h_view * ratio <= w_view:
                self.struc.struc.setFixedSize(h_view * ratio, h_view)
            else:
                self.struc.struc.setFixedSize(w_view, w_view / ratio)

    def add_resource_to_pdf(self, path: str|Path):
        if (doc := self.pdf_view.view.document()) and doc.status() == QPdfDocument.Status.Ready:
            im = QLabel(self)
            w, h = self.pdf_view.size().width(), self.pdf_view.size().height()
            pixmap = QPixmap(path).scaled(w/10, h/10, Qt.AspectRatioMode.KeepAspectRatio)
            im.setPixmap(pixmap)
            im.setGeometry(1000, 200, pixmap.width(), pixmap.height())
            im.show()

