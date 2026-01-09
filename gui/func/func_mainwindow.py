from PySide6.QtWidgets import QMessageBox, QInputDialog
from gui.ui.ui_mainwindow import MainWindowUI
from gui.utils.config_manager import ConfigManager
from gui.utils.workers import ModelListWorker, QuotaWorker

class MainWindow(MainWindowUI):
    def __init__(self):
        super().__init__()
        self.config_manager = ConfigManager()
        self.restore_geometry()
        self.refresh_quota_btn.clicked.connect(self.on_refresh_quota)
        self.load_data()

    def restore_geometry(self):
        x, y, w, h = self.config_manager.get_window_geometry()
        self.setGeometry(x, y, w, h)

    def load_data(self):
        self.worker = ModelListWorker()
        self.worker.finished.connect(self.on_data_loaded)
        self.worker.error.connect(self.on_error)
        self.worker.start()

    def on_data_loaded(self, quota_info):
        models = quota_info.get("models", [])
        self.status_label.setText(f"找到 {len(models)} 个模型")
        
        # 更新限流信息显示
        user_limit = quota_info.get("user_limit", "N/A")
        user_remaining = quota_info.get("user_remaining", "N/A")
        self.quota_label.setText(f"用户额度: {user_remaining} / {user_limit}")
        
        self.model_list.clear()
        self.model_list.addItems(models)

    def on_refresh_quota(self):
        # 获取当前列表中的模型
        items = [self.model_list.item(i).text() for i in range(self.model_list.count())]
        if not items:
            QMessageBox.warning(self, "警告", "没有可供选择的模型。")
            return

        model, ok = QInputDialog.getItem(self, "选择模型", 
                                       "选择一个模型进行额度检查 (将消耗 1 次调用):", 
                                       items, 0, False)
        if ok and model:
            self.quota_label.setText("额度: 检查中...")
            self.quota_worker = QuotaWorker(model)
            self.quota_worker.finished.connect(self.on_quota_checked)
            self.quota_worker.error.connect(self.on_quota_error)
            self.quota_worker.start()

    def on_quota_checked(self, quota_info):
        user_limit = quota_info.get("user_limit", "N/A")
        user_remaining = quota_info.get("user_remaining", "N/A")
        
        model_limit = quota_info.get("model_limit", "N/A")
        model_remaining = quota_info.get("model_remaining", "N/A")
        
        status_code = quota_info.get("status_code", "Unknown")
        
        self.quota_label.setText(f"用户额度: {user_remaining} / {user_limit}")
        self.model_quota_label.setText(f"模型额度: {model_remaining} / {model_limit}")
        
        if status_code == 200:
            QMessageBox.information(self, "额度已刷新", 
                                  f"额度刷新成功。\n状态码: {status_code}")
        else:
            QMessageBox.warning(self, "额度检查警告", 
                              f"请求完成，状态码 {status_code}，但响应头已更新。")

    def on_quota_error(self, error_msg):
        self.quota_label.setText("额度: 错误")
        QMessageBox.critical(self, "错误", error_msg)

    def on_error(self, error_msg):
        self.status_label.setText("加载模型出错")
        QMessageBox.critical(self, "错误", error_msg)

    def closeEvent(self, event):
        # 关闭时保存窗口几何信息
        rect = self.geometry()
        self.config_manager.set_window_geometry(
            rect.x(), rect.y(), rect.width(), rect.height()
        )
        self.config_manager.save_config()
        super().closeEvent(event)
