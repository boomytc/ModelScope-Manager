from core.config_manager import ConfigManager
from core import app_paths

class MainWindowApp:
    def __init__(self):
        self.config_manager = ConfigManager(app_paths.get_config_file())
        self.current_api_key = None

    def get_config_manager(self):
        return self.config_manager

    def get_current_api_key(self):
        return self.current_api_key

    def set_current_api_key(self, api_key):
        self.current_api_key = api_key

    def get_window_geometry(self):
        return self.config_manager.get_window_geometry()

    def set_window_geometry(self, x, y, width, height):
        self.config_manager.set_window_geometry(x, y, width, height)

    def save_config(self):
        self.config_manager.save_config()
