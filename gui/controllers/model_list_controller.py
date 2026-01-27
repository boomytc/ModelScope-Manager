from PySide6.QtWidgets import QMessageBox, QInputDialog, QApplication, QListWidgetItem
from gui.ui.ui_model_list import ModelListUI, ModelItemWidget
from gui.ui.messages import get_core_error_message
from gui.controllers.workers import ModelListWorker, QuotaWorker
from core.model_service import ModelService

class ModelListTab(ModelListUI):
    """模型列表标签页功能逻辑。"""

    def __init__(self, config_manager, get_api_key_func=None, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self.model_service = ModelService(config_manager)
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
        quota = self.model_service.get_cached_quota()
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

        result = self.model_service.update_quota_from_list(quota_info)
        if result["updated"]:
            self.quota_label.setText(
                f"用户额度: {result['user_remaining']} / {result['user_limit']}"
            )

        self.update_model_list()

    def update_model_list(self):
        """根据搜索条件和收藏过滤更新模型列表。"""
        # 记录当前滚动条位置
        current_scroll_value = self.model_list.verticalScrollBar().value()

        search_text = self.search_input.text().lower()
        favorites_only = self.favorites_only_checkbox.isChecked()
        hidden_only = self.hidden_only_checkbox.isChecked()

        self.model_list.clear()

        items = self.model_service.build_model_items(
            self.all_models,
            search_text,
            favorites_only,
            hidden_only,
        )

        for item_data in items:
            item = QListWidgetItem(self.model_list)
            widget = ModelItemWidget(
                item_data["model_id"],
                item_data["is_favorite"],
                item_data["is_custom"],
                item_data["is_hidden"],
            )
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

        model, ok = QInputDialog.getItem(
            self,
            "选择模型",
            "选择一个模型进行额度检查 (将消耗 1 次调用):",
            items,
            0,
            False,
        )
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
        result = self.model_service.update_quota_from_check(quota_info)
        if result["updated"]:
            self.quota_label.setText(
                f"用户额度: {result['user_remaining']} / {result['user_limit']}"
            )
        else:
            self.quota_label.setText("用户额度: N/A / N/A")

        if result["model_remaining"] != "N/A" and result["model_limit"] != "N/A":
            self.model_quota_label.setText(
                f"模型额度: {result['model_remaining']} / {result['model_limit']}"
            )
        else:
            self.model_quota_label.setText("模型额度: N/A / N/A")

        if result["status_code"] == 200:
            QMessageBox.information(
                self,
                "额度已刷新",
                f"额度刷新成功。\n状态码: {result['status_code']}",
            )
        else:
            QMessageBox.warning(
                self,
                "额度检查警告",
                f"请求完成，状态码 {result['status_code']}，但响应头已更新。",
            )

    def on_quota_error(self, error_info):
        if self.sender() is not self.quota_worker:
            return
        self.quota_label.setText("额度: 错误")
        QMessageBox.critical(self, "错误", get_core_error_message(error_info))

    def on_error(self, error_info):
        if self.sender() is not self.worker:
            return
        self.all_models = []
        self.model_list.clear()
        self.status_label.setText("无数据/错误状态")
        self.quota_label.setText("用户额度: N/A / N/A")
        self.model_quota_label.setText("模型额度: N/A")
        QMessageBox.critical(self, "错误", get_core_error_message(error_info))

    def copy_model_id(self, model_id):
        clipboard = QApplication.clipboard()
        clipboard.setText(model_id)
        self.status_label.setText(f"已复制: {model_id}")

    def toggle_favorite(self, model_id):
        message = self.model_service.toggle_favorite(model_id)
        self.status_label.setText(message)
        self.update_model_list()

    def toggle_hide(self, model_id):
        message = self.model_service.toggle_hidden(model_id)
        self.status_label.setText(message)
        self.update_model_list()

    def on_add_custom_model(self):
        model_id, ok = QInputDialog.getText(
            self, "添加自定义模型", "请输入模型 ID (例: org/model-name):"
        )
        if ok and model_id.strip():
            model_id = model_id.strip()
            result = self.model_service.add_custom_model(model_id, self.all_models)
            if not result["ok"]:
                QMessageBox.information(self, "提示", result["message"])
                return
            self.status_label.setText(result["message"])
            self.update_model_list()

    def delete_custom_model(self, model_id):
        message = self.model_service.delete_custom_model(model_id)
        self.status_label.setText(message)
        self.update_model_list()
