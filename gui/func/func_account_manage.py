import os
from pathlib import Path
from dotenv import load_dotenv, set_key, unset_key
from PySide6.QtWidgets import QMessageBox, QInputDialog, QListWidgetItem, QApplication, QLineEdit
from gui.ui.ui_account_manage import AccountManageUI, AccountItemWidget

from gui.utils import app_paths

class AccountManageTab(AccountManageUI):
    """账号管理标签页功能逻辑。"""
    
    def __init__(self, config_manager, on_account_changed=None, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self.on_account_changed = on_account_changed  # 切换账号时的回调
        self.env_path = app_paths.get_env_file()
        self.accounts = {}  # {account_name: api_key}
        self.default_account_name = "默认"  # 固定的默认账号名称
        
        self.add_btn.clicked.connect(self.on_add_account)
        self.load_accounts()

    def load_accounts(self):
        """从 .env 加载所有账号。"""
        load_dotenv(self.env_path, override=True)
        self.accounts = {}
        
        # 加载默认账号 (无后缀的 API_KEY)
        default_key = os.getenv("API_KEY")
        if default_key:
            self.accounts[self.default_account_name] = default_key
        
        # 加载带后缀的账号 (API_KEY_*)
        for key, value in os.environ.items():
            if key.startswith("API_KEY_"):
                account_name = key[8:]  # 去掉 "API_KEY_" 前缀
                self.accounts[account_name] = value
        
        # 首次启动时自动激活第一个账号
        active_account = self.config_manager.get_active_account()
        if self.accounts and (not active_account or active_account not in self.accounts):
            first_account = list(self.accounts.keys())[0]
            self.config_manager.set_active_account(first_account)
            self.config_manager.save_config()
        
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
        
        # 不允许与默认账号同名
        if name == self.default_account_name:
            QMessageBox.warning(self, "警告", f"不能使用 '{name}' 作为账号名。")
            return
        
        if name in self.accounts:
            QMessageBox.warning(self, "警告", f"账号 '{name}' 已存在。")
            return
        
        api_key, ok = QInputDialog.getText(self, "添加账号", f"请输入 {name} 的 API Key:",
                                           QLineEdit.Password)
        if not ok or not api_key.strip():
            return
        api_key = api_key.strip()
        
        # 写入 .env
        env_key = f"API_KEY_{name}"
        set_key(str(self.env_path), env_key, api_key)
        os.environ[env_key] = api_key
        self.accounts[name] = api_key
        
        # 如果是第一个账号，自动设为当前
        if len(self.accounts) == 1:
            self.config_manager.set_active_account(name)
            self.config_manager.save_config()
            if self.on_account_changed:
                self.on_account_changed(name, api_key)
        
        self.update_account_list()
        self.status_label.setText(f"已添加: {name}")

    def on_edit_account(self, account_name):
        """编辑账号。"""
        current_key = self.accounts.get(account_name, "")
        new_key, ok = QInputDialog.getText(self, "编辑账号", 
                                          f"请输入 {account_name} 的新 API Key:",
                                          QLineEdit.Password, current_key)
        if not ok or not new_key.strip():
            return
        new_key = new_key.strip()
        
        # 更新 .env (默认账号使用 API_KEY，其他使用 API_KEY_*)
        if account_name == self.default_account_name:
            env_key = "API_KEY"
        else:
            env_key = f"API_KEY_{account_name}"
        set_key(str(self.env_path), env_key, new_key)
        os.environ[env_key] = new_key
        self.accounts[account_name] = new_key
        
        self.update_account_list()
        self.status_label.setText(f"已更新: {account_name}")
        
        # 如果是当前账号，通知刷新
        if account_name == self.config_manager.get_active_account():
            if self.on_account_changed:
                self.on_account_changed(account_name, new_key)

    def on_delete_account(self, account_name):
        """删除账号。"""
        reply = QMessageBox.question(self, "确认删除", 
                                    f"确定要删除账号 '{account_name}' 吗？",
                                    QMessageBox.Yes | QMessageBox.No)
        if reply != QMessageBox.Yes:
            return
        
        # 从 .env 删除
        env_key = f"API_KEY_{account_name}"
        unset_key(str(self.env_path), env_key)
        if env_key in os.environ:
            del os.environ[env_key]
        del self.accounts[account_name]
        
        # 如果删除的是当前账号，清空或切换
        if account_name == self.config_manager.get_active_account():
            if self.accounts:
                new_active = list(self.accounts.keys())[0]
                self.config_manager.set_active_account(new_active)
                if self.on_account_changed:
                    self.on_account_changed(new_active, self.accounts[new_active])
            else:
                self.config_manager.set_active_account("")
            self.config_manager.save_config()
        
        self.update_account_list()
        self.status_label.setText(f"已删除: {account_name}")

    def on_activate_account(self, account_name):
        """设置当前账号。"""
        self.config_manager.set_active_account(account_name)
        self.config_manager.save_config()
        self.update_account_list()
        self.status_label.setText(f"已切换到: {account_name}")
        
        if self.on_account_changed:
            self.on_account_changed(account_name, self.accounts[account_name])

    def get_active_api_key(self):
        """获取当前激活账号的 API Key。"""
        active_account = self.config_manager.get_active_account()
        return self.accounts.get(active_account, "")

    def on_copy_api_key(self, api_key):
        """复制 API Key 到剪贴板。"""
        clipboard = QApplication.clipboard()
        clipboard.setText(api_key)
        self.status_label.setText("已复制 API Key")
