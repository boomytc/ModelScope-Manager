from core.account_store import AccountStore
from core.account_service import AccountService

class AccountManageApp:
    def __init__(self, config_manager, env_path, default_account_name="默认"):
        self.config_manager = config_manager
        self.default_account_name = default_account_name
        self.account_store = AccountStore(env_path, default_account_name)
        self.account_service = AccountService(
            self.config_manager,
            self.account_store,
            self.default_account_name,
        )

    def load_accounts(self):
        return self.account_service.load_accounts()

    def add_account(self, account_name, api_key, accounts):
        return self.account_service.add_account(account_name, api_key, accounts)

    def update_account(self, account_name, api_key, accounts):
        return self.account_service.update_account(account_name, api_key, accounts)

    def delete_account(self, account_name, accounts):
        return self.account_service.delete_account(account_name, accounts)

    def activate_account(self, account_name, accounts):
        return self.account_service.activate_account(account_name, accounts)

    def get_active_api_key(self, accounts):
        return self.account_service.get_active_api_key(accounts)

    def get_active_account(self):
        return self.config_manager.get_active_account()
