import sys

from PySide6.QtWidgets import QApplication, QWidget, QMainWindow, QPushButton, QLabel, QHBoxLayout
from PySide6.QtPdf import QPdfDocument
from PySide6.QtPdfWidgets import QPdfView
from PySide6.QtCore import Qt


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Beamer GUI')
        self.showMaximized()

        pdf_path = 'tex/main.pdf'
        self.pdf_doc = QPdfDocument(self)
        self.pdf_doc.load(pdf_path)
        self.pdf_view = QPdfView(self, document=self.pdf_doc, pageMode=QPdfView.PageMode.SinglePage, zoomMode=QPdfView.ZoomMode.FitToWidth)

        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.pdf_view)
        self.setCentralWidget(container)

    def update_pdf_size(self):
        if hasattr(self, 'pdf_view') and self.pdf_doc.pageCount() > 0:
            page = self.pdf_doc.pagePointSize(0)
            w = .7 * self.width()
            print(page.height(), page.width())
            h = page.height() / page.width() * w
            self.pdf_view.setFixedSize(w, h)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_pdf_size()


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()


if __name__ == "__main__":
    main()
