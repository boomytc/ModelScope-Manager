from PySide6.QtWidgets import QMessageBox, QInputDialog, QApplication, QListWidgetItem
from gui.ui.ui_mainwindow import MainWindowUI
from gui.ui.ui_model_item import ModelItemWidget
from gui.utils.config_manager import ConfigManager
from gui.utils.workers import ModelListWorker, QuotaWorker

class MainWindow(MainWindowUI):
    def __init__(self):
        super().__init__()
        self.config_manager = ConfigManager()
        self.all_models = []  # 存储 API 返回的模型列表
        self.restore_geometry()
        self.refresh_quota_btn.clicked.connect(self.on_refresh_quota)
        self.search_input.textChanged.connect(self.on_search_changed)
        self.favorites_only_checkbox.stateChanged.connect(self.on_filter_changed)
        self.add_model_btn.clicked.connect(self.on_add_custom_model)
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
        self.all_models = models  # 保存完整列表
        self.status_label.setText(f"找到 {len(models)} 个模型")
        
        # 更新限流信息显示
        user_limit = quota_info.get("user_limit", "N/A")
        user_remaining = quota_info.get("user_remaining", "N/A")
        self.quota_label.setText(f"用户额度: {user_remaining} / {user_limit}")
        
        self.update_model_list()

    def update_model_list(self):
        """根据搜索条件和收藏过滤更新模型列表。"""
        search_text = self.search_input.text().lower()
        favorites_only = self.favorites_only_checkbox.isChecked()
        
        # 合并 API 模型和自定义模型 (去重)
        custom_models = self.config_manager.get_custom_models()
        merged_models = list(self.all_models)
        for cm in custom_models:
            if cm not in merged_models:
                merged_models.append(cm)
        
        self.model_list.clear()
        
        for model in merged_models:
            # 搜索过滤
            if search_text and search_text not in model.lower():
                continue
            
            # 收藏过滤
            is_favorite = self.config_manager.is_favorite(model)
            if favorites_only and not is_favorite:
                continue
            
            # 检查是否为自定义模型
            is_custom = self.config_manager.is_custom_model(model)
            
            # 创建自定义 item widget
            item = QListWidgetItem(self.model_list)
            widget = ModelItemWidget(model, is_favorite, is_custom)
            widget.copy_clicked.connect(self.copy_model_id)
            widget.favorite_clicked.connect(self.toggle_favorite)
            widget.delete_clicked.connect(self.delete_custom_model)
            item.setSizeHint(widget.sizeHint())
            self.model_list.addItem(item)
            self.model_list.setItemWidget(item, widget)

    def on_search_changed(self, text):
        """搜索内容变化时过滤列表。"""
        self.update_model_list()

    def on_filter_changed(self, state):
        """收藏过滤复选框变化时更新列表。"""
        self.update_model_list()

    def on_refresh_quota(self):
        # 获取当前列表中的模型
        items = []
        for i in range(self.model_list.count()):
            widget = self.model_list.itemWidget(self.model_list.item(i))
            if widget:
                items.append(widget.model_id)
        
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

    def copy_model_id(self, model_id):
        """复制模型 ID 到剪贴板。"""
        clipboard = QApplication.clipboard()
        clipboard.setText(model_id)
        self.status_label.setText(f"已复制: {model_id}")

    def toggle_favorite(self, model_id):
        """切换收藏状态。"""
        if self.config_manager.is_favorite(model_id):
            self.config_manager.remove_favorite(model_id)
            self.status_label.setText(f"已取消收藏: {model_id}")
        else:
            self.config_manager.add_favorite(model_id)
            self.status_label.setText(f"已收藏: {model_id}")
        self.config_manager.save_config()

    def on_add_custom_model(self):
        """添加自定义模型。"""
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
            self.status_label.setText(f"已添加: {model_id}")
            self.update_model_list()

    def delete_custom_model(self, model_id):
        """删除自定义模型。"""
        self.config_manager.remove_custom_model(model_id)
        self.config_manager.save_config()
        self.status_label.setText(f"已删除: {model_id}")
        self.update_model_list()

    def closeEvent(self, event):
        # 关闭时保存窗口几何信息
        rect = self.geometry()
        self.config_manager.set_window_geometry(
            rect.x(), rect.y(), rect.width(), rect.height()
        )
        self.config_manager.save_config()
        super().closeEvent(event)
