import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QPushButton, QListWidget, QFileDialog, QMessageBox)
from PyQt6.QtCore import Qt, QMimeData
from PyQt6.QtGui import QDragEnterEvent, QDropEvent
import PyPDF2

class DragDropListWidget(QListWidget):
    def __init__(self, parent_window):
        super().__init__(parent_window)
        self.setAcceptDrops(True)
        self.parent_window = parent_window

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.setDropAction(Qt.DropAction.CopyAction)
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event: QDropEvent):
        if event.mimeData().hasUrls():
            event.setDropAction(Qt.DropAction.CopyAction)
            event.accept()
            links = []
            for url in event.mimeData().urls():
                links.append(str(url.toLocalFile()))
            self.parent_window.add_files(links)
        else:
            event.ignore()

class PDFMergerWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PDF Merger")
        self.setGeometry(100, 100, 500, 400)
        self.file_list = []

        # Create central widget and layout
        central_widget = QWidget()
        layout = QVBoxLayout()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        # Create and add widgets
        self.list_widget = DragDropListWidget(self)

        add_button = QPushButton("Add PDFs")
        remove_button = QPushButton("Remove Selected")
        merge_button = QPushButton("Merge PDFs")

        layout.addWidget(self.list_widget)
        layout.addWidget(add_button)
        layout.addWidget(remove_button)
        layout.addWidget(merge_button)

        # Connect buttons to functions
        add_button.clicked.connect(self.add_pdfs)
        remove_button.clicked.connect(self.remove_selected)
        merge_button.clicked.connect(self.merge_pdfs)

    def add_pdfs(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Select PDFs", "", "PDF Files (*.pdf)")
        self.add_files(files)

    def add_files(self, files):
        for file in files:
            if file.lower().endswith('.pdf') and file not in self.file_list:
                self.file_list.append(file)
                self.list_widget.addItem(os.path.basename(file))

    def remove_selected(self):
        for item in self.list_widget.selectedItems():
            self.file_list.remove(self.file_list[self.list_widget.row(item)])
            self.list_widget.takeItem(self.list_widget.row(item))

    def merge_pdfs(self):
        if not self.file_list:
            QMessageBox.warning(self, "Warning", "Please select PDF files to merge.")
            return

        output_file, _ = QFileDialog.getSaveFileName(self, "Save Merged PDF", "", "PDF Files (*.pdf)")
        if not output_file:
            return

        try:
            pdf_merger = PyPDF2.PdfMerger()
            for pdf in self.file_list:
                pdf_merger.append(pdf)
            with open(output_file, 'wb') as output:
                pdf_merger.write(output)
            QMessageBox.information(self, "Success", f"PDFs merged successfully! Output file: {output_file}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = PDFMergerWindow()
    window.show()
    sys.exit(app.exec())