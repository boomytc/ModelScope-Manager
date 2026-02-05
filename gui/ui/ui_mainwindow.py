from PySide6.QtWidgets import (QMainWindow, QTabWidget, QWidget, QVBoxLayout, 
                               QHBoxLayout, QLabel, QPushButton, QFrame, QSizeGrip)
from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QPainter, QColor, QBrush, QPen

class MainWindowUI(QMainWindow):
    """主窗口 UI，包含标签页容器，使用自定义无边框圆角设计。"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ModelScope Manager")
        
        # 无边框 + 透明背景
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # 窗口拖动相关
        self._is_dragging = False
        self._drag_position = QPoint()
        
        self.init_ui()
        self.apply_styles()

    def init_ui(self):
        # 主容器 (用于绘制背景)
        self.central_widget = QWidget()
        self.central_widget.setObjectName("CentralWidget")
        self.setCentralWidget(self.central_widget)
        
        # 主布局
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(10, 10, 10, 10) # 留出边缘给阴影或圆角
        self.main_layout.setSpacing(0)
        
        # 自定义标题栏
        self.init_title_bar()
        
        # 内容区域
        self.content_container = QWidget()
        self.content_container.setObjectName("ContentContainer")
        self.content_layout = QVBoxLayout(self.content_container)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        
        self.tab_widget = QTabWidget()
        self.content_layout.addWidget(self.tab_widget)
        
        # 添加 SizeGrip 到右下角
        grip_layout = QHBoxLayout()
        grip_layout.setContentsMargins(0, 0, 0, 0)
        grip_layout.addStretch()
        self.size_grip = QSizeGrip(self.content_container)
        self.size_grip.setFixedSize(16, 16)
        grip_layout.addWidget(self.size_grip)
        # 将 grip 布局添加到内容布局的底部，但这会占用空间
        # 更好的方法是将 SizeGrip 作为子控件绝对定位，或者放在状态栏位置
        # 这里简单起见，我们把 SizeGrip 直接放在 content_container 的右下角
        # 但由于 content_layout 已经是 VBoxLayout，我们可以添加到底部
        self.content_layout.addLayout(grip_layout)

        self.main_layout.addWidget(self.content_container)

    def init_title_bar(self):
        self.title_bar = QWidget()
        self.title_bar.setObjectName("TitleBar")
        self.title_bar.setFixedHeight(40)
        
        title_layout = QHBoxLayout(self.title_bar)
        title_layout.setContentsMargins(15, 0, 10, 0)
        title_layout.setSpacing(10)
        
        # 标题
        self.title_label = QLabel("ModelScope Manager")
        self.title_label.setObjectName("TitleLabel")
        title_layout.addWidget(self.title_label)
        
        title_layout.addStretch()
        
        # 最小化按钮
        self.min_btn = QPushButton("—")
        self.min_btn.setObjectName("TitleBtn")
        self.min_btn.setFixedSize(30, 30)
        self.min_btn.clicked.connect(self.showMinimized)
        title_layout.addWidget(self.min_btn)
        
        # 关闭按钮
        self.close_btn = QPushButton("✕")
        self.close_btn.setObjectName("CloseBtn")
        self.close_btn.setFixedSize(30, 30)
        self.close_btn.clicked.connect(self.close)
        title_layout.addWidget(self.close_btn)
        
        self.main_layout.addWidget(self.title_bar)

    def apply_styles(self):
        self.setStyleSheet("""
            #CentralWidget {
                background: transparent;
            }
            #TitleBar {
                background-color: transparent;
                border-top-left-radius: 16px;
                border-top-right-radius: 16px;
            }
            #TitleLabel {
                font-family: 'Segoe UI', sans-serif;
                font-size: 14px;
                font-weight: bold;
                color: #333333;
            }
            #TitleBtn {
                background-color: transparent;
                border: none;
                border-radius: 15px;
                font-weight: bold;
                color: #555555;
            }
            #TitleBtn:hover {
                background-color: rgba(0, 0, 0, 0.1);
            }
            #CloseBtn {
                background-color: transparent;
                border: none;
                border-radius: 15px;
                font-weight: bold;
                color: #555555;
            }
            #CloseBtn:hover {
                background-color: #FF5F57;
                color: white;
            }
            QTabWidget::pane {
                border: 1px solid rgba(200, 200, 200, 0.5);
                background: rgba(255, 255, 255, 0.6);
                border-bottom-left-radius: 16px;
                border-bottom-right-radius: 16px;
            }
            QTabBar::tab {
                background: rgba(240, 240, 240, 0.6);
                border: 1px solid transparent;
                padding: 8px 16px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                margin-right: 4px;
                color: #555;
            }
            QTabBar::tab:selected {
                background: rgba(255, 255, 255, 0.8);
                color: #000;
                font-weight: bold;
                border-bottom: 2px solid #007AFF;
            }
            QTabBar::tab:hover {
                background: rgba(250, 250, 250, 0.7);
            }
        """)

    def paintEvent(self, event):
        # 绘制圆角背景
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 背景颜色 (半透明白色，模拟 Glassmorphism)
        bg_color = QColor(255, 255, 255, 240) # 94% 不透明度
        painter.setBrush(QBrush(bg_color))
        painter.setPen(Qt.NoPen)
        
        # 绘制圆角矩形 (留出一点 margin 避免贴边)
        rect = self.rect().adjusted(5, 5, -5, -5)
        painter.drawRoundedRect(rect, 16, 16)
        
        # 绘制边框 (细微的白色边框增加质感)
        border_pen = QPen(QColor(255, 255, 255, 100))
        border_pen.setWidth(1)
        painter.setPen(border_pen)
        painter.drawRoundedRect(rect, 16, 16)

    # --- 窗口拖动逻辑 ---
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            # 只有点击标题栏区域才允许拖动
            if self.title_bar.geometry().contains(event.pos() - self.central_widget.pos()):
                self._is_dragging = True
                self._drag_position = event.globalPos() - self.frameGeometry().topLeft()
                event.accept()

    def mouseMoveEvent(self, event):
        if self._is_dragging and event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self._drag_position)
            event.accept()

    def mouseReleaseEvent(self, event):
        self._is_dragging = False
