from PySide6.QtWidgets import QMainWindow, QTabWidget

class MainWindowUI(QMainWindow):
    """主窗口 UI，包含标签页容器。"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ModelScope Manager")
        self.init_ui()

    def init_ui(self):
        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)
