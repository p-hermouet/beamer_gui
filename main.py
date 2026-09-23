import logging
from pathlib import Path
import sys
import subprocess

from PySide6.QtWidgets import QApplication, QWidget, QMainWindow, QPushButton, QLabel, QHBoxLayout, QVBoxLayout, QFileDialog
from PySide6.QtPdf import QPdfDocument
from PySide6.QtPdfWidgets import QPdfView
from PySide6.QtCore import Qt, QMargins

logging.basicConfig(level=logging.DEBUG, filename='log', filemode='w')


class TestButton(QPushButton):
    def __init__(self):
        super().__init__('Test')
        self.clicked.connect(self.on_clicked)

    def on_clicked(self):
        if (view := self.window().texpdf.view).isVisible():
            view.setVisible(False)
            self.window().pdf_view2.setVisible(True)
        else:
            view.setVisible(True)
            self.window().pdf_view2.setVisible(False)


class TexSelectButton(QPushButton):
    def __init__(self):
        super().__init__('Open tex')
        self.clicked.connect(self.on_clicked)

    def on_clicked(self):
        path, _ = QFileDialog.getOpenFileName(self, caption='Open tex file', filter='Tex files (*.tex)')
        self.window().texpdf.tex_path = Path(path)


class TexCompileButton(QPushButton):
    def __init__(self):
        super().__init__('Compile')


class TexPdfButton(QPushButton):
    def __init__(self):
        super().__init__('Compile')
        self.tex_path = Path('')
        self.pdf_path = Path('')
        self.doc = QPdfDocument(self)
        self.view = QPdfView(self, pageMode=QPdfView.PageMode.SinglePage, zoomMode=QPdfView.ZoomMode.FitInView, documentMargins=QMargins())
        self.clicked.connect(self.on_clicked)

    def on_clicked(self):
        if self.tex_path.is_file():
            proc = subprocess.Popen(['pdflatex', '-output-dir=tmp', str(self.tex_path)])
            proc.wait() # TODO find some way to make it asynchronous
            logging.info(f'pdflatex returned {proc.returncode}')
            self.pdf_path = Path(f'tmp/{self.tex_path.stem}.pdf')
            self.doc.load(str(self.pdf_path))
            self.view.setDocument(self.doc)

        else:
            ... # TODO raise some error



class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Beamer GUI')
        self.showMaximized()

        self.texpdf = TexPdfButton()
        self.test_btn = TestButton()

        pdf_path2 = 'tex/main2.pdf'
        self.pdf_doc2 = QPdfDocument(self)
        self.pdf_doc2.load(pdf_path2)
        self.pdf_view2 = QPdfView(self, document=self.pdf_doc2, pageMode=QPdfView.PageMode.SinglePage, zoomMode=QPdfView.ZoomMode.FitInView)
        self.pdf_view2.setDocumentMargins(QMargins())
        self.pdf_view2.setVisible(False)

        self.tex_select = TexSelectButton()

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.texpdf.view)
        layout.addWidget(self.pdf_view2)
        layout.addWidget(self.tex_select)
        layout.addWidget(self.texpdf)
        layout.addWidget(self.test_btn)
        self.setCentralWidget(container)

    def update_pdf_size(self):
        if hasattr(self, 'pdf_view') and self.pdf_doc.pageCount() > 0:
            page = self.pdf_doc.pagePointSize(0)
            w = .7 * self.width()
            print(page.height(), page.width())
            h = page.height() / page.width() * w
            self.pdf_view.setFixedSize(w, h)


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()


if __name__ == "__main__":
    main()
