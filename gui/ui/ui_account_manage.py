from pathlib import Path
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QListWidget, 
                               QPushButton, QLabel, QSizePolicy)
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt, Signal

from gui.ui import ui_paths

class AccountItemWidget(QWidget):
    """账号列表项 Widget。"""
    copy_clicked = Signal(str)
    edit_clicked = Signal(str)
    delete_clicked = Signal(str)
    activate_clicked = Signal(str)

    def __init__(self, account_name, api_key, is_active=False, is_default=False, parent=None):
        super().__init__(parent)
        self.account_name = account_name
        self.api_key = api_key
        self.is_active = is_active
        self.is_default = is_default
        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)

        # 激活状态标记
        self.active_label = QLabel("✓" if self.is_active else "")
        self.active_label.setFixedWidth(20)
        self.active_label.setStyleSheet("color: green; font-weight: bold;")
        layout.addWidget(self.active_label)

        # 账号名称
        self.name_label = QLabel(self.account_name)
        self.name_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        if self.is_active:
            self.name_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(self.name_label)

        # API Key (遮罩显示)
        masked_key = self.mask_key(self.api_key)
        self.key_label = QLabel(masked_key)
        self.key_label.setStyleSheet("color: gray;")
        layout.addWidget(self.key_label)

        # 设为当前按钮
        self.activate_btn = QPushButton("设为当前")
        self.activate_btn.setEnabled(not self.is_active)
        self.activate_btn.clicked.connect(lambda: self.activate_clicked.emit(self.account_name))
        layout.addWidget(self.activate_btn)

        # 复制按钮
        self.copy_btn = QPushButton()
        self.copy_btn.setIcon(QIcon(ui_paths.get_icon_path("Copy.png")))
        self.copy_btn.setFixedSize(28, 28)
        self.copy_btn.setToolTip("复制 API Key")
        self.copy_btn.clicked.connect(lambda: self.copy_clicked.emit(self.api_key))
        layout.addWidget(self.copy_btn)

        # 编辑按钮
        self.edit_btn = QPushButton()
        self.edit_btn.setIcon(QIcon(ui_paths.get_icon_path("Edit.png")))
        self.edit_btn.setFixedSize(28, 28)
        self.edit_btn.setToolTip("编辑账号")
        self.edit_btn.clicked.connect(lambda: self.edit_clicked.emit(self.account_name))
        layout.addWidget(self.edit_btn)

        # 删除按钮 (默认账号不显示)
        self.delete_btn = QPushButton()
        self.delete_btn.setIcon(QIcon(ui_paths.get_icon_path("Delete.png")))
        self.delete_btn.setFixedSize(28, 28)
        self.delete_btn.setToolTip("删除账号")
        self.delete_btn.clicked.connect(lambda: self.delete_clicked.emit(self.account_name))
        self.delete_btn.setVisible(not self.is_default)
        layout.addWidget(self.delete_btn)

    def mask_key(self, key):
        """遮罩 API Key，只显示前后几位。"""
        if len(key) <= 12:
            return key[:4] + "..." + key[-4:] if len(key) > 8 else key
        return key[:6] + "..." + key[-6:]


class AccountManageUI(QWidget):
    """账号管理标签页 UI。"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # 标题和添加按钮
        header_layout = QHBoxLayout()
        
        title_label = QLabel("API Key 管理")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        header_layout.addStretch()
        
        self.add_btn = QPushButton()
        self.add_btn.setIcon(QIcon(ui_paths.get_icon_path("Add.png")))
        self.add_btn.setFixedSize(32, 32)
        self.add_btn.setToolTip("添加新账号")
        header_layout.addWidget(self.add_btn)
        
        layout.addLayout(header_layout)

        # 账号列表
        self.account_list = QListWidget()
        layout.addWidget(self.account_list)

        # 提示信息
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)
