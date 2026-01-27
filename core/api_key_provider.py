import os
from dotenv import load_dotenv


def resolve_api_key(env_path=None):
    if env_path:
        load_dotenv(env_path, override=True)
    else:
        load_dotenv()
    return os.getenv("API_KEY")
