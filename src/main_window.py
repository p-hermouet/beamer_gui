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
from src.models import Block, FrameParser, RDWModel
from src.pdf_view import PdfView
from src.resources import Resources
from src.rdw import ResizableDragableWidget, Mask
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

        self.menu.tex_opened.connect(self.set_tex_path)
        self.menu.compile_action.triggered.connect(self.compile_and_display)
        self.menu.swap_action.triggered.connect(self.swap_pdf_struc)
        self.resources.resource_list.content.double_clicked.connect(self.add_resource_to_pdf)
        self.draw_area.rdw_modified.connect(self.add_image_to_tex)
        self.draw_area.remove_rdw.connect(self.rm_rdw)

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
        self.draw_area.clear()
        parser = FrameParser(self.tex_path)
        ratio = self.pdf_view.doc_size[0] / self.pdf_view.view.size().width()
        rdws = [ResizableDragableWidget.from_block(self.draw_area, b, ratio)
                for b in parser.blocks if b.pid == RDWModel.pid]
        for rdw in rdws:
            rdw.hidding_mask.stackUnder(rdws[0])
            self.draw_area.add_rdw(rdw)
        self.struc.fit_pdf(self.pdf_view.view_size)

    def swap_pdf_struc(self):
        if self.stack.layout().currentIndex() == 0:
            self.stack.layout().setCurrentIndex(1)
        else:
            self.stack.layout().setCurrentIndex(0)

    def add_resource_to_pdf(self, path: str|Path):
        if (doc := self.pdf_view.view.document()) and doc.status() == QPdfDocument.Status.Ready:
            self.draw_area.add_rdw(ResizableDragableWidget(self.draw_area, path, (200, 200), (200, 200)))
            # TODO: (200, 200), (200, 200) seems hardcoded, make it depend on the pdfdoc size

    def add_image_to_tex(self, rdw: ResizableDragableWidget):
        # TODO: change this function: temporary one; i think parts of it must be in PdfModel
        parser = FrameParser(self.tex_path)
        ratio = self.pdf_view.doc_size[0] / self.pdf_view.view.size().width()
        content = self.tex_path.read_text()
        if rdw.block:
            block = parser.find_block_from_id(rdw.block.id)
            if not block:
                return # enters here if texfile has been modified, maybe raise some error instead
            new_block = Block.tex(block.id, rdw.to_model(ratio).to_tex())
            new_content = content[:block.start] + new_block + content[block.end:]
            self.tex_path.write_text(new_content)
        else:
            id = parser.new_id(RDWModel)
            new_block = Block.tex(id, rdw.to_model(ratio).to_tex())
            new_content = content[:parser.end] + new_block + '\n\n' + content[parser.end:]
            self.tex_path.write_text(new_content)
            parser = FrameParser(self.tex_path)
            rdw.block = parser.find_block_from_id(id)

    def rm_rdw(self, rdw: ResizableDragableWidget):
        parser = FrameParser(self.tex_path)
        block = parser.find_block_from_id(rdw.block.id)
        content = self.tex_path.read_text()
        new_content = content[:block.start] + content[block.end:]
        self.tex_path.write_text(new_content)
