from PySide6.QtWidgets import QMessageBox, QInputDialog, QApplication, QListWidgetItem
from gui.ui.ui_mainwindow import MainWindowUI
from gui.ui.ui_model_item import ModelItemWidget
from gui.func.func_account_manage import AccountManageTab
from gui.utils.config_manager import ConfigManager
from gui.utils.workers import ModelListWorker, QuotaWorker

class MainWindow(MainWindowUI):
    def __init__(self):
        super().__init__()
        self.config_manager = ConfigManager()
        self.all_models = []  # 存储 API 返回的模型列表
        self.current_api_key = None  # 当前使用的 API Key
        
        # 添加账号管理标签页
        self.account_tab = AccountManageTab(
            self.config_manager, 
            on_account_changed=self.on_account_changed
        )
        self.tab_widget.addTab(self.account_tab, "账号管理")
        
        self.restore_geometry()
        self.setup_model_tab_connections()
        self.init_api_key()
        self.load_data()

    def setup_model_tab_connections(self):
        """设置模型列表标签页的信号连接。"""
        mt = self.model_tab
        mt.refresh_quota_btn.clicked.connect(self.on_refresh_quota)
        mt.search_input.textChanged.connect(self.on_search_changed)
        mt.favorites_only_checkbox.stateChanged.connect(self.on_filter_changed)
        mt.add_model_btn.clicked.connect(self.on_add_custom_model)

    def init_api_key(self):
        """初始化当前 API Key。"""
        self.current_api_key = self.account_tab.get_active_api_key()

    def on_account_changed(self, account_name, api_key):
        """账号切换时的回调。"""
        self.current_api_key = api_key
        self.model_tab.status_label.setText(f"已切换到账号: {account_name}，正在刷新...")
        self.load_data()

    def restore_geometry(self):
        x, y, w, h = self.config_manager.get_window_geometry()
        self.setGeometry(x, y, w, h)

    def load_data(self):
        self.worker = ModelListWorker(self.current_api_key)
        self.worker.finished.connect(self.on_data_loaded)
        self.worker.error.connect(self.on_error)
        self.worker.start()

    def on_data_loaded(self, quota_info):
        models = quota_info.get("models", [])
        self.all_models = models
        self.model_tab.status_label.setText(f"找到 {len(models)} 个模型")
        
        user_limit = quota_info.get("user_limit", "N/A")
        user_remaining = quota_info.get("user_remaining", "N/A")
        self.model_tab.quota_label.setText(f"用户额度: {user_remaining} / {user_limit}")
        
        self.update_model_list()

    def update_model_list(self):
        """根据搜索条件和收藏过滤更新模型列表。"""
        mt = self.model_tab
        search_text = mt.search_input.text().lower()
        favorites_only = mt.favorites_only_checkbox.isChecked()
        
        custom_models = self.config_manager.get_custom_models()
        merged_models = list(self.all_models)
        for cm in custom_models:
            if cm not in merged_models:
                merged_models.append(cm)
        
        mt.model_list.clear()
        
        for model in merged_models:
            if search_text and search_text not in model.lower():
                continue
            
            is_favorite = self.config_manager.is_favorite(model)
            if favorites_only and not is_favorite:
                continue
            
            is_custom = self.config_manager.is_custom_model(model)
            
            item = QListWidgetItem(mt.model_list)
            widget = ModelItemWidget(model, is_favorite, is_custom)
            widget.copy_clicked.connect(self.copy_model_id)
            widget.favorite_clicked.connect(self.toggle_favorite)
            widget.delete_clicked.connect(self.delete_custom_model)
            item.setSizeHint(widget.sizeHint())
            mt.model_list.addItem(item)
            mt.model_list.setItemWidget(item, widget)

    def on_search_changed(self, text):
        self.update_model_list()

    def on_filter_changed(self, state):
        self.update_model_list()

    def on_refresh_quota(self):
        mt = self.model_tab
        items = []
        for i in range(mt.model_list.count()):
            widget = mt.model_list.itemWidget(mt.model_list.item(i))
            if widget:
                items.append(widget.model_id)
        
        if not items:
            QMessageBox.warning(self, "警告", "没有可供选择的模型。")
            return

        model, ok = QInputDialog.getItem(self, "选择模型", 
                                       "选择一个模型进行额度检查 (将消耗 1 次调用):", 
                                       items, 0, False)
        if ok and model:
            mt.quota_label.setText("额度: 检查中...")
            self.quota_worker = QuotaWorker(model, self.current_api_key)
            self.quota_worker.finished.connect(self.on_quota_checked)
            self.quota_worker.error.connect(self.on_quota_error)
            self.quota_worker.start()

    def on_quota_checked(self, quota_info):
        mt = self.model_tab
        user_limit = quota_info.get("user_limit", "N/A")
        user_remaining = quota_info.get("user_remaining", "N/A")
        model_limit = quota_info.get("model_limit", "N/A")
        model_remaining = quota_info.get("model_remaining", "N/A")
        status_code = quota_info.get("status_code", "Unknown")
        
        mt.quota_label.setText(f"用户额度: {user_remaining} / {user_limit}")
        mt.model_quota_label.setText(f"模型额度: {model_remaining} / {model_limit}")
        
        if status_code == 200:
            QMessageBox.information(self, "额度已刷新", f"额度刷新成功。\n状态码: {status_code}")
        else:
            QMessageBox.warning(self, "额度检查警告", 
                              f"请求完成，状态码 {status_code}，但响应头已更新。")

    def on_quota_error(self, error_msg):
        self.model_tab.quota_label.setText("额度: 错误")
        QMessageBox.critical(self, "错误", error_msg)

    def on_error(self, error_msg):
        self.model_tab.status_label.setText("加载模型出错")
        QMessageBox.critical(self, "错误", error_msg)

    def copy_model_id(self, model_id):
        clipboard = QApplication.clipboard()
        clipboard.setText(model_id)
        self.model_tab.status_label.setText(f"已复制: {model_id}")

    def toggle_favorite(self, model_id):
        if self.config_manager.is_favorite(model_id):
            self.config_manager.remove_favorite(model_id)
            self.model_tab.status_label.setText(f"已取消收藏: {model_id}")
        else:
            self.config_manager.add_favorite(model_id)
            self.model_tab.status_label.setText(f"已收藏: {model_id}")
        self.config_manager.save_config()

    def on_add_custom_model(self):
        model_id, ok = QInputDialog.getText(self, "添加自定义模型", 
                                           "请输入模型 ID (例: org/model-name):")
        if ok and model_id.strip():
            model_id = model_id.strip()
            if model_id in self.all_models:
                QMessageBox.information(self, "提示", "该模型已在 API 列表中。")
                return
            if self.config_manager.is_custom_model(model_id):
                QMessageBox.information(self, "提示", "该模型已存在。")
                return
            self.config_manager.add_custom_model(model_id)
            self.config_manager.save_config()
            self.model_tab.status_label.setText(f"已添加: {model_id}")
            self.update_model_list()

    def delete_custom_model(self, model_id):
        self.config_manager.remove_custom_model(model_id)
        self.config_manager.save_config()
        self.model_tab.status_label.setText(f"已删除: {model_id}")
        self.update_model_list()

    def closeEvent(self, event):
        rect = self.geometry()
        self.config_manager.set_window_geometry(
            rect.x(), rect.y(), rect.width(), rect.height()
        )
        self.config_manager.save_config()
        super().closeEvent(event)
