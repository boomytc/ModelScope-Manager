from pathlib import Path
from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QListWidget, QLabel, QHBoxLayout, QPushButton, QLineEdit, QCheckBox
from PySide6.QtGui import QIcon
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

        # Quota Information Area
        quota_layout = QHBoxLayout()
        self.quota_label = QLabel("用户额度: 加载中...")
        self.quota_label.setAlignment(Qt.AlignLeft)
        quota_layout.addWidget(self.quota_label)
        
        self.refresh_quota_btn = QPushButton("刷新额度")
        quota_layout.addWidget(self.refresh_quota_btn)
        
        layout.addLayout(quota_layout)

        # Model Quota Display
        self.model_quota_label = QLabel("模型额度: N/A")
        self.model_quota_label.setAlignment(Qt.AlignLeft)
        layout.addWidget(self.model_quota_label)

        self.status_label = QLabel("正在加载模型...")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)

        # Search and Filter Area
        filter_layout = QHBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("搜索模型...")
        filter_layout.addWidget(self.search_input)
        
        self.favorites_only_checkbox = QCheckBox("仅收藏")
        filter_layout.addWidget(self.favorites_only_checkbox)
        
        # Add Custom Model Button
        icon_dir = Path(__file__).resolve().parent.parent / "icon"
        self.add_model_btn = QPushButton()
        self.add_model_btn.setIcon(QIcon(str(icon_dir / "Add.png")))
        self.add_model_btn.setFixedSize(28, 28)
        self.add_model_btn.setToolTip("添加自定义模型")
        filter_layout.addWidget(self.add_model_btn)
        
        layout.addLayout(filter_layout)

        # Model List
        self.model_list = QListWidget()
        layout.addWidget(self.model_list)
