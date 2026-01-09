from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QListWidget, QLabel
from PySide6.QtCore import Qt

class MainWindowUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ModelScope Manager")
        self.init_ui()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        self.status_label = QLabel("Loading models...")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)

        self.model_list = QListWidget()
        layout.addWidget(self.model_list)
