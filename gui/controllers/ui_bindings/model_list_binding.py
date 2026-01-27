from PySide6.QtWidgets import QMessageBox, QInputDialog, QApplication, QListWidgetItem
from gui.ui.ui_model_list import ModelListUI, ModelItemWidget
from gui.ui.messages import get_core_error_message
from gui.controllers.app.model_list_app import ModelListApp

class ModelListTab(ModelListUI):
    """模型列表标签页 UI 绑定层。"""

    def __init__(self, config_manager, get_api_key_func=None, parent=None):
        super().__init__(parent)
        self.app = ModelListApp(config_manager)
        self.get_api_key = get_api_key_func  # 获取当前 API Key 的回调
        self.all_models = []  # 存储 API 返回的模型列表

        self.refresh_quota_btn.clicked.connect(self.on_refresh_quota)
        self.search_input.textChanged.connect(self.on_search_changed)
        self.favorites_only_checkbox.stateChanged.connect(self.on_filter_changed)
        self.hidden_only_checkbox.stateChanged.connect(self.on_filter_changed)
        self.add_model_btn.clicked.connect(self.on_add_custom_model)

        self.load_cached_quota()

    def load_cached_quota(self):
        """加载缓存的额度信息。"""
        quota = self.app.get_cached_quota()
        user_remaining = quota.get("user_remaining", "N/A")
        user_limit = quota.get("user_limit", "N/A")
        if user_remaining != "N/A":
            self._set_user_quota_label(user_remaining, user_limit)

    def load_data(self):
        """加载模型列表。"""
        self.load_cached_quota()

        api_key = self.get_api_key() if self.get_api_key else None
        self.app.load_models(api_key, self.on_data_loaded, self.on_error)

    def on_data_loaded(self, quota_info):
        if not self.app.is_list_worker(self.sender()):
            return
        models = quota_info.get("models", [])
        self.all_models = models
        self.status_label.setText(f"找到 {len(models)} 个模型")

        result = self.app.update_quota_from_list(quota_info)
        if result["updated"]:
            self._set_user_quota_label(result["user_remaining"], result["user_limit"])

        self.update_model_list()

    def update_model_list(self):
        """根据搜索条件和收藏过滤更新模型列表。"""
        current_scroll_value = self.model_list.verticalScrollBar().value()

        search_text = self.search_input.text().lower()
        favorites_only = self.favorites_only_checkbox.isChecked()
        hidden_only = self.hidden_only_checkbox.isChecked()

        self.model_list.clear()

        items = self.app.build_model_items(
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
            self.app.check_quota(model, api_key, self.on_quota_checked, self.on_quota_error)

    def on_quota_checked(self, quota_info):
        if not self.app.is_quota_worker(self.sender()):
            return
        result = self.app.update_quota_from_check(quota_info)
        if result["updated"]:
            self._set_user_quota_label(result["user_remaining"], result["user_limit"])
        else:
            self._set_user_quota_label("N/A", "N/A")

        self._set_model_quota_label(result["model_remaining"], result["model_limit"])

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
        if not self.app.is_quota_worker(self.sender()):
            return
        self.quota_label.setText("额度: 错误")
        QMessageBox.critical(self, "错误", get_core_error_message(error_info))

    def on_error(self, error_info):
        if not self.app.is_list_worker(self.sender()):
            return
        self._reset_error_state()
        QMessageBox.critical(self, "错误", get_core_error_message(error_info))

    def copy_model_id(self, model_id):
        clipboard = QApplication.clipboard()
        clipboard.setText(model_id)
        self.status_label.setText(f"已复制: {model_id}")

    def toggle_favorite(self, model_id):
        message = self.app.toggle_favorite(model_id)
        self.status_label.setText(message)
        self.update_model_list()

    def toggle_hide(self, model_id):
        message = self.app.toggle_hidden(model_id)
        self.status_label.setText(message)
        self.update_model_list()

    def on_add_custom_model(self):
        model_id, ok = QInputDialog.getText(
            self, "添加自定义模型", "请输入模型 ID (例: org/model-name):"
        )
        if ok and model_id.strip():
            model_id = model_id.strip()
            result = self.app.add_custom_model(model_id, self.all_models)
            if not result["ok"]:
                QMessageBox.information(self, "提示", result["message"])
                return
            self.status_label.setText(result["message"])
            self.update_model_list()

    def delete_custom_model(self, model_id):
        message = self.app.delete_custom_model(model_id)
        self.status_label.setText(message)
        self.update_model_list()

    def _set_user_quota_label(self, user_remaining, user_limit):
        if user_remaining != "N/A" and user_limit != "N/A":
            self.quota_label.setText(f"用户额度: {user_remaining} / {user_limit}")
        else:
            self.quota_label.setText("用户额度: N/A / N/A")

    def _set_model_quota_label(self, model_remaining, model_limit):
        if model_remaining != "N/A" and model_limit != "N/A":
            self.model_quota_label.setText(
                f"模型额度: {model_remaining} / {model_limit}"
            )
        else:
            self.model_quota_label.setText("模型额度: N/A / N/A")

    def _reset_error_state(self):
        self.all_models = []
        self.model_list.clear()
        self.status_label.setText("无数据/错误状态")
        self._set_user_quota_label("N/A", "N/A")
        self.model_quota_label.setText("模型额度: N/A")
