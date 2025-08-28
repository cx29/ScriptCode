import sys
import os

from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFileDialog, QListWidget, QListWidgetItem, QMessageBox
)

from PyQt5.QtCore import Qt


class CsvMergeApp(QWidget):
    def __init__(self):
        super().__init__()
        self.file_list = None
        self.path_input = None
        self.file_input = None
        self.setWindowTitle("CsvMerge")
        self.setGeometry(300, 300, 800, 600)
        self.setStyleSheet("background-color: #fdfdfd;")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        file_layout = QHBoxLayout()
        file_label = QLabel("Csv File Name:")
        file_label.setStyleSheet("color:blue;font-weight:bold;")
        self.file_input = QLineEdit()
        self.file_input.setPlaceholderText("Enter CSV File Name")
        self.file_input.setStyleSheet("background-color: #fdfdfd;padding:3px;")
        file_layout.addWidget(file_label)
        file_layout.addWidget(self.file_input)
        layout.addLayout(file_layout)

        path_layout = QHBoxLayout()
        path_label = QLabel("Directory Path:")
        path_label.setStyleSheet("color:blue;font-weight:bold;")
        self.path_input = QLineEdit()
        self.path_input.setStyleSheet("background-color: #fdfdfd;color:#000000;padding:3px;")
        path_btn = QPushButton("Select Directory")
        path_btn.setStyleSheet("background-color: lightblue;border-radius:5px;padding:5px;")
        path_btn.clicked.connect(self.select_directory)
        path_layout.addWidget(path_label)
        path_layout.addWidget(self.path_input)
        path_layout.addWidget(path_btn)
        path_layout.addWidget(self.path_input)
        layout.addLayout(path_layout)

        search_btn = QPushButton("Search")
        search_btn.setStyleSheet("background-color: lightgreen;border-radius:5px;padding:5px;")
        search_btn.clicked.connect(self.search_files)
        layout.addWidget(search_btn)

        self.file_list = QListWidget()
        layout.addWidget(self.file_list)

        self.setLayout(layout)

    def select_directory(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Directory")
        if folder:
            self.path_input.setText(folder)

    def search_files(self):
        dir = self.path_input.text().strip()
        filename = self.file_input.text().strip()

        if not dir or not filename:
            QMessageBox.warning(self, "Error", "Please enter valid directory and filename")
            return

        self.file_list.clear()
        for root, dirs, files in os.walk(dir):
            for file in files:
                if filename.lower() in file.lower():
                    full_path = os.path.join(root, file)
                    self.add_fil_item(full_path)

        if self.file_list.isEmpty():
            QMessageBox.Information(self, "Info", f"No Files found '{filename}'")

    def add_file_item(self, file_path):
        item = QListWidgetItem(file_path)
        item.setToolTip(file_path)
        self.file_list.addItem(item)
        delete_btn = QPushButton("Delete")
        delete_btn.setStyleSheet(
            "background-color:red; color:white;border-radius:5px;padding:5px;"
        )
        delete_btn.clicked.connect(lambda _, it=item: self.delete_file(it))
        self.file_list.setItemWidget(item,delete_btn)

    def delete_file(self, item):
        file_path = item.text()
        self.file_list.takeItem(self.file_list.row(item))



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CsvMergeApp()
    window.show()
    sys.exit(app.exec_())
