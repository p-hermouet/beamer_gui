import logging
from pathlib import Path
import sys
import subprocess
import tomllib

from PySide6.QtWidgets import QApplication, QWidget, QMainWindow, QPushButton, QLabel, QHBoxLayout, QVBoxLayout, QFileDialog
from PySide6.QtPdf import QPdfDocument
from PySide6.QtPdfWidgets import QPdfView
from PySide6.QtCore import Qt, QMargins, Signal

from src.options import SwapButton, TexSelectButton

logging.basicConfig(level=logging.DEBUG, filename='log', filemode='w')



class TexPdfButton(QPushButton):
    tex_path_changed = Signal(object)

    def __init__(self):
        super().__init__('Compile')
        self._tex_path = Path('')
        self.pdf_path = Path('')
        self.doc = QPdfDocument(self)
        self.view = QPdfView(self, pageMode=QPdfView.PageMode.SinglePage, zoomMode=QPdfView.ZoomMode.FitInView, documentMargins=QMargins())

        self.clicked.connect(self.on_clicked)
        self.tex_path_changed.connect(self.on_tex_path_changed)

        if (last_tex := tomllib.loads(Path('config.toml').read_text())['last_tex']) and Path(last_tex).is_file():
            self.tex_path = Path(last_tex)
        else:
            self.tex_path = Path('')

    @property
    def tex_path(self):
        return self._tex_path

    @tex_path.setter
    def tex_path(self, value: str|Path):
        self._tex_path = value
        self.tex_path_changed.emit(value)

    def on_clicked(self):
        if self.tex_path.is_file():
            proc = subprocess.Popen(['pdflatex', '-output-dir=tmp', str(self.tex_path)])
            proc.wait()
            logging.info(f'pdflatex returned {proc.returncode}')
            self.pdf_path = Path(f'tmp/{self.tex_path.stem}.pdf')
            self.doc.load(str(self.pdf_path))
            self.view.setDocument(self.doc)
            self.window().resize_struc()

        else:
            ... # TODO raise some error

    def on_tex_path_changed(self, value: str|Path):
        if Path(value).parts:
            self.setText(f'Compile {Path(value).parts[-1]}')



class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Beamer GUI')
        self.showMaximized()

        self.texpdf = TexPdfButton()
        self.test_btn = SwapButton()

        self.struc = QWidget()
        self.struc.setObjectName('struc')
        self.struc.setVisible(False)

        self.tex_select = TexSelectButton()

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.texpdf.view)
        layout.addWidget(self.struc, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.tex_select)
        layout.addWidget(self.texpdf)
        layout.addWidget(self.test_btn)
        self.setCentralWidget(container)

    def resize_struc(self):
        if self.texpdf.doc.pageCount() > 0:
            w_doc, h_doc = self.texpdf.doc.pagePointSize(0).width(), self.texpdf.doc.pagePointSize(0).height()
            ratio = w_doc / h_doc
            w_view, h_view = self.texpdf.view.width(), self.texpdf.view.height()
            if h_view * ratio <= w_view:
                self.struc.setFixedSize(h_view * ratio, h_view)
            else:
                self.struc.setFixedSize(w_view, w_view / ratio)


def main():
    app = QApplication(sys.argv)
    app.setStyleSheet('QWidget#struc {border: 2px solid black;}')
    window = MainWindow()
    window.show()
    app.exec()


if __name__ == "__main__":
    main()
