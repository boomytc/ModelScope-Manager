from PySide6.QtWidgets import QMessageBox, QInputDialog, QApplication, QListWidgetItem
from gui.ui.ui_model_list import ModelListUI, ModelItemWidget
from gui.utils.workers import ModelListWorker, QuotaWorker

class ModelListTab(ModelListUI):
    """模型列表标签页功能逻辑。"""
    
    def __init__(self, config_manager, get_api_key_func=None, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self.get_api_key = get_api_key_func  # 获取当前 API Key 的回调
        self.all_models = []  # 存储 API 返回的模型列表
        self.worker = None  # 模型列表加载 worker
        self.quota_worker = None  # 额度检查 worker
        
        self.refresh_quota_btn.clicked.connect(self.on_refresh_quota)
        self.search_input.textChanged.connect(self.on_search_changed)
        self.favorites_only_checkbox.stateChanged.connect(self.on_filter_changed)
        self.hidden_only_checkbox.stateChanged.connect(self.on_filter_changed)
        self.add_model_btn.clicked.connect(self.on_add_custom_model)

        self.load_cached_quota()

    def load_cached_quota(self):
        """加载缓存的额度信息。"""
        quota = self.config_manager.get_last_quota()
        user_remaining = quota.get("user_remaining", "N/A")
        user_limit = quota.get("user_limit", "N/A")
        if user_remaining != "N/A":
            self.quota_label.setText(f"用户额度: {user_remaining} / {user_limit}")

    def load_data(self):
        """加载模型列表。"""
        # 加载当前账号的缓存额度
        self.load_cached_quota()

        api_key = self.get_api_key() if self.get_api_key else None
        self.worker = ModelListWorker(api_key)
        self.worker.finished.connect(self.on_data_loaded)
        self.worker.error.connect(self.on_error)
        self.worker.start()

    def on_data_loaded(self, quota_info):
        if self.sender() is not self.worker:
            return
        models = quota_info.get("models", [])
        self.all_models = models
        self.status_label.setText(f"找到 {len(models)} 个模型")
        
        user_limit = quota_info.get("user_limit", "N/A")
        user_remaining = quota_info.get("user_remaining", "N/A")

        # 仅当获取到有效额度时才更新和保存
        if user_remaining != "N/A" and user_limit != "N/A":
            self.quota_label.setText(f"用户额度: {user_remaining} / {user_limit}")
            self.config_manager.set_last_quota(user_remaining, user_limit)
            self.config_manager.save_config()
        elif user_remaining == "N/A":
            # 如果是 N/A，尝试保持显示缓存的值（如果还未显示）
            # 注意：load_cached_quota 已经在 load_data 开始时调用过，
            # 所以这里不需要做什么，只要不覆盖成 N/A 即可。
            pass
        
        self.update_model_list()

    def update_model_list(self):
        """根据搜索条件和收藏过滤更新模型列表。"""
        # 记录当前滚动条位置
        current_scroll_value = self.model_list.verticalScrollBar().value()
        
        search_text = self.search_input.text().lower()
        favorites_only = self.favorites_only_checkbox.isChecked()
        hidden_only = self.hidden_only_checkbox.isChecked()
        
        custom_models = self.config_manager.get_custom_models()
        merged_models = list(self.all_models)
        for cm in custom_models:
            if cm not in merged_models:
                merged_models.append(cm)
        
        self.model_list.clear()
        
        for model in merged_models:
            if search_text and search_text not in model.lower():
                continue
            
            is_favorite = self.config_manager.is_favorite(model)
            if favorites_only and not is_favorite:
                continue
            
            is_visible = not self.config_manager.is_invisible(model)
            # 如果勾选了“仅隐藏”，只显示隐藏的
            if hidden_only:
                if is_visible:
                    continue
            # 如果没勾选“仅隐藏”，默认不显示隐藏的
            else:
                if not is_visible:
                    continue

            is_custom = self.config_manager.is_custom_model(model)
            
            item = QListWidgetItem(self.model_list)
            # 注意 ModelItemWidget 的构造函数参数变了
            widget = ModelItemWidget(model, is_favorite, is_custom, not is_visible)
            widget.copy_clicked.connect(self.copy_model_id)
            widget.favorite_clicked.connect(self.toggle_favorite)
            widget.hide_clicked.connect(self.toggle_hide)
            widget.delete_clicked.connect(self.delete_custom_model)
            item.setSizeHint(widget.sizeHint())
            self.model_list.addItem(item)
            self.model_list.setItemWidget(item, widget)
            
        # 恢复滚动条位置
        self.model_list.verticalScrollBar().setValue(current_scroll_value)

    def on_search_changed(self, text):
        self.update_model_list()

    def on_filter_changed(self, state):
        self.update_model_list()

    def on_refresh_quota(self):
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
            api_key = self.get_api_key() if self.get_api_key else None
            self.quota_worker = QuotaWorker(model, api_key)
            self.quota_worker.finished.connect(self.on_quota_checked)
            self.quota_worker.error.connect(self.on_quota_error)
            self.quota_worker.start()

    def on_quota_checked(self, quota_info):
        if self.sender() is not self.quota_worker:
            return
        user_limit = quota_info.get("user_limit", "N/A")
        user_remaining = quota_info.get("user_remaining", "N/A")
        model_limit = quota_info.get("model_limit", "N/A")
        model_remaining = quota_info.get("model_remaining", "N/A")
        status_code = quota_info.get("status_code", "Unknown")
        
        if user_remaining != "N/A" and user_limit != "N/A":
            self.quota_label.setText(f"用户额度: {user_remaining} / {user_limit}")
            self.config_manager.set_last_quota(user_remaining, user_limit)
            self.config_manager.save_config()
        else:
            self.quota_label.setText("用户额度: N/A / N/A")

        if model_remaining != "N/A" and model_limit != "N/A":
            self.model_quota_label.setText(f"模型额度: {model_remaining} / {model_limit}")
        else:
            self.model_quota_label.setText("模型额度: N/A / N/A")
        
        if status_code == 200:
            QMessageBox.information(self, "额度已刷新", f"额度刷新成功。\n状态码: {status_code}")
        else:
            QMessageBox.warning(self, "额度检查警告", 
                              f"请求完成，状态码 {status_code}，但响应头已更新。")

    def on_quota_error(self, error_msg):
        if self.sender() is not self.quota_worker:
            return
        self.quota_label.setText("额度: 错误")
        QMessageBox.critical(self, "错误", error_msg)

    def on_error(self, error_msg):
        if self.sender() is not self.worker:
            return
        self.all_models = []
        self.model_list.clear()
        self.status_label.setText("无数据/错误状态")
        self.quota_label.setText("用户额度: N/A / N/A")
        self.model_quota_label.setText("模型额度: N/A")
        QMessageBox.critical(self, "错误", error_msg)

    def copy_model_id(self, model_id):
        clipboard = QApplication.clipboard()
        clipboard.setText(model_id)
        self.status_label.setText(f"已复制: {model_id}")

    def toggle_favorite(self, model_id):
        if self.config_manager.is_favorite(model_id):
            self.config_manager.remove_favorite(model_id)
            self.status_label.setText(f"已取消收藏: {model_id}")
        else:
            self.config_manager.add_favorite(model_id)
            self.status_label.setText(f"已收藏: {model_id}")
        self.config_manager.save_config()
        self.update_model_list()

    def toggle_hide(self, model_id):
        if self.config_manager.is_invisible(model_id):
            self.config_manager.remove_invisible(model_id)
            self.status_label.setText(f"已取消隐藏: {model_id}")
        else:
            self.config_manager.add_invisible(model_id)
            self.status_label.setText(f"已隐藏: {model_id}")
        self.config_manager.save_config()
        self.update_model_list()

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
            self.status_label.setText(f"已添加: {model_id}")
            self.update_model_list()

    def delete_custom_model(self, model_id):
        self.config_manager.remove_custom_model(model_id)
        self.config_manager.save_config()
        self.status_label.setText(f"已删除: {model_id}")
        self.update_model_list()
