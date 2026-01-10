import sys
import os
from pathlib import Path

def get_app_root():
    """获取应用根目录。
    打包后: sys._MEIPASS
    源码运行: 项目根目录 (gui 目录的上级)
    """
    if getattr(sys, 'frozen', False):
        # PyInstaller 打包后的临时目录
        return Path(sys._MEIPASS)
    else:
        # 源码运行，gui/utils/app_paths.py -> utils -> gui -> root
        return Path(__file__).resolve().parent.parent.parent

def get_icon_path(icon_name):
    """获取图标文件的绝对路径。"""
    root = get_app_root()
    
    if getattr(sys, 'frozen', False):
        # 打包时，资源通常会被配置在根目录的 icon 文件夹下
        # 或者直接在根目录，取决于 spec 配置。这里假设映射到了 icon 目录
        return str(root / "icon" / icon_name)
    else:
        # 源码运行时: gui/icon/
        return str(root / "gui" / "icon" / icon_name)

def get_data_path():
    """获取用户数据存储目录 (跨平台)。
    macOS/Linux: ~/.modelscope_manager/
    Windows: C:/Users/Name/.modelscope_manager/
    """
    home = Path.home()
    data_dir = home / ".modelscope_manager"
    
    # 确保目录存在
    if not data_dir.exists():
        try:
            data_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            print(f"Error creating data directory: {e}")
            
    return data_dir

def get_config_file():
    """获取 config.toml 路径。"""
    return get_data_path() / "config.toml"

def get_env_file():
    """获取 .env 文件路径。"""
    return get_data_path() / ".env"
