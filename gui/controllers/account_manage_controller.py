from PySide6.QtWidgets import QMessageBox, QInputDialog, QListWidgetItem, QApplication, QLineEdit
from gui.ui.ui_account_manage import AccountManageUI, AccountItemWidget
from gui.ui.messages import get_account_error_message

from core import app_paths
from core.account_store import AccountStore
from core.account_service import AccountService

class AccountManageTab(AccountManageUI):
    """账号管理标签页功能逻辑。"""

    def __init__(self, config_manager, on_account_changed=None, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self.on_account_changed = on_account_changed  # 切换账号时的回调
        self.env_path = app_paths.get_env_file()
        self.accounts = {}  # {account_name: api_key}
        self.default_account_name = "默认"  # 固定的默认账号名称
        self.account_store = AccountStore(self.env_path, self.default_account_name)
        self.account_service = AccountService(
            self.config_manager,
            self.account_store,
            self.default_account_name,
        )

        self.add_btn.clicked.connect(self.on_add_account)
        self.load_accounts()

    def load_accounts(self):
        """从 .env 加载所有账号。"""
        self.accounts = self.account_service.load_accounts()

        self.update_account_list()

    def update_account_list(self):
        """更新账号列表显示。"""
        active_account = self.config_manager.get_active_account()
        self.account_list.clear()

        for account_name, api_key in self.accounts.items():
            is_active = (account_name == active_account)
            is_default = (account_name == self.default_account_name)
            item = QListWidgetItem(self.account_list)
            widget = AccountItemWidget(account_name, api_key, is_active, is_default)
            widget.copy_clicked.connect(self.on_copy_api_key)
            widget.edit_clicked.connect(self.on_edit_account)
            widget.delete_clicked.connect(self.on_delete_account)
            widget.activate_clicked.connect(self.on_activate_account)
            item.setSizeHint(widget.sizeHint())
            self.account_list.addItem(item)
            self.account_list.setItemWidget(item, widget)

        if not self.accounts:
            self.status_label.setText("暂无账号，点击右上角 + 添加")
        else:
            self.status_label.setText(f"共 {len(self.accounts)} 个账号")

    def on_add_account(self):
        """添加新账号。"""
        name, ok = QInputDialog.getText(self, "添加账号", "请输入账号名称:")
        if not ok or not name.strip():
            return
        name = name.strip()

        api_key, ok = QInputDialog.getText(
            self, "添加账号", f"请输入 {name} 的 API Key:", QLineEdit.Password
        )
        if not ok or not api_key.strip():
            return
        api_key = api_key.strip()

        result = self.account_service.add_account(name, api_key, self.accounts)
        if not result["ok"]:
            QMessageBox.warning(
                self,
                "警告",
                get_account_error_message(result.get("code"), self.default_account_name),
            )
            return

        if result.get("became_active") and self.on_account_changed:
            self.on_account_changed(name, api_key)

        self.update_account_list()
        self.status_label.setText(f"已添加: {name}")

    def on_edit_account(self, account_name):
        """编辑账号。"""
        current_key = self.accounts.get(account_name, "")
        new_key, ok = QInputDialog.getText(
            self,
            "编辑账号",
            f"请输入 {account_name} 的新 API Key:",
            QLineEdit.Password,
            current_key,
        )
        if not ok or not new_key.strip():
            return
        new_key = new_key.strip()

        result = self.account_service.update_account(account_name, new_key, self.accounts)

        self.update_account_list()
        self.status_label.setText(f"已更新: {account_name}")

        # 如果是当前账号，通知刷新
        if account_name == self.config_manager.get_active_account():
            if self.on_account_changed:
                self.on_account_changed(account_name, new_key)

    def on_delete_account(self, account_name):
        """删除账号。"""
        reply = QMessageBox.question(
            self,
            "确认删除",
            f"确定要删除账号 '{account_name}' 吗？",
            QMessageBox.Yes | QMessageBox.No,
        )
        if reply != QMessageBox.Yes:
            return

        result = self.account_service.delete_account(account_name, self.accounts)

        # 如果删除的是当前账号，清空或切换
        if result.get("was_active"):
            if self.on_account_changed:
                self.on_account_changed(
                    result.get("active_account", ""),
                    result.get("active_api_key", ""),
                )

        self.update_account_list()
        self.status_label.setText(f"已删除: {account_name}")

    def on_activate_account(self, account_name):
        """设置当前账号。"""
        result = self.account_service.activate_account(account_name, self.accounts)
        self.update_account_list()
        self.status_label.setText(f"已切换到: {account_name}")

        if self.on_account_changed:
            self.on_account_changed(account_name, result.get("active_api_key", ""))

    def get_active_api_key(self):
        """获取当前激活账号的 API Key。"""
        return self.account_service.get_active_api_key(self.accounts)

    def on_copy_api_key(self, api_key):
        """复制 API Key 到剪贴板。"""
        clipboard = QApplication.clipboard()
        clipboard.setText(api_key)
        self.status_label.setText("已复制 API Key")

