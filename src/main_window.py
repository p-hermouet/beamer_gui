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
from src.drawing_area import DrawingArea
from src.menu import Menu
from src.pdf_view import PdfView
from src.resources import Resources, ResourceThumbnail, FloatingResource
from src.rdw import ResizableDragableWidget
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
        self.pdf_stack = QWidget()
        self.draw_area = DrawingArea()
        self.pdf_view = PdfView()
        self.struc = MainStruc()

        self.menu.open_tex_action.triggered.connect(self.set_tex_path)
        self.menu.compile_action.triggered.connect(self.compile_and_display)
        self.menu.swap_action.triggered.connect(self.swap_pdf_struc)
        self.resources.resource_list.double_clicked.connect(self.add_resource_to_pdf)
        self.pdf_view.float_resource_dropped.connect(self.add_image_to_tex) # to remove: not used any longer
        self.draw_area.rdw_modified.connect(self.add_image_to_tex)

        if Path(cfg['last_tex']).is_file():
            self.tex_path = Path(cfg['last_tex'])
        else:
            self.tex_path = Path('')

        container = QWidget()
        self.addToolBar(self.menu)
        container.setLayout(QHBoxLayout())
        container.layout().addWidget(self.resources, stretch=1)
        container.layout().addWidget(self.stack, stretch=4)
        stack_layout = QStackedLayout(self.stack)
        self.pdf_stack.setLayout(QStackedLayout())
        self.pdf_stack.layout().setStackingMode(QStackedLayout.StackingMode.StackAll)
        self.pdf_stack.layout().addWidget(self.draw_area)
        self.pdf_stack.layout().addWidget(self.pdf_view)
        stack_layout.addWidget(self.pdf_stack)
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

    def add_resource_to_pdf(self, path: str|Path):
        if (doc := self.pdf_view.view.document()) and doc.status() == QPdfDocument.Status.Ready:
            # FloatingResource(path, self.pdf_view.view)
            self.draw_area.add_rdw(path, (200, 200), (200, 200))

    # def add_image_to_tex(self, x: float, y: float, width: float, path: str|Path):
    #     # TODO: change this function: temporary one
    #     tex_lines = self.tex_path.read_text().splitlines()
    #     idx = next(i for i, l in enumerate(tex_lines) if r'\end{frame}' in l) # TODO catch possible error
    #     tikz_code = '\n'.join([
    #         rf'\begin{{tikzpicture}}[remember picture, overlay]',
    #         rf'  \node[anchor=north west] at ([xshift={x}, yshift=-{y}] current page.north west) {{\includegraphics[width={width}px]{{{path}}}}};',
    #         rf'\end{{tikzpicture}}'
    #     ])
    #     new_content = '\n'.join(tex_lines[:idx]) + '\n' + tikz_code + '\n' + '\n'.join(tex_lines[idx:]) # TODO: use insert
    #     self.tex_path.write_text(new_content)

    def add_image_to_tex(self, rdw: ResizableDragableWidget):
        # TODO: implement this function
        ...
