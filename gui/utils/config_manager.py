import logging
import toml
from pathlib import Path

class ConfigManager:
    def __init__(self, config_path=None):
        if config_path is None:
            # 默认配置文件位于 gui/config.toml
            gui_dir = Path(__file__).resolve().parent.parent
            config_path = gui_dir / "config.toml"
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
