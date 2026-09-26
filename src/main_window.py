import logging
from pathlib import Path
import sys
import subprocess
import tomllib

from PySide6.QtWidgets import QApplication, QWidget, QMainWindow, QPushButton, QLabel, QHBoxLayout, QVBoxLayout, QFileDialog
from PySide6.QtPdf import QPdfDocument
from PySide6.QtPdfWidgets import QPdfView
from PySide6.QtCore import Qt, QMargins, Signal

# from src.options import SwapButton, TexSelectButton
from src.config import cfg
from src.menu import Menu
from src.pdf_view import PdfView

logging.basicConfig(level=logging.DEBUG, filename='log', filemode='w')


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Beamer GUI')
        self.showMaximized()

        self.menu = Menu()
        self.pdf_view = PdfView()
        self.struc = QWidget()
        self.struc.setObjectName('struc')
        self.struc.setVisible(False)

        self.menu.open_tex_btn.tex_opened.connect(self.set_tex_path)
        self.menu.compile_btn.clicked.connect(self.compile_and_display)
        self.menu.compile_btn.clicked.connect(self.resize_struc)
        self.menu.swap_btn.clicked.connect(self.swap_pdf_struc)
        self.pdf_view.tex_path_changed.connect(self.on_tex_path_changed)

        if Path(cfg['last_tex'] ).is_file():
            self.pdf_view.tex_path = Path(cfg['last_tex'])
        else:
            self.pdf_view.tex_path = Path('')

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.menu)
        layout.addWidget(self.pdf_view)
        layout.addWidget(self.struc, alignment=Qt.AlignmentFlag.AlignCenter)
        self.setCentralWidget(container)

    def set_tex_path(self, path: str|Path):
        self.pdf_view.tex_path = Path(path)

    def on_tex_path_changed(self, path: str|Path):
        if Path(path).parts:
            self.menu.compile_btn.setText(f'Compile {Path(path).parts[-1]}')

    def compile_and_display(self):
        self.pdf_view.compile_tex()
        self.pdf_view.display()

    def swap_pdf_struc(self):
        if self.pdf_view.isVisible():
            self.pdf_view.setVisible(False)
            self.struc.setVisible(True)
        else:
            self.pdf_view.setVisible(True)
            self.struc.setVisible(False)

    def resize_struc(self):
        if self.pdf_view.doc.pageCount() > 0:
            w_doc, h_doc = self.pdf_view.doc.pagePointSize(0).width(), self.pdf_view.doc.pagePointSize(0).height()
            ratio = w_doc / h_doc
            w_view, h_view = self.pdf_view.width(), self.pdf_view.height()
            if h_view * ratio <= w_view:
                self.struc.setFixedSize(h_view * ratio, h_view)
            else:
                self.struc.setFixedSize(w_view, w_view / ratio)
