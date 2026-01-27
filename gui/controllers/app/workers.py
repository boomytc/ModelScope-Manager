from PySide6.QtCore import QThread, Signal
from core.modelscope_service import ModelScopeService
from core.errors import CoreError
from core import app_paths

class ModelListWorker(QThread):
    finished = Signal(dict)
    error = Signal(dict)

    def __init__(self, api_key=None):
        super().__init__()
        self.api_key = api_key
        self.env_path = app_paths.get_env_file()
        self.service = ModelScopeService(self.env_path)

    def run(self):
        try:
            quota_info = self.service.list_models(self.api_key)
            self.finished.emit(quota_info)

        except CoreError as e:
            self.error.emit({"code": e.code, "context": e.context})
        except Exception as e:
            self.error.emit({"code": "unknown", "context": {"message": str(e)}})


class QuotaWorker(QThread):
    finished = Signal(dict)
    error = Signal(dict)

    def __init__(self, model_id, api_key=None):
        super().__init__()
        self.model_id = model_id
        self.api_key = api_key
        self.env_path = app_paths.get_env_file()
        self.service = ModelScopeService(self.env_path)

    def run(self):
        try:
            quota_info = self.service.check_quota(self.model_id, self.api_key)
            self.finished.emit(quota_info)

        except CoreError as e:
            self.error.emit({"code": e.code, "context": e.context})
        except Exception as e:
            self.error.emit({"code": "unknown", "context": {"message": str(e)}})
