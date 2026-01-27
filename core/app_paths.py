from pathlib import Path


def get_app_root():
    """获取应用根目录。源码运行: 项目根目录 (gui 目录的上级)"""
    # 源码运行，core/app_paths.py -> core -> root
    return Path(__file__).resolve().parent.parent


def get_data_path():
    """获取用户数据存储目录 (项目内)。"""
    root = get_app_root()
    data_dir = root / ".modelscope_manager"

    if not data_dir.exists():
        try:
            data_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            print(f"Error creating data directory: {e}")

    return data_dir


def get_config_file():
    """获取 config.toml 路径。"""
    return get_app_root() / "gui" / "config.toml"


def get_env_file():
    """获取 .env 文件路径。"""
    return get_app_root() / ".env"
