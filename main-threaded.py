import sys
import os
import fitz  # PyMuPDF
from PIL import Image
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog, QLabel,
    QMessageBox, QProgressBar, QComboBox
)
from PySide6.QtCore import QThread, Signal
from PySide6.QtGui import QIcon

# Function to locate bundled resources (PyInstaller-safe)
def resource_path(relative_path):
    """ Get absolute path to resource, works for development and PyInstaller EXE """
    if hasattr(sys, '_MEIPASS'):  # If running from PyInstaller bundle
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

class PDFtoJPGConverter(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("PDF to JPG Converter")
        self.setGeometry(100, 100, 500, 300)

        # Set application icon from "icon/" subdirectory
        icon_path = resource_path("icon/pdftojpg.ico")  
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        else:
            QMessageBox.warning(self, "Warning", f"Icon file not found: {icon_path}")

        layout = QVBoxLayout()

        self.label = QLabel("Select a PDF file to convert:")
        layout.addWidget(self.label)

        self.select_button = QPushButton("Select PDF")
        self.select_button.clicked.connect(self.select_pdf)
        layout.addWidget(self.select_button)

        self.scale_label = QLabel("Select Image Quality (Resolution Scale):")
        layout.addWidget(self.scale_label)

        self.scale_selector = QComboBox()
        self.scale_selector.addItems(["1x (72 DPI)", "2x (144 DPI)", "3x (216 DPI)", "4x (288 DPI)"])
        self.scale_selector.setCurrentIndex(3)
        layout.addWidget(self.scale_selector)

        self.convert_button = QPushButton("Convert to JPG")
        self.convert_button.clicked.connect(self.convert_pdf)
        self.convert_button.setEnabled(False)
        layout.addWidget(self.convert_button)

        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        self.setLayout(layout)
        self.pdf_path = ""

    def select_pdf(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select PDF File", "", "PDF Files (*.pdf)")
        if file_path:
            self.pdf_path = file_path
            self.label.setText(f"Selected: {os.path.basename(file_path)}")
            self.convert_button.setEnabled(True)

    def convert_pdf(self):
        if not self.pdf_path:
            QMessageBox.warning(self, "Error", "No PDF file selected.")
            return

        output_dir = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        if not output_dir:
            return

        scale_factors = [1, 2, 3, 4]
        selected_scale = scale_factors[self.scale_selector.currentIndex()]

        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)

        self.thread = PDFConverterThread(self.pdf_path, output_dir, selected_scale)
        self.thread.progress_updated.connect(self.progress_bar.setValue)
        self.thread.conversion_finished.connect(self.on_conversion_success)
        self.thread.conversion_failed.connect(self.on_conversion_failure)

        self.convert_button.setEnabled(False)
        self.thread.start()

    def on_conversion_success(self, output_dir):
        self.progress_bar.setVisible(False)
        QMessageBox.information(self, "Success", f"PDF converted and saved in {output_dir}")
        self.convert_button.setEnabled(True)

    def on_conversion_failure(self, error_msg):
        self.progress_bar.setVisible(False)
        QMessageBox.critical(self, "Error", f"Failed to convert PDF: {error_msg}")
        self.convert_button.setEnabled(True)

class PDFConverterThread(QThread):
    progress_updated = Signal(int)
    conversion_finished = Signal(str)
    conversion_failed = Signal(str)

    def __init__(self, pdf_path, output_dir, scale_factor):
        super().__init__()
        self.pdf_path = pdf_path
        self.output_dir = output_dir
        self.scale_factor = scale_factor

    def run(self):
        try:
            doc = fitz.open(self.pdf_path)
            base_name = os.path.splitext(os.path.basename(self.pdf_path))[0]

            total_pages = len(doc)
            for i, page in enumerate(doc):
                matrix = fitz.Matrix(self.scale_factor, self.scale_factor)
                pix = page.get_pixmap(matrix=matrix)
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                image_path = os.path.join(self.output_dir, f"{base_name}_page_{i+1}.jpg")
                img.save(image_path, "JPEG", quality=95)

                self.progress_updated.emit(i + 1)

            self.conversion_finished.emit(self.output_dir)
        except Exception as e:
            self.conversion_failed.emit(str(e))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PDFtoJPGConverter()
    window.show()
    sys.exit(app.exec())
