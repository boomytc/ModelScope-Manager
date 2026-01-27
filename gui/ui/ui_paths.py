from core.app_paths import get_app_root


def get_icon_path(icon_name):
    """获取图标文件的绝对路径。"""
    root = get_app_root()
    return str(root / "gui" / "icon" / icon_name)
