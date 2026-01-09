import os
import requests
from dotenv import load_dotenv

# 从 .env 文件加载环境变量
load_dotenv()

# 从环境变量获取 API 密钥
api_key = os.getenv("API_KEY")
if not api_key:
    raise ValueError("在 .env 文件中未找到 API_KEY")

base_url = "https://api-inference.modelscope.cn/v1/"

def list_models():
    """使用 requests 直接调用 API 列出模型"""
    print("--- 使用 Requests 调用 ---")
    try:
        headers = {
            "Authorization": f"Bearer {api_key}"
        }
        url = f"{base_url}models"
        
        print(f"正在请求: {url}")
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            resp_json = response.json()
            models = resp_json.get("data", [])
            
            print(f"找到 {len(models)} 个模型:")
            for model in models:
                print(f"- {model['id']}")
        else:
            print(f"请求失败: 状态码 {response.status_code}, 响应: {response.text}")
            
    except Exception as e:
        print(f"Requests 调用失败: {e}")

if __name__ == "__main__":
    list_models()
