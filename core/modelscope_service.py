from core.api_key_provider import resolve_api_key
from core.modelscope_client import ModelScopeClient

class ModelScopeService:
    def __init__(self, env_path=None, client=None):
        self.env_path = env_path
        self.client = client or ModelScopeClient()

    def list_models(self, api_key=None):
        key = api_key or resolve_api_key(self.env_path)
        return self.client.list_models(key)

    def check_quota(self, model_id, api_key=None):
        key = api_key or resolve_api_key(self.env_path)
        return self.client.check_quota(model_id, key)
