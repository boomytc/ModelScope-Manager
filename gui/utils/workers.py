import os
import requests
from PySide6.QtCore import QThread, Signal
from dotenv import load_dotenv

class ModelListWorker(QThread):
    finished = Signal(list)
    error = Signal(str)

    def run(self):
        try:
            load_dotenv()
            api_key = os.getenv("API_KEY")
            if not api_key:
                self.error.emit("API_KEY not found in .env file")
                return

            base_url = "https://api-inference.modelscope.cn/v1/models"
            headers = {"Authorization": f"Bearer {api_key}"}

            response = requests.get(base_url, headers=headers)
            
            if response.status_code == 200:
                resp_json = response.json()
                models = resp_json.get("data", [])
                
                # 为简化起见，只提取 ID
                model_ids = [model['id'] for model in models if 'id' in model]
                self.finished.emit(model_ids)
            else:
                self.error.emit(f"Request failed: {response.status_code} - {response.text}")

        except Exception as e:
            self.error.emit(f"Worker Error: {str(e)}")
