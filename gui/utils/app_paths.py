from pathlib import Path

def get_app_root():
    """获取应用根目录。
    源码运行: 项目根目录 (gui 目录的上级)
    """
    # 源码运行，gui/utils/app_paths.py -> utils -> gui -> root
    return Path(__file__).resolve().parent.parent.parent

def get_icon_path(icon_name):
    """获取图标文件的绝对路径。"""
    root = get_app_root()
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
