import logging
from pathlib import Path
import subprocess

from PySide6.QtWidgets import QApplication, QWidget, QMainWindow, QPushButton, QLabel, QHBoxLayout, QVBoxLayout, QFileDialog
from PySide6.QtPdf import QPdfDocument
from PySide6.QtPdfWidgets import QPdfView
from PySide6.QtCore import Qt, QMargins, Signal

from src.config import cfg

logging.basicConfig(level=logging.DEBUG, filename='log', filemode='w')


class PdfView(QWidget):
    float_resource_dropped = Signal(float, float, float, Path)

    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)

        self.pdf_path = Path('')
        self.doc = QPdfDocument()

        self.view = QPdfView(pageMode=QPdfView.PageMode.SinglePage, zoomMode=QPdfView.ZoomMode.FitInView, documentMargins=QMargins())

        self.setLayout(QHBoxLayout())
        self.layout().addWidget(self.view)

    @property
    def doc_size(self) -> tuple[float, float]:
        return self.doc.pagePointSize(0).toTuple()

    def compile_tex(self, path: str|Path):
        if Path(path).is_file():
            proc = subprocess.Popen(['pdflatex', '-output-dir=tmp', str(path)]) # TODO: replace with a QProcess or something Qt
            proc.wait()
            proc = subprocess.Popen(['pdflatex', '-output-dir=tmp', str(path)]) # TODO: replace with a QProcess or something Qt
            proc.wait()
            self.pdf_path = Path('tmp')/ Path(path).with_suffix('.pdf').name
            logging.info(f'pdflatex returned {proc.returncode}')
        else:
            ... # TODO raise error

    def display(self):
        self.doc.load(str(self.pdf_path))
        self.view.setDocument(self.doc)
