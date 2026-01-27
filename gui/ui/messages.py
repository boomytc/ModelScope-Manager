def get_core_error_message(error_info):
    code = error_info.get("code")
    context = error_info.get("context", {})
    if code == "api_key_missing":
        return "未找到 API Key"
    if code == "request_failed":
        status_code = context.get("status_code", "Unknown")
        return f"请求失败: {status_code}"
    return context.get("message", "未知错误")


def get_account_error_message(error_code, default_account_name):
    if error_code == "invalid_account_name":
        return "账号名仅允许字母、数字、下划线和短横线。"
    if error_code == "default_account_name":
        return f"不能使用 '{default_account_name}' 作为账号名。"
    if error_code == "account_exists":
        return "账号已存在。"
    return "未知错误"
