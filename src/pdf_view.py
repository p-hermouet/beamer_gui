import logging
from pathlib import Path
import subprocess

from PySide6.QtWidgets import QApplication, QWidget, QMainWindow, QPushButton, QLabel, QHBoxLayout, QVBoxLayout, QFileDialog
from PySide6.QtPdf import QPdfDocument
from PySide6.QtPdfWidgets import QPdfView
from PySide6.QtCore import Qt, QMargins, Signal

from src.config import cfg

logging.basicConfig(level=logging.DEBUG, filename='log', filemode='w')


class PdfView(QPdfView):
    tex_path_changed = Signal(object)

    def __init__(self):
        super().__init__(pageMode=QPdfView.PageMode.SinglePage, zoomMode=QPdfView.ZoomMode.FitInView, documentMargins=QMargins())

        self._tex_path = Path('')
        self.pdf_path = Path('')
        self.doc = QPdfDocument(self)

    @property
    def tex_path(self):
        return self._tex_path

    @tex_path.setter
    def tex_path(self, value: str|Path):
        self._tex_path = value
        self.tex_path_changed.emit(value)

    def compile_tex(self):
        if self.tex_path.is_file():
            proc = subprocess.Popen(['pdflatex', '-output-dir=tmp', str(self.tex_path)])
            proc.wait()
            self.pdf_path = Path('tmp')/ self.tex_path.with_suffix('.pdf').name
            logging.info(f'pdflatex returned {proc.returncode}')
        else:
            ... # TODO raise error

    def display(self):
        self.doc.load(str(self.pdf_path))
        self.setDocument(self.doc)
