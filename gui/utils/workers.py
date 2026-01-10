import os
import requests
from PySide6.QtCore import QThread, Signal
from dotenv import load_dotenv

class ModelListWorker(QThread):
    finished = Signal(dict)
    error = Signal(str)

    def __init__(self, api_key=None):
        super().__init__()
        self.api_key = api_key

    def run(self):
        try:
            api_key = self.api_key
            if not api_key:
                # 回退到 .env 中的 API_KEY
                load_dotenv()
                api_key = os.getenv("API_KEY")
            
            if not api_key:
                self.error.emit("未找到 API Key")
                return

            base_url = "https://api-inference.modelscope.cn/v1/models"
            headers = {"Authorization": f"Bearer {api_key}"}

            response = requests.get(base_url, headers=headers)
            
            if response.status_code == 200:
                resp_json = response.json()
                models = resp_json.get("data", [])
                
                # 为简化起见，只提取 ID
                model_ids = [model['id'] for model in models if 'id' in model]
                
                # 提取限流信息
                quota_info = {
                    "user_limit": response.headers.get("modelscope-ratelimit-requests-limit", "N/A"),
                    "user_remaining": response.headers.get("modelscope-ratelimit-requests-remaining", "N/A"),
                    "model_limit": response.headers.get("modelscope-ratelimit-model-requests-limit", "N/A"),
                    "model_remaining": response.headers.get("modelscope-ratelimit-model-requests-remaining", "N/A"),
                    "models": model_ids
                }
                
                self.finished.emit(quota_info)
            else:
                self.error.emit(f"请求失败: {response.status_code} - {response.text}")

        except Exception as e:
            self.error.emit(f"Worker 错误: {str(e)}")

class QuotaWorker(QThread):
    finished = Signal(dict)
    error = Signal(str)

    def __init__(self, model_id, api_key=None):
        super().__init__()
        self.model_id = model_id
        self.api_key = api_key

    def run(self):
        try:
            api_key = self.api_key
            if not api_key:
                load_dotenv()
                api_key = os.getenv("API_KEY")
            
            if not api_key:
                self.error.emit("未找到 API Key")
                return

            base_url = "https://api-inference.modelscope.cn/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": self.model_id,
                "messages": [{"role": "user", "content": "Hello"}],
                "max_tokens": 1
            }

            response = requests.post(base_url, headers=headers, json=payload)
            
            quota_info = {
                "user_limit": response.headers.get("modelscope-ratelimit-requests-limit", "N/A"),
                "user_remaining": response.headers.get("modelscope-ratelimit-requests-remaining", "N/A"),
                "model_limit": response.headers.get("modelscope-ratelimit-model-requests-limit", "N/A"),
                "model_remaining": response.headers.get("modelscope-ratelimit-model-requests-remaining", "N/A"),
                "status_code": response.status_code
            }
            
            self.finished.emit(quota_info)

        except Exception as e:
            self.error.emit(f"Quota 检查错误: {str(e)}")
