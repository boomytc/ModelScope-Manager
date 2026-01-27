import os
from pathlib import Path
from dotenv import load_dotenv, set_key, unset_key

class AccountStore:
    def __init__(self, env_path, default_account_name="默认"):
        self.env_path = Path(env_path)
        self.default_account_name = default_account_name

    def load_accounts(self):
        load_dotenv(self.env_path, override=True)
        accounts = {}

        default_key = os.getenv("API_KEY")
        if default_key:
            accounts[self.default_account_name] = default_key

        for key, value in os.environ.items():
            if key.startswith("API_KEY_"):
                account_name = key[8:]
                accounts[account_name] = value

        return accounts

    def add_account(self, account_name, api_key):
        env_key = self._get_env_key(account_name)
        set_key(str(self.env_path), env_key, api_key)
        os.environ[env_key] = api_key

    def update_account(self, account_name, api_key):
        env_key = self._get_env_key(account_name)
        set_key(str(self.env_path), env_key, api_key)
        os.environ[env_key] = api_key

    def delete_account(self, account_name):
        env_key = self._get_env_key(account_name)
        unset_key(str(self.env_path), env_key)
        if env_key in os.environ:
            del os.environ[env_key]

    def _get_env_key(self, account_name):
        if account_name == self.default_account_name:
            return "API_KEY"
        return f"API_KEY_{account_name}"
