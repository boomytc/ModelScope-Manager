import os
from dotenv import load_dotenv
from core import app_paths


def resolve_api_key(env_path=None):
    if env_path is None:
        env_path = app_paths.get_env_file()
    load_dotenv(env_path, override=True)
    return os.getenv("API_KEY")
