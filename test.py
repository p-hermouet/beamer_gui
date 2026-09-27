import logging
from pathlib import Path
import sys
import subprocess
import tomllib

from PySide6.QtWidgets import QApplication, QWidget, QMainWindow, QPushButton, QLabel, QHBoxLayout, QVBoxLayout, QFileDialog, QMenu, QStatusBar, QToolBar, QStackedLayout
from PySide6.QtPdf import QPdfDocument
from PySide6.QtGui import QAction
from PySide6.QtPdfWidgets import QPdfView
from PySide6.QtCore import Qt, QMargins, Signal

from src.config import cfg
from src.menu import Menu
from src.pdf_view import PdfView
from src.test import TestButton
from src.strucs import MainStruc

logging.basicConfig(level=logging.DEBUG, filename='log', filemode='w')


class TestCentralWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setLayout(QStackedLayout())

        self.pdf_view = QPdfView(zoomMode=QPdfView.ZoomMode.FitInView, documentMargins=QMargins(0, 0, 0, 0))
        doc = QPdfDocument(self)
        doc.load('tmp/main.pdf')
        self.pdf_view.setDocument(doc)

        self.struc_page = QWidget()
        self.struc_page.setLayout(QHBoxLayout())
        self.struc = QWidget()
        self.struc.setStyleSheet('* {border: 2px solid black;}')
        self.struc_page.layout().addWidget(self.struc, alignment=Qt.AlignmentFlag.AlignCenter)

        self.layout().addWidget(self.pdf_view)
        self.layout().addWidget(self.struc_page)


class TestMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.showMaximized()

        toolbar = QToolBar()
        self.addToolBar(toolbar)
        action = QAction('swap', self)
        action.triggered.connect(self.swap)
        action2 = QAction('resize', self)
        action2.triggered.connect(self.resize_struc)
        toolbar.addAction(action)
        toolbar.addAction(action2)

        self.central = TestCentralWidget()
        self.setCentralWidget(self.central)

    def swap(self, e):
        self.central.layout().setAlignment(Qt.AlignmentFlag.AlignCenter)
        if self.central.layout().currentIndex() == 0:
            self.central.layout().setCurrentIndex(1)
        else:
            self.central.layout().setCurrentIndex(0)
        # if self.central.pdf_view.isVisible():
        #     self.central.pdf_view.setVisible(False)
        #     self.central.struc.setVisible(True)
        # else:
        #     self.central.pdf_view.setVisible(True)
        #     self.central.struc.setVisible(False)

    def resize_struc(self):
        if self.central.pdf_view.document().pageCount() > 0:
            w_doc, h_doc = self.central.pdf_view.document().pagePointSize(0).width(), self.central.pdf_view.document().pagePointSize(0).height()
            ratio = w_doc / h_doc
            w_view, h_view = self.central.pdf_view.width(), self.central.pdf_view.height()
            if h_view * ratio <= w_view:
                self.central.struc.setFixedSize(h_view * ratio, h_view)
            else:
                self.central.struc.setFixedSize(w_view, w_view / ratio)


if __name__ == "__main__":
    app = QApplication([])
    main_window = TestMainWindow()
    main_window.show()
    app.exec()
