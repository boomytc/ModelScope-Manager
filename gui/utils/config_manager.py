import logging
import toml
from pathlib import Path
from gui.utils import app_paths

class ConfigManager:
    def __init__(self, config_path=None):
        if config_path is None:
            # 默认配置路径 (跨平台用户数据目录)
            config_path = app_paths.get_config_file()
        self.config_path = Path(config_path)
        self.config = {}
        self.load_config()

    def load_config(self):
        """从 TOML 文件加载配置。"""
        if self.config_path.exists():
            try:
                self.config = toml.load(self.config_path)
            except Exception as e:
                logging.error(f"Failed to load config: {e}")
                self.config = {}
        else:
            logging.warning(f"Config file not found at {self.config_path}")
            self.config = {}

    def save_config(self):
        """将当前配置保存到 TOML 文件。"""
        try:
            # 确保目录存在
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, "w") as f:
                toml.dump(self.config, f)
        except Exception as e:
            logging.error(f"Failed to save config: {e}")

    def get_window_geometry(self):
        """从配置中获取窗口几何信息 (x, y, width, height)。"""
        window_config = self.config.get("window", {})
        return (
            window_config.get("x", 100),
            window_config.get("y", 100),
            window_config.get("width", 800),
            window_config.get("height", 600)
        )

    def set_window_geometry(self, x, y, width, height):
        """更新配置中的窗口几何信息。"""
        if "window" not in self.config:
            self.config["window"] = {}
        
        self.config["window"]["x"] = x
        self.config["window"]["y"] = y
        self.config["window"]["width"] = width
        self.config["window"]["height"] = height

    def get_favorites(self):
        """获取收藏的模型列表。"""
        return self.config.get("favorites", [])

    def add_favorite(self, model_id):
        """添加模型到收藏。"""
        if "favorites" not in self.config:
            self.config["favorites"] = []
        if model_id not in self.config["favorites"]:
            self.config["favorites"].append(model_id)

    def remove_favorite(self, model_id):
        """从收藏中移除模型。"""
        if "favorites" in self.config and model_id in self.config["favorites"]:
            self.config["favorites"].remove(model_id)

    def is_favorite(self, model_id):
        """检查模型是否已收藏。"""
        return model_id in self.config.get("favorites", [])

    def get_custom_models(self):
        """获取自定义模型列表。"""
        return self.config.get("custom_models", [])

    def add_custom_model(self, model_id):
        """添加自定义模型。"""
        if "custom_models" not in self.config:
            self.config["custom_models"] = []
        if model_id not in self.config["custom_models"]:
            self.config["custom_models"].append(model_id)

    def remove_custom_model(self, model_id):
        """移除自定义模型。"""
        if "custom_models" in self.config and model_id in self.config["custom_models"]:
            self.config["custom_models"].remove(model_id)

    def is_custom_model(self, model_id):
        """检查是否为自定义模型。"""
        return model_id in self.config.get("custom_models", [])

    def get_active_account(self):
        """获取当前激活的账号名。"""
        return self.config.get("active_account", "")

    def set_active_account(self, account_name):
        """设置当前激活的账号名。"""
        self.config["active_account"] = account_name

    def get_last_quota(self):
        """获取最后一次保存的额度信息 (基于当前账号)。"""
        account = self.get_active_account()
        if not account:
            return {"user_remaining": "N/A", "user_limit": "N/A"}

        quotas = self.config.get("quotas", {})
        account_quota = quotas.get(account, {})
        return {
            "user_remaining": account_quota.get("user_remaining", "N/A"),
            "user_limit": account_quota.get("user_limit", "N/A")
        }

    def set_last_quota(self, user_remaining, user_limit):
        """保存额度信息 (基于当前账号)。"""
        account = self.get_active_account()
        if not account:
            return

        if "quotas" not in self.config:
            self.config["quotas"] = {}
        
        if account not in self.config["quotas"]:
            self.config["quotas"][account] = {}

        self.config["quotas"][account]["user_remaining"] = str(user_remaining)
        self.config["quotas"][account]["user_limit"] = str(user_limit)
