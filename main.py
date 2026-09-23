import sys

from PySide6.QtWidgets import QApplication, QWidget, QMainWindow, QPushButton, QLabel, QHBoxLayout, QVBoxLayout, QFileDialog
from PySide6.QtPdf import QPdfDocument
from PySide6.QtPdfWidgets import QPdfView
from PySide6.QtCore import Qt, QMargins


class PdfSelectButton(QPushButton):
    def __init__(self):
        super().__init__('Load pdf')
        self.clicked.connect(self.on_clicked)

    def on_clicked(self):
        QFileDialog.getOpenFileName()



class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Beamer GUI')
        self.showMaximized()

        pdf_path = 'tex/main.pdf'
        self.pdf_doc = QPdfDocument(self)
        self.pdf_doc.load(pdf_path)
        self.pdf_view = QPdfView(self, document=self.pdf_doc, pageMode=QPdfView.PageMode.SinglePage, zoomMode=QPdfView.ZoomMode.FitInView)
        self.pdf_view.setDocumentMargins(QMargins())

        self.pdf_select = PdfSelectButton()

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.pdf_view)
        layout.addWidget(self.pdf_select)
        self.setCentralWidget(container)

    def update_pdf_size(self):
        if hasattr(self, 'pdf_view') and self.pdf_doc.pageCount() > 0:
            page = self.pdf_doc.pagePointSize(0)
            w = .7 * self.width()
            print(page.height(), page.width())
            h = page.height() / page.width() * w
            self.pdf_view.setFixedSize(w, h)

    # def resizeEvent(self, event):
    #     super().resizeEvent(event)
    #     self.update_pdf_size()


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()


if __name__ == "__main__":
    main()
