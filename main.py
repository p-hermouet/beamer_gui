import logging
from pathlib import Path
import sys
import subprocess
import tomllib

from PySide6.QtWidgets import QApplication, QWidget, QMainWindow, QPushButton, QLabel, QHBoxLayout, QVBoxLayout, QFileDialog
from PySide6.QtPdf import QPdfDocument
from PySide6.QtPdfWidgets import QPdfView
from PySide6.QtCore import Qt, QMargins, Signal

from src.main_window import MainWindow

logging.basicConfig(level=logging.DEBUG, filename='log', filemode='w')


def main():
    app = QApplication(sys.argv)
    app.setStyleSheet('QWidget#struc {border: 2px solid black;}')
    window = MainWindow()
    window.show()
    app.exec()


if __name__ == "__main__":
    main()
