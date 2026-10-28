import argparse
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
from src.config import LOCAL_PATH, LOCAL_CFG, LOCAL_TEX

logging.basicConfig(level=logging.DEBUG, filename='log', filemode='w')


def init_dir(path: str|Path):
    if not LOCAL_PATH.exists(): LOCAL_PATH.mkdir()
    if not LOCAL_CFG.exists(): LOCAL_CFG.touch()
    if not LOCAL_TEX.exists(): LOCAL_TEX.mkdir()
    if not (LOCAL_TEX / 'preamble.tex').exists(): (LOCAL_TEX / 'preamble.tex').touch()


def main():
    app = QApplication(sys.argv)
    app.setStyleSheet('''QWidget#main_struc {border: 2px solid black;}
QWidget#title_struc {border: 2px solid black;}''')
    window = MainWindow()
    window.show()
    app.exec()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Runs Beamer GUI')

    args = parser.parse_args()
    init_dir('.')
    main()
