from PySide6.QtGui import QGuiApplication
from gui.ui.ui_mainwindow import MainWindowUI
from gui.controllers.model_list_controller import ModelListTab
from gui.controllers.account_manage_controller import AccountManageTab
from core import app_paths
from core.config_manager import ConfigManager

class MainWindow(MainWindowUI):
    """主窗口功能逻辑，整合各标签页。"""

    def __init__(self):
        super().__init__()
        self.config_manager = ConfigManager(app_paths.get_config_file())
        self.current_api_key = None

        self.init_tabs()
        self.restore_geometry()
        self.model_tab.load_data()

    def init_tabs(self):
        """初始化所有标签页。"""
        # Tab 1: 模型列表
        self.model_tab = ModelListTab(
            self.config_manager,
            get_api_key_func=self.get_current_api_key,
        )
        self.tab_widget.addTab(self.model_tab, "模型列表")

        # Tab 2: 账号管理
        self.account_tab = AccountManageTab(
            self.config_manager,
            on_account_changed=self.on_account_changed,
        )
        self.tab_widget.addTab(self.account_tab, "账号管理")

        # 初始化 API Key
        self.current_api_key = self.account_tab.get_active_api_key()

    def get_current_api_key(self):
        """获取当前 API Key 的回调函数。"""
        return self.current_api_key

    def on_account_changed(self, account_name, api_key):
        """账号切换时的回调。"""
        self.current_api_key = api_key
        self.model_tab.status_label.setText(f"已切换到账号: {account_name}，正在刷新...")
        self.model_tab.load_data()

    def restore_geometry(self):
        x, y, w, h = self.config_manager.get_window_geometry()
        screen = QGuiApplication.primaryScreen()
        if screen:
            available = screen.availableGeometry()
            if w <= 0:
                w = 800
            if h <= 0:
                h = 600
            w = min(w, available.width())
            h = min(h, available.height())
            if (
                x + w < available.left()
                or x > available.right()
                or y + h < available.top()
                or y > available.bottom()
            ):
                x = available.left() + max((available.width() - w) // 2, 0)
                y = available.top() + max((available.height() - h) // 2, 0)
        self.setGeometry(x, y, w, h)

    def closeEvent(self, event):
        rect = self.geometry()
        self.config_manager.set_window_geometry(
            rect.x(), rect.y(), rect.width(), rect.height()
        )
        self.config_manager.save_config()
        super().closeEvent(event)
