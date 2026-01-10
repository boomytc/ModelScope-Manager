from pathlib import Path
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton, QSizePolicy
from PySide6.QtGui import QIcon
from PySide6.QtCore import Signal

class ModelItemWidget(QWidget):
    copy_clicked = Signal(str)
    favorite_clicked = Signal(str)

    def __init__(self, model_id, is_favorite=False, parent=None):
        super().__init__(parent)
        self.model_id = model_id
        self.is_favorite = is_favorite
        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 2, 4, 2)

        # 模型名称
        self.label = QLabel(self.model_id)
        self.label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        layout.addWidget(self.label)

        # 图标路径
        icon_dir = Path(__file__).resolve().parent.parent / "icon"

        # 复制按钮
        self.copy_btn = QPushButton()
        self.copy_btn.setIcon(QIcon(str(icon_dir / "Copy.png")))
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

    def update_favorite_icon(self):
        icon_dir = Path(__file__).resolve().parent.parent / "icon"
        if self.is_favorite:
            self.favorite_btn.setIcon(QIcon(str(icon_dir / "Stared.png")))
            self.favorite_btn.setToolTip("从收藏移除")
        else:
            self.favorite_btn.setIcon(QIcon(str(icon_dir / "Star.png")))
            self.favorite_btn.setToolTip("添加到收藏")

    def on_favorite_clicked(self):
        self.is_favorite = not self.is_favorite
        self.update_favorite_icon()
        self.favorite_clicked.emit(self.model_id)
