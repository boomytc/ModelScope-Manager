from core.account_validation import is_valid_account_name

class AccountService:
    def __init__(self, config_manager, account_store, default_account_name="默认"):
        self.config_manager = config_manager
        self.account_store = account_store
        self.default_account_name = default_account_name

    def load_accounts(self):
        accounts = self.account_store.load_accounts()
        active_account = self.config_manager.get_active_account()
        if accounts and (not active_account or active_account not in accounts):
            first_account = list(accounts.keys())[0]
            self.config_manager.set_active_account(first_account)
            self.config_manager.save_config()
        return accounts

    def add_account(self, account_name, api_key, accounts):
        if not is_valid_account_name(account_name):
            return {"ok": False, "code": "invalid_account_name"}

        if account_name == self.default_account_name:
            return {"ok": False, "code": "default_account_name"}

        if account_name in accounts:
            return {"ok": False, "code": "account_exists"}

        self.account_store.add_account(account_name, api_key)
        accounts[account_name] = api_key

        became_active = False
        if len(accounts) == 1:
            self.config_manager.set_active_account(account_name)
            self.config_manager.save_config()
            became_active = True

        return {"ok": True, "code": "ok", "became_active": became_active}

    def update_account(self, account_name, api_key, accounts):
        self.account_store.update_account(account_name, api_key)
        accounts[account_name] = api_key
        return {"ok": True, "code": "ok"}

    def delete_account(self, account_name, accounts):
        was_active = account_name == self.config_manager.get_active_account()
        self.account_store.delete_account(account_name)
        if account_name in accounts:
            del accounts[account_name]

        active_account = self.config_manager.get_active_account()
        if account_name == active_account:
            if accounts:
                new_active = list(accounts.keys())[0]
                self.config_manager.set_active_account(new_active)
            else:
                self.config_manager.set_active_account("")
            self.config_manager.save_config()

        active_account = self.config_manager.get_active_account()
        active_api_key = accounts.get(active_account, "") if active_account else ""

        return {
            "ok": True,
            "code": "ok",
            "was_active": was_active,
            "active_account": active_account,
            "active_api_key": active_api_key,
        }

    def activate_account(self, account_name, accounts):
        self.config_manager.set_active_account(account_name)
        self.config_manager.save_config()
        return {"ok": True, "code": "ok", "active_api_key": accounts.get(account_name, "")}

    def get_active_api_key(self, accounts):
        active_account = self.config_manager.get_active_account()
        return accounts.get(active_account, "")
