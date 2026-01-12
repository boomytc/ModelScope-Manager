from pathlib import Path
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QListWidget, 
                               QLabel, QPushButton, QLineEdit, QCheckBox, QSizePolicy)
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt, Signal


from gui.utils import app_paths

class ModelItemWidget(QWidget):
    """模型列表项 Widget。"""
    copy_clicked = Signal(str)
    favorite_clicked = Signal(str)
    hide_clicked = Signal(str)
    delete_clicked = Signal(str)

    def __init__(self, model_id, is_favorite=False, is_custom=False, is_hidden=False, parent=None):
        super().__init__(parent)
        self.model_id = model_id
        self.is_favorite = is_favorite
        self.is_custom = is_custom
        self.is_hidden = is_hidden
        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 2, 4, 2)

        # 模型名称
        self.label = QLabel(self.model_id)
        self.label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        layout.addWidget(self.label)

        # 复制按钮
        self.copy_btn = QPushButton()
        self.copy_btn.setIcon(QIcon(app_paths.get_icon_path("Copy.png")))
        self.copy_btn.setFixedSize(24, 24)
        self.copy_btn.setFlat(True)
        self.copy_btn.setToolTip("复制模型 ID")
        self.copy_btn.clicked.connect(lambda: self.copy_clicked.emit(self.model_id))
        layout.addWidget(self.copy_btn)

        # 收藏按钮
        self.favorite_btn = QPushButton()
        self.favorite_btn.setFixedSize(24, 24)
        self.favorite_btn.setFlat(True)
        self.update_favorite_icon()
        self.favorite_btn.clicked.connect(self.on_favorite_clicked)
        layout.addWidget(self.favorite_btn)

        # 隐藏按钮
        self.hide_btn = QPushButton()
        self.hide_btn.setFixedSize(24, 24)
        self.hide_btn.setFlat(True)
        self.update_hide_icon()
        self.hide_btn.clicked.connect(self.on_hide_clicked)
        layout.addWidget(self.hide_btn)

        # 删除按钮 (仅自定义模型显示)
        self.delete_btn = QPushButton()
        self.delete_btn.setIcon(QIcon(app_paths.get_icon_path("Delete.png")))
        self.delete_btn.setFixedSize(24, 24)
        self.delete_btn.setFlat(True)
        self.delete_btn.setToolTip("删除自定义模型")
        self.delete_btn.clicked.connect(lambda: self.delete_clicked.emit(self.model_id))
        self.delete_btn.setVisible(self.is_custom)
        layout.addWidget(self.delete_btn)

    def update_favorite_icon(self):
        if self.is_favorite:
            self.favorite_btn.setIcon(QIcon(app_paths.get_icon_path("Stared.png")))
            self.favorite_btn.setToolTip("从收藏移除")
        else:
            self.favorite_btn.setIcon(QIcon(app_paths.get_icon_path("Star.png")))
            self.favorite_btn.setToolTip("添加到收藏")

    def on_favorite_clicked(self):
        self.is_favorite = not self.is_favorite
        self.update_favorite_icon()
        self.favorite_clicked.emit(self.model_id)

    def update_hide_icon(self):
        if self.is_hidden:
            self.hide_btn.setIcon(QIcon(app_paths.get_icon_path("EyeClose.png")))
            self.hide_btn.setToolTip("取消隐藏")
        else:
            self.hide_btn.setIcon(QIcon(app_paths.get_icon_path("Eye.png")))
            self.hide_btn.setToolTip("隐藏模型")

    def on_hide_clicked(self):
        self.is_hidden = not self.is_hidden
        self.update_hide_icon()
        self.hide_clicked.emit(self.model_id)


class ModelListUI(QWidget):
    """模型列表标签页 UI。"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

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
        
        self.hidden_only_checkbox = QCheckBox("仅隐藏")
        filter_layout.addWidget(self.hidden_only_checkbox)
        
        self.add_model_btn = QPushButton()
        self.add_model_btn.setIcon(QIcon(app_paths.get_icon_path("Add.png")))
        self.add_model_btn.setFixedSize(28, 28)
        self.add_model_btn.setToolTip("添加自定义模型")
        filter_layout.addWidget(self.add_model_btn)
        
        layout.addLayout(filter_layout)

        # Model List
        self.model_list = QListWidget()
        layout.addWidget(self.model_list)
