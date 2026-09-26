import logging
from pathlib import Path
import subprocess

from PySide6.QtWidgets import QApplication, QWidget, QMainWindow, QPushButton, QLabel, QHBoxLayout, QVBoxLayout, QFileDialog
from PySide6.QtPdf import QPdfDocument
from PySide6.QtPdfWidgets import QPdfView
from PySide6.QtCore import Qt, QMargins, Signal

from src.config import cfg

logging.basicConfig(level=logging.DEBUG, filename='log', filemode='w')


class Menu(QWidget):
    def __init__(self):
        super().__init__()
        self.open_tex_btn = OpenTexButton()
        self.compile_btn = CompileButton()
        self.swap_btn = SwapButton()

        self.setLayout(QVBoxLayout())
        self.layout().addWidget(self.open_tex_btn)
        self.layout().addWidget(self.compile_btn)
        self.layout().addWidget(self.swap_btn)


class OpenTexButton(QPushButton):
    tex_opened = Signal(str)

    def __init__(self):
        super().__init__('Open tex')

        self.clicked.connect(self.on_clicked)

    def on_clicked(self):
        path, _ = QFileDialog.getOpenFileName(self, caption='Open tex file', filter='Tex files (*.tex)')
        self.tex_opened.emit(path)


class CompileButton(QPushButton):
    # tex_path_changed = Signal(object)

    def __init__(self):
        super().__init__('Compile')
        # self._tex_path = Path('')
        # self.pdf_path = Path('')
        # self.doc = QPdfDocument(self)
        # self.view = QPdfView(self, pageMode=QPdfView.PageMode.SinglePage, zoomMode=QPdfView.ZoomMode.FitInView, documentMargins=QMargins())

        # self.tex_path_changed.connect(self.on_tex_path_changed)

        # if (last_tex := tomllib.loads(Path('config.toml').read_text())['last_tex']) and Path(last_tex).is_file():
        #     self.tex_path = Path(last_tex)
        # else:
        #     self.tex_path = Path('')

    # @property
    # def tex_path(self):
    #     return self._tex_path

    # @tex_path.setter
    # def tex_path(self, value: str|Path):
    #     self._tex_path = value
    #     self.tex_path_changed.emit(value)

        # else:
        #     ... # TODO raise some error

    # def on_tex_path_changed(self, value: str|Path):
    #     if Path(value).parts:
    #         self.setText(f'Compile {Path(value).parts[-1]}')


class SwapButton(QPushButton):
    def __init__(self):
        super().__init__('Swap')
