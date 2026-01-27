class CoreError(Exception):
    code = "unknown"

    def __init__(self, message=None, context=None):
        super().__init__(message or "")
        self.message = message or ""
        self.context = context or {}


class ApiKeyMissingError(CoreError):
    code = "api_key_missing"


class RequestFailedError(CoreError):
    code = "request_failed"

    def __init__(self, status_code=None, response_text=None):
        context = {
            "status_code": status_code,
            "response_text": response_text,
        }
        super().__init__(message="request_failed", context=context)
