from pathlib import Path
import tomllib

from PySide6.QtWidgets import QApplication, QWidget, QMainWindow, QPushButton, QLabel, QHBoxLayout, QVBoxLayout, QFileDialog
from PySide6.QtPdf import QPdfDocument
from PySide6.QtPdfWidgets import QPdfView
from PySide6.QtCore import Qt, QMargins


# class SwapButton(QPushButton):
#     def __init__(self):
#         super().__init__('Test')
#         self.clicked.connect(self.on_clicked)

#     def on_clicked(self):
#         if (view := self.window().texpdf.view).isVisible():
#             view.setVisible(False)
#             self.window().struc.setVisible(True)
#         else:
#             view.setVisible(True)
#             self.window().struc.setVisible(False)


# class TexSelectButton(QPushButton):
#     def __init__(self):
#         super().__init__('Open tex')
#         self.clicked.connect(self.on_clicked)

#     def on_clicked(self):
#         path, _ = QFileDialog.getOpenFileName(self, caption='Open tex file', filter='Tex files (*.tex)')
#         self.window().texpdf.tex_path = Path(path)
