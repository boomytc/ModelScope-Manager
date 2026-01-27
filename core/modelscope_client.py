import requests
from core.errors import ApiKeyMissingError, RequestFailedError

REQUEST_TIMEOUT = 15

class ModelScopeClient:
    def __init__(self, request_timeout=REQUEST_TIMEOUT):
        self.request_timeout = request_timeout
        self.models_url = "https://api-inference.modelscope.cn/v1/models"
        self.quota_url = "https://api-inference.modelscope.cn/v1/chat/completions"

    def list_models(self, api_key):
        if not api_key:
            raise ApiKeyMissingError("未找到 API Key")

        headers = {"Authorization": f"Bearer {api_key}"}
        response = requests.get(self.models_url, headers=headers, timeout=self.request_timeout)

        if response.status_code != 200:
            raise RequestFailedError(response.status_code, response.text)

        resp_json = response.json()
        models = resp_json.get("data", [])
        model_ids = [model["id"] for model in models if "id" in model]

        return {
            "user_limit": response.headers.get("modelscope-ratelimit-requests-limit", "N/A"),
            "user_remaining": response.headers.get("modelscope-ratelimit-requests-remaining", "N/A"),
            "model_limit": response.headers.get("modelscope-ratelimit-model-requests-limit", "N/A"),
            "model_remaining": response.headers.get("modelscope-ratelimit-model-requests-remaining", "N/A"),
            "models": model_ids,
        }

    def check_quota(self, model_id, api_key):
        if not api_key:
            raise ApiKeyMissingError("未找到 API Key")

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": model_id,
            "messages": [{"role": "user", "content": "Hello"}],
            "max_tokens": 1,
        }

        response = requests.post(
            self.quota_url,
            headers=headers,
            json=payload,
            timeout=self.request_timeout,
        )

        return {
            "user_limit": response.headers.get("modelscope-ratelimit-requests-limit", "N/A"),
            "user_remaining": response.headers.get("modelscope-ratelimit-requests-remaining", "N/A"),
            "model_limit": response.headers.get("modelscope-ratelimit-model-requests-limit", "N/A"),
            "model_remaining": response.headers.get("modelscope-ratelimit-model-requests-remaining", "N/A"),
            "status_code": response.status_code,
        }
